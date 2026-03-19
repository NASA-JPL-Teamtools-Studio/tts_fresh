import csv
import enum
import pathlib
import arrow
import datetime as dt
from dataclasses import dataclass
from functools import reduce
from tts_fresh.flightrules.fr_base import FRBase, FRCheckInfo, FRCriticality, FRResult, FRState
from tts_fresh.utils.step_utils import get_steps
from tts_fresh.utils.modal_bool import ModalBool
from tts_fresh.seqdict import SeqDict, SeqStep, SeqArgType, SeqStepType, SeqTimeType
from tts_fresh.mission_config import get_control_flow_directives


class CmdTimingRuleType(enum.Enum):
    """
    Defines the various categories of timing relationships that can exist between commands. 
    It identifies whether a rule pertains to overlapping executions, mandatory wait times, or sequential execution orders.
    These types determine the underlying logic used by the validation engine to identify command pairs.
    """
    OVERLAP = 1
    WAIT = 2 # This param must wait some time after that param
    FOLLOWS = 3 # This param must follow after that param
    FOLLOWED_BY = 4 # This param must be followed by that param

class CmdTimingRule:
    """
    Encapsulates the definition of a single timing-based flight rule, typically loaded from a configuration file. 
    It stores the criteria for identifying trigger commands and their related counterparts, as well as the allowed duration between them.
    The class provides utility methods to determine if specific sequence commands qualify for the rule's application.
    """
    fr_id: str
    fr_version: str
    fr_description: str
    fr_criticality: FRCriticality
    alert_level: FRState
    cmd_stem: str
    cmd_args: dict # May be None
    rule_type: CmdTimingRuleType
    duration_range: "TimeRange"
    rel_cmd: str
    rel_args: dict # May be None
    message: str

    def __init__(self, args: dict):
        """
        Initializes a new timing rule by parsing raw data from a configuration CSV file. 
        It handles the conversion of string-based parameters into structured types like timedelta ranges and criticality enums.
        This constructor is typically called while reading rule definitions from a CSV file.

        :param args: A dictionary representing a row from a rule configuration file.
        :type args: dict
        """
        self.fr_id = args['FR_ID']
        self.fr_version = args['FR_Version']
        self.fr_description = args['Message']
        crit_letter = args['FR_ID'].split('-')[1]
        self.fr_criticality=FRCriticality.from_letter(crit_letter)
        self.alert_level = FRState[args['Alert_Level']]
        self.cmd_stem = args['Command_Stem']
        self.cmd_args = self.__make_arg_map(args['Arg_Names'], args['Arg_Values'])
        self.rule_type = CmdTimingRuleType[args['Arg_Check_Type'].upper()]
        min_str = args['Duration_Min']
        max_str = args['Duration_Max']
        self.duration_range = TimeRange(
            mn=dt.timedelta(seconds=int(min_str)) if min_str else dt.timedelta(),
            mx=dt.timedelta(seconds=int(max_str)) if max_str else None)
        self.rel_cmd = args['Rel_Command']
        self.rel_args = self.__make_arg_map(args['Rel_Arg_Names'], args['Rel_Arg_Values'])
        self.message = args['Message']

    @staticmethod
    def __make_arg_map(arg_str: str, value_str: str) -> dict:
        """
        Parses semicolon-delimited strings of argument names and values into a structured mapping.
        It supports list-based values formatted with brackets and pipes to allow rules to match against multiple possible argument values.
        This internal helper ensures that complex command criteria are correctly translated from text-based rule files.

        :param arg_str: A string containing semicolon-separated argument names.
        :type arg_str: str
        :param value_str: A string containing semicolon-separated argument values or value lists.
        :type value_str: str
        :return: A dictionary mapping argument names to their required values or lists of values.
        :rtype: dict
        :raises SyntaxError: If the number of arguments and values do not match or if list formatting is invalid.
        """
        if arg_str:
            arg_dict = {}
            arg_str_list = [] if arg_str is None else arg_str.split(';')
            val_str_list = [] if value_str is None else value_str.split(';')
            num_args = len(arg_str_list)
            num_vals = len(val_str_list)
            if num_args != num_vals:
                err = f"Cannot define more values <{num_vals}> than arguments <{num_args}>"
                raise SyntaxError(err)
            for arg, val in zip(arg_str_list, val_str_list):
                arg = arg.strip()
                if '[' in val or ']' in val:
                    if val.startswith('[') and val.endswith(']'):
                        arg_dict[arg] = [v.strip() for v in val[1:-1].split('|')]
                    else:
                        raise SyntaxError("List must be of the format: [ 1 | 2 | ... | n ]")
                else:
                    arg_dict[arg] = val
            return arg_dict
        return dict()

    def cmd_args_qualify(self, exp_args: dict, args: list) -> ModalBool:
        """
        Check if the provided command arguments match those needed for the rule to apply.
        It evaluates the actual values used by the command against the expected criteria defined in the rule.
        The function returns a ModalBool to account for uncertainty if symbolic arguments are encountered.

        :param exp_args: A dictionary of expected argument names and values.
        :type exp_args: dict
        :param args: The list of actual argument objects from a sequence command.
        :type args: list
        :return: YES if arguments match, NO if they do not, and MAYBE if the result is indeterminate.
        :rtype: ModalBool
        """
        answer = ModalBool.YES
        for name, exp_val in exp_args.items():
            try:
                arg = None
                for a in args:
                    if a.name == name:
                        arg = a
                if arg is not None:
                    if arg.argtype == SeqArgType.SYMBOL:
                        # If the argument is symbolic, we can't know for certain if it qualifies.
                        answer &= ModalBool.MAYBE
                    else:
                        val = str(arg.value)
                        # Otherwise, it qualifies if it's one of the listed values,
                        # if the expected value is actually to match a paired command (so skip this check),
                        # or if it exactly matches the expected value.
                        if isinstance(exp_val, list):
                            answer &= val in exp_val
                        else:
                            answer &= exp_val.startswith('=') or val == exp_val
                # If the commands we're checking aren't well-formed, flag for review.
                else:
                    answer &= ModalBool.MAYBE
            except (IndexError, KeyError):
                answer &= ModalBool.MAYBE
        return answer

    def is_cmd(self, cmd: SeqStep) -> ModalBool:
        """
        Determines if a given command is the primary trigger for this timing rule.
        It checks both the command stem and the associated arguments to see if they meet the rule's criteria.
        For overlap rules, it also considers whether the command could be the related command in the pair.

        :param cmd: The sequence command step to evaluate.
        :type cmd: SeqStep
        :return: A ModalBool describing the certainty of the command matching the rule.
        :rtype: ModalBool
        """
        return self.__is_cmd(cmd) | ((self.rule_type == CmdTimingRuleType.OVERLAP) & self.__is_rel(cmd))

    def is_rel(self, cmd: SeqStep) -> ModalBool:
        """
        Determines if a given command is relevant to the rule as a related (secondary) command.
        Similar to the primary command check, it validates the stem and arguments against defined criteria.
        For overlap rules, it also considers whether the command could be the primary trigger in the pair.

        :param cmd: The sequence command step to evaluate.
        :type cmd: SeqStep
        :return: A ModalBool describing the certainty of the match.
        :rtype: ModalBool
        """
        return self.__is_rel(cmd) | ((self.rule_type == CmdTimingRuleType.OVERLAP) & self.__is_cmd(cmd))

    def __is_cmd(self, cmd: SeqStep) -> ModalBool:
        """
        Internal helper to check if a command matches the primary stem and argument requirements.

        :param cmd: The command object.
        :type cmd: SeqStep
        :return: ModalBool status of the match.
        :rtype: ModalBool
        """
        return (cmd.stem == self.cmd_stem) & self.cmd_args_qualify(self.cmd_args, cmd.args)

    def __is_rel(self, cmd: SeqStep) -> ModalBool:
        """
        Internal helper to check if a command matches the related stem and argument requirements.

        :param cmd: The command object.
        :type cmd: SeqStep
        :return: ModalBool status of the match.
        :rtype: ModalBool
        """
        return (cmd.stem == self.rel_cmd) & self.cmd_args_qualify(self.rel_args, cmd.args)

    def __arg_values_match(self, a: list, b: list, exp_a: dict) -> bool:
        """
        Validates that specific arguments between two commands match as required by the rule.
        This is used for rules where a related command's argument must equal a primary command's argument (indicated by the '=' prefix).
        It returns a ModalBool to reflect any uncertainty caused by symbolic or missing data.

        :param a: The first command object in the pair.
        :param b: The second command object in the pair.
        :param exp_a: The expected argument mapping for the first command.
        :type exp_a: dict
        :return: ModalBool describing the success of the cross-command match.
        :rtype: ModalBool
        """
        answer = ModalBool.YES
        for exp_a_name, exp_val in exp_a.items():
            if isinstance(exp_val, str) and exp_val.startswith('='):
                try:
                    exp_b_name = exp_a_name if exp_val == '=' else exp_val[1:]
                    a_check_arg = None
                    b_check_arg = None
                    for arg in a.args:
                        if arg.name == exp_a_name:
                            a_check_arg = arg
                            break
                    for arg in b.args:
                        if arg.name == exp_b_name:
                            b_check_arg = arg
                            break
                    # If the commands we're checking aren't well-formed, flag for review.
                    if a_check_arg == None or b_check_arg == None:
                        answer &= ModalBool.MAYBE
                    # If either value is symbolic, we can't know if they match
                    elif a_check_arg.argtype == SeqArgType.SYMBOL or b_check_arg.argtype == SeqArgType.SYMBOL:
                        answer &= ModalBool.MAYBE
                    # Otherwise, accumulate this check into the overall answer
                    else:
                        answer &= b_check_arg.value == a_check_arg.value
                # If the commands we're checking aren't well-formed, flag for review.
                except (IndexError, KeyError):
                    answer &= ModalBool.MAYBE
        return answer

    def is_pair(self, cmd, rel) -> ModalBool:
        """
        Determines if two commands form a valid pair that should be checked against this timing rule.
        It verifies that both commands match their respective definitions and that any cross-command argument requirements are met.
        The function handles the symmetric nature of overlap rules by checking both potential orderings.

        :param cmd: The primary command object.
        :param rel: The related command object.
        :return: A ModalBool describing the certainty of the pair matching the rule definition.
        :rtype: ModalBool
        """
        if self.rule_type == CmdTimingRuleType.OVERLAP:
            return (self.__is_cmd(cmd) & self.__is_rel(rel) & self.__check_pair(cmd, rel)) | \
                (self.__is_rel(cmd) & self.__is_cmd(rel) & self.__check_pair(rel, cmd))
        else:
            return self.__check_pair(cmd, rel)

    def __check_pair(self, cmd, rel):
        """
        Internal helper to perform the final argument value matching for a command pair.

        :param cmd: The primary command object.
        :param rel: The related command object.
        :return: ModalBool indicating match success.
        :rtype: ModalBool
        """
        return self.__arg_values_match(cmd, rel, self.cmd_args) & \
            self.__arg_values_match(rel, cmd, self.rel_args)


@dataclass
class TimeRange:
    """
    Represents an interval of relative time, defined by optional minimum and maximum durations.
    This class supports arithmetic and logical operations to facilitate the calculation and intersection of time constraints within a sequence.
    It is used to verify whether the actual duration between commands falls within the bounds allowed by a flight rule.
    """
    mn: dt.timedelta = None
    mx: dt.timedelta = None

    def __add__(self, other) -> "TimeRange":
        """
        Adds a timedelta or another TimeRange to the current range.
        This operation effectively shifts or expands the interval based on additional timing offsets or constraints.

        :param other: The time offset or range to add.
        :return: A new TimeRange representing the combined interval.
        :rtype: TimeRange
        """
        if isinstance(other, dt.timedelta):
            return TimeRange(
                mn=(self.mn + other if self.mn is not None else None),
                mx=(self.mx + other if self.mx is not None else None))
        elif isinstance(other, TimeRange):
            return TimeRange(
                mn=(self.mn + other.mn if self.mn is not None and other.mn is not None else None),
                mx=(self.mx + other.mx if self.mx is not None and other.mx is not None else None))
        return NotImplemented


    def __neg__(self) -> "TimeRange":
        """
        Returns the negation of the current TimeRange.
        This is useful for reversing the direction of a time offset while maintaining the correct min/max logic.

        :return: A new negated TimeRange.
        :rtype: TimeRange
        """
        return TimeRange(
            mn=(-self.mx if self.mx is not None else None),
            mx=(-self.mn if self.mn is not None else None))


    def __sub__(self, other) -> "TimeRange":
        """
        Subtracts another TimeRange from the current one.
        This is implemented as addition with the negation of the other range.

        :param other: The range to subtract.
        :return: The resulting TimeRange.
        :rtype: TimeRange
        """
        return self + (-other)


    def __and__(self, other: "TimeRange") -> "TimeRange":
        """
        Computes the intersection of this TimeRange and another.
        The resulting range covers the period shared by both intervals, helping to resolve multiple timing constraints.

        :param other: The other TimeRange to intersect with.
        :type other: TimeRange
        :return: A new TimeRange representing the overlapping period.
        :rtype: TimeRange
        """
        if isinstance(other, TimeRange):
            return TimeRange(
                mn=max((t for t in [self.mn, other.mn] if t is not None), default=None),
                mx=min((t for t in [self.mx, other.mx] if t is not None), default=None))
        return NotImplemented

    
    def __bool__(self):
        """
        Determines if the TimeRange represents a valid, non-empty interval.
        A range is considered valid if its minimum value is less than or equal to its maximum value, or if either bound is infinite.

        :return: True if the range is valid, False otherwise.
        """
        return self.mn is None or self.mx is None or self.mn <= self.mx


    def contains(self, other: "TimeRange") -> ModalBool:
        """
        Checks if the current TimeRange logically contains another TimeRange.
        It returns YES if the other range is a complete subset, NO if they are disjoint, and MAYBE if they only partially overlap.

        :param other: The other TimeRange to check.
        :type other: TimeRange
        :return: A ModalBool describing the containment status.
        :rtype: ModalBool
        """
        if isinstance(other, TimeRange):
            intersection = self & other
            if not intersection:
                return ModalBool.NO
            elif intersection == other:
                return ModalBool.YES
            else:
                return ModalBool.MAYBE
        return NotImplemented


    def __eq__(self, other):
        """
        Compares two TimeRange objects for equality.

        :param other: The other range to compare against.
        :return: True if both ranges have identical bounds.
        """
        return self is other or (isinstance(other, TimeRange) and self.mn == other.mn and self.mx == other.mx)


    def __str__(self):
        """
        Returns a human-readable string representation of the TimeRange.
        It handles infinite bounds by displaying '-inf.' or 'inf.' as appropriate.

        :return: A formatted string describing the time interval.
        :rtype: str
        """
        def _time_fmt(t, none_str):
            if t is None:
                return none_str
            elif t < dt.timedelta():
                return '-' + str(abs(t))
            else:
                return str(t)

        if self.mn == self.mx:
            if self.mn is None:
                return "[-inf., inf.]"
            return _time_fmt(self.mn, None)
        else:
            return f'[{_time_fmt(self.mn, "-inf.")}, {_time_fmt(self.mx, "inf.")}]'


@dataclass
class AnchoredTimeRange:
    """
    Pairs a relative TimeRange with a specific anchor, such as an absolute timestamp or a logical sequence event. 
    This structure allows for comparing time offsets that are calculated from different points of reference.
    It is a key component in Resolving the dispatch timing of commands relative to sequence start or mission epochs.
    """
    anchor: object
    time_range: TimeRange

    def __add__(self, other: dt.timedelta) -> "AnchoredTimeRange":
        """
        Adds a timedelta offset to the anchored range.
        This shifts the relative window while maintaining the same anchor point.

        :param other: The time offset to add.
        :type other: dt.timedelta or TimeRange
        :return: A new AnchoredTimeRange with the updated window.
        :rtype: AnchoredTimeRange
        """
        if isinstance(other, dt.timedelta) or isinstance(other, TimeRange):
            return AnchoredTimeRange(self.anchor, self.time_range + other)
        return NotImplemented


    def __sub__(self, other: "AnchoredTimeRange") -> TimeRange:
        """
        Computes the time difference between this AnchoredTimeRange and another.
        It resolves the relative delta between different anchors, returning a range that covers all possible durations between the two.
        If the anchors are incomparable, it returns an empty TimeRange signifying total uncertainty.

        :param other: The other AnchoredTimeRange to subtract.
        :type other: AnchoredTimeRange
        :return: The relative time duration between the two anchored ranges.
        :rtype: TimeRange
        """
        if isinstance(other, AnchoredTimeRange):
            if isinstance(self.anchor, arrow.Arrow) and isinstance(other.anchor, arrow.Arrow):
                anchor_delta = self.anchor - other.anchor
                range_delta = self.time_range - other.time_range
                return range_delta + anchor_delta
            elif self.anchor == other.anchor:
                return self.time_range - other.time_range
            else:
                return TimeRange()
        return NotImplemented


    def __and__(self, other: "AnchoredTimeRange") -> "AnchoredTimeRange":
        """
        Calculates the intersection of two AnchoredTimeRanges.
        If the anchors are absolute timestamps, one is re-homed to the other's anchor before performing the intersection.
        This ensures that multiple timing constraints on the same event are correctly merged.

        :param other: The other AnchoredTimeRange to intersect with.
        :type other: AnchoredTimeRange
        :return: A new merged AnchoredTimeRange.
        :rtype: AnchoredTimeRange
        """
        if isinstance(other, AnchoredTimeRange):
            if isinstance(self.anchor, arrow.Arrow) and isinstance(other.anchor, arrow.Arrow):
                # Re-home other absolute time range to this anchor, then intersect
                shift_other_range = other.time_range + (other.anchor - self.anchor)
                return AnchoredTimeRange(self.anchor, self.time_range & shift_other_range)
            elif self.anchor == other.anchor:
                return AnchoredTimeRange(self.anchor, self.time_range & other.time_range)
            else:
                return AnchoredTimeRange(self.anchor, TimeRange())
        return NotImplemented


    def is_comparable(self, other: "AnchoredTimeRange") -> bool:
        """
        Determines if two anchored ranges can be mathematically compared.
        Comparison is possible if both anchors are absolute timestamps or if they share the exact same logical anchor.

        :param other: The other range to evaluate for comparability.
        :type other: AnchoredTimeRange
        :return: True if comparison is possible, False otherwise.
        :rtype: bool
        """
        return (isinstance(self.anchor, arrow.Arrow) and isinstance(other.anchor, arrow.Arrow)) or self.anchor == other.anchor


    def __str__(self):
        """
        Returns a string representation showing the anchor and its associated time range.
        """
        return f'{self.anchor} + {self.time_range}'


@dataclass
class TimePoint:
    """
    Represents a specific moment in time as a collection of anchored constraints. 
    It provides the mathematical framework for resolving the most precise possible time window for a command dispatch based on all known relative and absolute information.
    A TimePoint can simultaneously track its relationship to sequence start, absolute time, and other markers.
    """
    references: "list[AnchoredTimeRange]"

    @staticmethod
    def at(anchor, offset = dt.timedelta()) -> "TimePoint":
        """
        Creates a new TimePoint at a specific anchor with an optional offset.
        This serves as the constructor for defining an exact point in time relative to a marker.

        :param anchor: The logical or absolute anchor for the point.
        :param offset: The initial offset from the anchor.
        :type offset: dt.timedelta
        :return: A new TimePoint instance.
        :rtype: TimePoint
        """
        return TimePoint([AnchoredTimeRange(anchor, TimeRange(offset, offset))])


    @staticmethod
    def after(other: "TimePoint") -> "TimePoint":
        """
        Creates a new TimePoint that is constrained to occur after another existing point.
        The resulting point has an infinite maximum bound relative to the original point's constraints.

        :param other: The preceding TimePoint.
        :type other: TimePoint
        :return: A new TimePoint representing the subsequent moment.
        :rtype: TimePoint
        """
        return TimePoint([AnchoredTimeRange(r.anchor, TimeRange(r.time_range.mn, None)) for r in other.references])


    def is_impossible(self):
        """
        Checks if the constraints of the TimePoint are logically contradictory.
        A point is impossible if any of its internal time ranges have become empty (min > max).

        :return: True if the point represents an impossible time state, False otherwise.
        """
        # This TimePoint is impossible if any time range is empty
        return any(not r.time_range for r in self.references)


    def __and__(self, other: "TimePoint") -> "TimePoint":
        """
        Combines two TimePoints that are intended to represent the same moment in time.
        It merges all references from both points, refining existing constraints through intersection wherever anchors are comparable.
        This logic is essential for synthesizing multiple timing requirements into a single consistent schedule.

        :param other: The other TimePoint to merge with.
        :type other: TimePoint
        :return: A refined TimePoint obeying all combined constraints.
        :rtype: TimePoint
        """
        new_refs = list(self.references)
        for other_ref in other.references:
            i,comp_ref = next(((i,c) for i,c in enumerate(new_refs) if other_ref.is_comparable(c)), (None, None))
            if comp_ref is None:
                new_refs.append(other_ref)
            else:
                # Refine and replace comp_ref
                new_refs[i] = comp_ref & other_ref
        return TimePoint(new_refs)


    def __add__(self, other):
        """
        Applies a time offset to every reference within the TimePoint.
        """
        return TimePoint([r + other for r in self.references])


    def __sub__(self, other: "TimePoint") -> TimeRange:
        """
        Calculates the relative time duration between this TimePoint and another.
        Since TimePoints involve uncertainty, the result is the intersection of all possible deltas computed across all shared anchors.
        This provides the most restrictive possible window of time that could separate the two events.

        :param other: The point to subtract.
        :type other: TimePoint
        :return: The resulting duration as a TimeRange.
        :rtype: TimeRange
        """
        # Take the Cartesian product of references, computing the time delta for each, and intersecting all of them.
        # That is, brute-force the answer by restricting by all possible comparisons.
        return reduce(TimeRange.__and__, (a - b for a in self.references for b in other.references), TimeRange())


    def __str__(self):
        """
        Returns a string representation of the TimePoint and its various references.
        """
        return '{' + ', '.join(map(str, self.references)) + '}'


class FR_Command_Timing_Checker(FRBase):
    """
    Implements complex validation logic for checking the timing relationships between commands in a sequence against a set of CSV-defined rules. 
    It performs a multi-pass analysis that first infers the dispatch timing for every step and then evaluates applicable rules across the entire sequence timeline.
    The checker handles various scenarios including absolute timestamps, relative offsets, and ambiguous nonlinear control flow.
    """
    __CONTROL_FLOW_DIRECTIVES = get_control_flow_directives()

    @staticmethod
    def __read_cmd_timing_rule_file(file: pathlib.Path) -> "list[CmdTimingRule]":
        """
        Internal helper to load and parse a CSV file containing command timing rule definitions.
        Each row is converted into a CmdTimingRule object that can be used for sequence validation.

        :param file: Path to the rule CSV file.
        :type file: pathlib.Path
        :return: A list of parsed rule objects.
        :rtype: list[CmdTimingRule]
        """
        rules = []
        with open(file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rule = CmdTimingRule(row)
                rules.append(rule)
        return rules

    @staticmethod
    def __compute_timing(seq: dict) -> "list[(int, dict, AnchoredTimeRange)]":
        """
        Analyzes a command sequence to determine the earliest and latest possible dispatch times for every individual step. 
        It handles absolute timestamps, relative offsets, and complex scenarios involving nonlinear control flow to build a comprehensive timing profile.
        The function also identifies the point where control flow becomes unpredictable, which limits the precision of subsequent timing checks.

        :param seq: The sequence dictionary to analyze.
        :type seq: SeqDict
        :return: A tuple containing the list of timed steps and the index of the first nonlinear command.
        :rtype: tuple[list, int]
        :raises ValueError: If the sequence contains out-of-order steps or invalid relative dispatches.
        """
        # First, label all steps in the sequence with time points
        # Sequences start at an abstract "sequence start" timepoint since we don't know when they'll be run.
        step_times = [TimePoint.at("Sequence Start")]
        nonlinear_control_flow_start = None
        enumerated_steps = list(enumerate(get_steps(seq), 1))
        for ind, step in enumerated_steps:
            if nonlinear_control_flow_start is not None:
                # If we've seen nonlinear control flow, give up on trying to infer detailed timing information.
                # Instead, just assign each step a unique, incomparable time point, and note that it's after the start of nonlinear code.
                # This will cause all future comparisons between relevant command pairs to come back ambiguous and be flagged.
                # Note that this doesn't encode the possibility that a nonlinear step doesn't execute at all - that needs to be handled separately.
                step_times.append(
                    TimePoint.at(f"Step {ind} Dispatch - Time unknown due to nonlinear control flow at step {nonlinear_control_flow_start}")
                    & TimePoint.after(step_times[nonlinear_control_flow_start]))
                continue

            if step.time is None:
                # If no time is specified, there's nothing to compute
                step_times.append(step_times[-1])
                continue

            # Compute time if we're still in here
            time_obj = step.time
            time_type = time_obj.timetype

            if time_type == SeqTimeType.ABSOLUTE:
                abs_dispatch_time = TimePoint.at(arrow.get(time_obj.tag))
                dispatch_time = abs_dispatch_time
                # Since we know the dispatch time exactly, refer back to every previous time point we knew,
                # try to calculate the time delta between each of those and now, and update our understanding of "now".
                # If at any point we discover we went backwards in time, raise an error to prevent propagating that contradiction.
                nonnegative = TimeRange(mn=dt.timedelta())
                for prior_step_number, prior_time in enumerate(step_times):
                    time_since_prior = (abs_dispatch_time - prior_time) & nonnegative
                    if not time_since_prior:
                        raise ValueError(f'Sequence contains out-of-order steps. Step {ind} happens at {abs_dispatch_time}, strictly before step {prior_step_number} at {prior_time}.')
                    dispatch_time &= prior_time + time_since_prior
                step_times.append(dispatch_time)
                continue

            if time_type in [SeqTimeType.ABSOLUTE, SeqTimeType.COMMAND_RELATIVE, SeqTimeType.EPOCH_RELATIVE]:
                tag = time_obj.tag.strip()
                sign = -1 if tag.startswith('-') else 1
                h,m,s = tag.lstrip('+-').split(':')
                delta = sign * dt.timedelta(hours=int(h), minutes=int(m), seconds=float(s))
            else:
                delta = dt.timedelta()

            if time_type == SeqTimeType.EPOCH_RELATIVE:
                abs_dispatch_time = TimePoint.at('Epoch', delta)
                dispatch_time = abs_dispatch_time
                # Since we know the dispatch time exactly (relative to Epoch), refer back to every previous time point we knew,
                # try to calculate the time delta between each of those and now, and update our understanding of "now".
                # If at any point we discover we went backwards in time, raise an error to prevent propagating that contradiction.
                nonnegative = TimeRange(mn=dt.timedelta())
                for prior_step_number, prior_time in enumerate(step_times):
                    time_since_prior = (abs_dispatch_time - prior_time) & nonnegative
                    if not time_since_prior:
                        raise ValueError(f'Sequence contains out-of-order steps. Step {ind} happens at {abs_dispatch_time}, strictly before step {prior_step_number} at {prior_time}.')
                    dispatch_time &= prior_time + time_since_prior
                step_times.append(dispatch_time)
            elif time_type == SeqTimeType.COMMAND_RELATIVE:
                if delta < dt.timedelta():
                    raise ValueError(f'Step {ind} uses a negative relative time dispatch {tag}, which is not allowed.')
                # The best case - we can just offset from the last dispatch time exactly
                step_times.append(step_times[-1] + delta)
            elif time_type == SeqTimeType.COMMAND_COMPLETE:
                # We have no idea how long the last command took, hence no idea how long we waited.
                # so the best we can do is "after the last command was dispatched", and abstractly "when the last command finished".
                # Note that this cannot introduce an out-of-order command.
                step_times.append(TimePoint.at(f'Step {ind - 1} Completion') & TimePoint.after(step_times[-1]))

            # Now that we've assigned a time to this step, look for things that'll mess up later commands' dispatch time
            if step.stem in FR_Command_Timing_Checker.__CONTROL_FLOW_DIRECTIVES:
                nonlinear_control_flow_start = ind

        if nonlinear_control_flow_start is None:
            nonlinear_control_flow_start = len(enumerated_steps)
        # Report where nonlinear control flow starts, if at all.
        # This is the step number of the first step before nonlinearity, so is the last step if the sequence is linear.
        return [(i, s, step_times[i]) for i,s in enumerated_steps], nonlinear_control_flow_start
        

    @staticmethod
    def __eval_cmd_timing_fr(extended_steps, rule: CmdTimingRule) -> FRCheckInfo:
        """
        Dispatches a specific timing check based on the rule type.
        It evaluates the entire sequence against the rule definition and returns an aggregated result summary.

        :param extended_steps: The sequence steps enriched with timing information.
        :param rule: The specific timing rule to evaluate.
        :type rule: CmdTimingRule
        :return: Aggregated validation results for the rule.
        :rtype: FRCheckInfo
        """
        if rule.rule_type == CmdTimingRuleType.FOLLOWS:
            return FR_Command_Timing_Checker.__check_follows(rule, extended_steps)
        if rule.rule_type == CmdTimingRuleType.FOLLOWED_BY:
            return FR_Command_Timing_Checker.__check_followed_by(rule, extended_steps)
        if rule.rule_type == CmdTimingRuleType.WAIT:
            return FR_Command_Timing_Checker.__check_wait(rule, extended_steps)
        if rule.rule_type == CmdTimingRuleType.OVERLAP:
            return FR_Command_Timing_Checker.__check_overlap(rule, extended_steps)
        raise AssertionError(f'Internal error: Unhandled enum type {rule.rule_type}. This error should never appear in production!')


    @staticmethod
    def __check_follows(rule, extended_steps):
        """Internal helper for FOLLOWS rules."""
        return FR_Command_Timing_Checker.__check_against_prior_steps(rule, extended_steps, rule.alert_level)


    @staticmethod
    def __check_followed_by(rule, extended_steps_info):
        """Internal helper for FOLLOWED_BY rules."""
        return FR_Command_Timing_Checker.__check_against_all_steps(rule, extended_steps_info, rule.alert_level,
            lambda step_number: extended_steps_info[0][step_number:], # 1-based index correction cancels the +1 to skip this step
            lambda cmd_time, rel_time: rel_time - cmd_time
        )


    @staticmethod
    def __check_wait(rule, extended_steps):
        """Internal helper for WAIT rules."""
        return FR_Command_Timing_Checker.__check_against_prior_steps(rule, extended_steps, FRState.PASSED)


    @staticmethod
    def __check_overlap(rule, extended_steps):
        """Internal helper for OVERLAP rules."""
        return FR_Command_Timing_Checker.__check_against_prior_steps(rule, extended_steps, FRState.PASSED)

    
    @staticmethod
    def __check_against_prior_steps(rule, extended_steps_info, default_step_result_state):
        """Internal helper to iterate backwards from a command to find related steps."""
        return FR_Command_Timing_Checker.__check_against_all_steps(
            rule,
            extended_steps_info,
            default_step_result_state,
            lambda step_number: reversed(extended_steps_info[0][:step_number - 1]),
            lambda cmd_time, rel_time: cmd_time - rel_time
        )


    @staticmethod
    def __check_against_all_steps(rule, extended_steps_info, default_step_result_state, get_rel_steps, get_delta):
        """
        Core logic for evaluating a timing rule against a range of sequence steps.
        It identifies matching command pairs and verifies if the time delta between them falls within the rule's allowed range.
        The function handles nonlinear control flow by merging statuses and adding descriptive warnings to the results.
        """
        extended_steps, nonlinear_start_step_number = extended_steps_info
        overall_result = FR_Command_Timing_Checker.__initial_check_info(rule)
        for step_number, step, time_point in extended_steps:
            is_cmd = rule.is_cmd(step)
            if is_cmd == ModalBool.NO:
                # Not relevant to this rule
                continue

            step_result = FR_Command_Timing_Checker.__result(default_step_result_state, step_number, step, rule, 'No matching command found.')
            if is_cmd == ModalBool.MAYBE:
                # Note our uncertainty around this command even triggering the FR by replacing the default result.
                step_result = FR_Command_Timing_Checker.__flag(step_number, step, rule,
                    f"This FR might apply to step {step_number}, but some arguments were symbolic, missing a name, or missing altogether."
                    f" If it does apply, then state would be {step_result.state} because {step_result.message}."
                    f" Please review this command for compliance with this flight rule.")

            for rel_step_number, rel_step, rel_time_point in get_rel_steps(step_number):
                if rel_step_number > nonlinear_start_step_number:
                    # Nonlinear steps are considered separately
                    continue
                is_rel = rule.is_rel(rel_step)
                if is_rel == ModalBool.NO:
                    continue
                is_pair = rule.is_pair(step, rel_step)
                if is_pair == ModalBool.NO:
                    continue
                delta = get_delta(time_point, rel_time_point)
                time_is_valid = rule.duration_range.contains(delta)
                if (is_cmd & is_rel & is_pair) != ModalBool.YES:
                    # We got here but we're not sure if this is a match... Report that uncertainty.
                    # Also report the timing information we've calculated.
                    verb = {
                        ModalBool.YES: 'does',
                        ModalBool.NO: 'does not',
                        ModalBool.MAYBE: 'may'
                    }[time_is_valid]
                    step_result = FR_Command_Timing_Checker.__flag(step_number, step, rule,
                        f'Step {rel_step_number} might match, but some arguments were symbolic, missing a name, or missing altogether.'
                        f' Please review whether these commands match the requirements for this FR.'
                        f' Calculated the time between these commands to be {delta}, which {verb} obey this FR.'
                        f' If this flight rule does not apply to these commands, please look for other commands that might match instead.')
                elif time_is_valid == ModalBool.YES:
                    step_result = FR_Command_Timing_Checker.__pass(step_number, step, rule,
                        f'Step {rel_step_number} matches and timing is valid.'
                        f' Inferred time between commands is {delta}, in legal range of {rule.duration_range}.')
                elif time_is_valid == ModalBool.NO:
                    step_result = FR_Command_Timing_Checker.__violation(step_number, step, rule,
                        f'Step {rel_step_number} matches but timing is not valid.'
                        f' Inferred time between commands is {delta}, not in legal range of {rule.duration_range}.')
                else: # time_is_valid == ModalBool.MAYBE
                    step_result = FR_Command_Timing_Checker.__flag(step_number, step, rule,
                        f'Step {rel_step_number} matches but timing cannot be determined.'
                        f' Inferred time between commands is {delta}, ambiguous compared to legal range of {rule.duration_range}.'
                        f' Please verify timing manually.')
                break

            matched_nonlinear_step = False
            for rel_step_number, rel_step, rel_time_point in extended_steps[nonlinear_start_step_number:]: # 1-based index correction cancels the +1 to get first nonlinear step
                is_rel = rule.is_rel(rel_step)
                if is_rel == ModalBool.NO:
                    continue
                is_pair = rule.is_pair(step, rel_step)
                if is_pair == ModalBool.NO:
                    continue
                delta = get_delta(time_point, rel_time_point)
                time_is_valid = rule.duration_range.contains(delta)
                time_descr = {
                    ModalBool.YES: 'in',
                    ModalBool.NO: 'not in',
                    ModalBool.MAYBE: 'ambiguous compared to',
                }[time_is_valid]
                additional_state = FRState.PASSED if (is_rel & is_pair & time_is_valid) == ModalBool.YES else FRState.FLAGGED
                if matched_nonlinear_step:
                    # If we've already seen a match in the nonlinear period, just tack on another message.
                    new_message = (step_result.message +
                        f' Also, may match step {rel_step_number} after nonlinear control flow starts on {nonlinear_start_step_number}.'
                        f' Inferred time between commands is {delta}, {time_descr} legal range of {rule.duration_range}.')
                else:
                    # Otherwise, put the rule message up front, splice in the message for the linear portion, and add the message for the nonlinear portion.
                    # This keeps the message simpler when no commands in the nonlinear portion match (including when the sequence is completely linear).
                    new_message = (
                        rule.message +
                        f' During linear control flow (up to step {nonlinear_start_step_number}): {step_result.message[len(rule.message):]}'
                        f' During nonlinear control flow (after step {nonlinear_start_step_number}):'
                        f' May match step {rel_step_number} after nonlinear control flow starts on {nonlinear_start_step_number}.'
                        f' Inferred time between commands is {delta}, {time_descr} legal range of {rule.duration_range}.')

                matched_nonlinear_step = True

                # By merging the states together, we allow this step to still pass when it matches a nonlinear command if and only if:
                # 1) It passes without matching this command, since this command may not execute, and
                # 2) It passes while matching this command, given only the limited timing information for nonlinear steps.
                step_result = FRResult(
                    state=step_result.state.merge(additional_state),
                    step_number=step_result.step_number,
                    command_stem=step_result.command_stem,
                    command_args=step_result.command_args,
                    flight_rule_id=step_result.flight_rule_id,
                    message=new_message)

            overall_result += step_result
        return overall_result


    @staticmethod
    def __initial_check_info(rule):
        """Initializes a blank result summary for a timing rule."""
        return FRCheckInfo(
            flight_rule_id=rule.fr_id,
            flight_rule_version=rule.fr_version,
            flight_rule_description=rule.fr_description,
            criticality=rule.fr_criticality,
            state=FRState.PASSED,
            num_violations=0,
            results=[]
        )


    @staticmethod
    def __pass(step_number, step, rule, msg=None):
        """Generates a PASSED result for a specific command."""
        return FR_Command_Timing_Checker.__result(FRState.PASSED, step_number, step, rule, msg)


    @staticmethod
    def __flag(step_number, step, rule, msg=None):
        """Generates a FLAGGED result for a specific command."""
        return FR_Command_Timing_Checker.__result(FRState.FLAGGED, step_number, step, rule, msg)


    @staticmethod
    def __violation(step_number, step, rule, msg=None):
        """Generates a VIOLATION result based on the rule's alert level."""
        return FR_Command_Timing_Checker.__result(rule.alert_level, step_number, step, rule, msg)


    @staticmethod
    def __result(state, step_number, step, rule, msg=None):
        """Internal helper to construct an FRResult object."""
        if msg is not None:
            msg = ' ' + msg
        return FRResult(
            state=state,
            step_number=step_number,
            command_stem=step.stem if step is not None else "SEQUENCE",
            command_args=step.args if step is not None else {},
            flight_rule_id=rule.fr_id,
            message=rule.message + msg)


    @staticmethod
    def __augment_result(result, additional_state, additional_msg):
        """Appends additional information to an existing result."""
        return FRResult(
            state=result.state + additional_state,
            step_number=result.step_number,
            command_stem=result.command_stem,
            command_args=result.command_args,
            flight_rule_id=result.flight_rule_id,
            message=result.message + ' ' + additional_msg)


    @staticmethod
    def check_fr(sequence: SeqDict, config: dict) -> "list[FRCheckInfo]":
        """
        Serves as the main entry point for executing command timing validations within the FRESH framework. 
        It loads rules from external files, calculates the sequence-wide timing model, and aggregates the results of every applicable check.
        If the timing calculation fails due to sequence errors, it returns flags explaining the failure for every rule.

        :param sequence: The parsed command sequence to validate.
        :type sequence: SeqDict
        :param config: The configuration dictionary containing rule file paths and directories.
        :type config: dict
        :return: A list of aggregated results, one for every timing rule evaluated.
        :rtype: list[FRCheckInfo]
        """
        config_dir = pathlib.Path(config['config_dir'])
        rule_files = [config_dir.joinpath(p) for p in config['command_timing_rule_files']]
        rules = []
        for file in rule_files:
            rules += FR_Command_Timing_Checker.__read_cmd_timing_rule_file(file)
        try:
            extended_sequences = FR_Command_Timing_Checker.__compute_timing(sequence)
        except ValueError as e:
            return [
                FR_Command_Timing_Checker.__initial_check_info(rule) + FR_Command_Timing_Checker.__flag(-1, None, rule,
                    f'Sequence does not have valid timing! Please correct the following error and re-check: {e}')
                for rule in rules
            ]
        except Exception as e:
            return [
                FR_Command_Timing_Checker.__initial_check_info(rule) + FR_Command_Timing_Checker.__flag(-1, None, rule,
                    f'Error computing sequence timing! Please correct the following error and re-check: {e}')
                for rule in rules
            ]
        return [
            FR_Command_Timing_Checker.__eval_cmd_timing_fr(extended_sequences, rule)
            for rule in rules
        ]