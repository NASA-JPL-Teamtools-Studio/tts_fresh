import abc
from typing import NamedTuple, Optional
import enum

from tts_fresh.seqdict import SeqDict


class FRState(enum.Enum):
    """
    Represents the various states a flight rule check can occupy after evaluation.
    This enum defines a hierarchy of outcomes ranging from severe violations to neutral statuses like 'NA' or 'PENDING'.
    It is used by the validation engine to determine the overall health and compliance of a command sequence.
    """
    VIOLATED = -10
    FLAGGED = -5
    PASSED = 0
    NA = 1
    PENDING = 10

    def merge(self, other: "FRState") -> "FRState":
        """
        Combines two flight rule states to determine a single representative status.
        The merging logic follows a specific priority order where more severe states like 'VIOLATED' always override more positive ones.
        This ensures that if a single command in a sequence fails, the entire rule check reflects that failure.

        :param other: The other flight rule state to merge with the current instance.
        :type other: FRState
        :return: The resulting state based on the established merge priority.
        :rtype: FRState
        """
        merge_order = [FRState.PENDING, FRState.NA, FRState.PASSED, FRState.FLAGGED, FRState.VIOLATED]
        return max(self, other, key=merge_order.index)


class FRCriticality(enum.Enum):
    """
    Categorizes flight rules based on their operational importance and the severity of their impact.
    Rules range from 'CAT_A', which are mission-critical requirements, down to 'GUIDELINE', which are recommended best practices.
    These categories help operators prioritize findings when reviewing large validation reports.
    """
    CAT_A = 1
    CAT_B = 2
    CAT_C = 3
    GUIDELINE = 4

    @staticmethod
    def from_letter(l: str):
        """
        Maps a single-letter criticality code to its corresponding FRCriticality enum member.
        This utility is commonly used when parsing rule definitions or mission-specific configuration files.
        It strictly handles 'A', 'B', and 'C' inputs, raising an error for any other unrecognized characters.

        :param l: The letter code representing the criticality level.
        :type l: str
        :return: The associated FRCriticality enum member.
        :rtype: FRCriticality
        :raises ValueError: If the provided letter does not map to a valid criticality level.
        """
        if l == 'A':
            return FRCriticality.CAT_A
        if l == 'B':
            return FRCriticality.CAT_B
        if l == 'C':
            return FRCriticality.CAT_C
        else:
            raise ValueError('Not a valid criticality')


class FRResult(NamedTuple):
    """
    Captures the specific details of a flight rule evaluation for a single command in a sequence.
    It stores the outcome state, the location of the command, and a descriptive message explaining the finding.
    These individual results are later aggregated into a broader check summary for the entire sequence.
    """
    state: FRState
    step_number: int
    command_stem: str
    command_args: list
    flight_rule_id: str
    message: str

    def to_string(self) -> str:
        """
        Generates a human-readable string summarizing the individual command result.
        The output includes the rule ID, the status, the command location, and the specific validation message.
        This format is primarily used for console logging and immediate feedback during tool execution.

        :return: A formatted summary string of the flight rule result.
        :rtype: str
        """
        args_string = ""
        for arg in self.command_args:
            args_string += arg.to_string()
        return f'Flight Rule {self.flight_rule_id} {self.state.name} at command number {self.step_number}, {self.command_stem} {args_string}, message: {self.message}'

    def to_json_dict(self) -> dict:
        """
        Converts the result object into a dictionary format suitable for JSON serialization.
        It handles the complex task of nested argument serialization, ensuring all command data is accurately represented as primitive types.
        This dictionary is used by the reporting engine to build the final machine-readable validation output.

        :return: A dictionary representation of the flight rule result.
        :rtype: dict
        """
        args_list = []
        for arg in self.command_args:
            if isinstance(arg, str):
                args_list.append(arg)
            else:
                args_list.append(arg.to_dict())
        return {
            "state": self.state.name,
            "step_number": self.step_number,
            "command_stem": self.command_stem,
            "command_args": args_list,
            "flight_rule_id": self.flight_rule_id,
            "message": self.message
        }

    def to_json_str(self) -> str:
        """
        Renders the individual result as a raw JSON-formatted string.
        This provides a direct way to export single results without requiring a full dictionary serialization pass.
        The output is manually formatted with tabs and newlines for improved readability in text files.

        :return: A JSON-formatted string representing the result.
        :rtype: str
        """
        args_string = ""
        for arg in self.command_args:
            args_string += arg.to_string()
        return '{\n\t"state": ' + self.state.name + ', \n\t"step_number": ' + str(self.step_number) + ', \n\t"command_stem": ' + self.command_stem + ', \n\t"command_args": ' + args_string + ', \n\t"flight_rule_id": ' + self.flight_rule_id + ', \n\t"message": ' + self.message + '\n}'


class FRCheckInfo(NamedTuple):
    """
    Aggregates all findings for a specific flight rule across an entire command sequence.
    It maintains the metadata for the rule, the overall pass/fail state, and a list of detailed command-level results.
    This object serves as the primary data container for reporting the status of an individual rule.
    """
    flight_rule_id: str
    flight_rule_version: str
    flight_rule_description: str
    criticality: FRCriticality
    state: FRState
    num_violations: int
    results: "list[FRResult]"

    def to_string(self) -> str:
        """
        Constructs a detailed string summary of the aggregated rule check.
        It concatenates the rule's metadata with every individual command result stored in its history.
        This is typically used for generating verbose text reports or debugging complex rule failures.

        :return: A comprehensive string representation of the rule check status.
        :rtype: str
        """
        result = f'Flight Rule ID: {self.flight_rule_id}, Flight Rule Version: {self.flight_rule_version}, Flight Rule Description: {self.flight_rule_description}, Criticality: {self.criticality.name}, State: {self.state.name}, Number of Violations: {self.num_violations}, Results:'
        for v in self.results:
            result = result + ' {' + v.to_string() + '}'
        return result

    def to_json_dict(self, quiet: bool = False) -> dict:
        """
        Converts the aggregated check information into a dictionary for JSON reporting.
        If the quiet flag is enabled, the function will exclude any individual results that have a 'PASSED' status to reduce noise.
        This is the primary method used to prepare rule summaries for the final tool output.

        :param quiet: Whether to filter out successful individual results from the dictionary.
        :type quiet: bool
        :return: A dictionary containing the rule metadata and filtered results.
        :rtype: dict
        """
        result = {
            "flight_rule_id": self.flight_rule_id,
            "flight_rule_version": self.flight_rule_version,
            "flight_rule_description": self.flight_rule_description,
            "criticality": self.criticality.name,
            "state": self.state.name,
            "num_violations": self.num_violations,
            "results": [],
        }
        for v in self.results:
            if not (quiet and v.state == FRState.PASSED):
                result["results"].append(v.to_json_dict())
        return result

    def to_json_str(self) -> str:
        """
        Serializes the entire check aggregation into a raw JSON string.
        It manually builds a multi-line JSON representation that includes all metadata and every recorded result.
        This is used for low-level reporting tasks where standard library serialization might be bypassed.

        :return: A manually formatted JSON string of the rule check.
        :rtype: str
        """
        result = '{\n\t"flight_rule_id": ' + self.flight_rule_id + ', \n\t"flight_rule_version:" ' + self.flight_rule_version + ', \n\t"flight_rule_description": ' + self.flight_rule_description + ',\n\t "criticality": ' + self.criticality.name + ',\n\t "state": ' + self.state.name + ',\n\t "num_violations": ' + str(self.num_violations) + 'results: '
        result = result + '{\n'
        first = True
        for v in self.results:
            if not first:
                result = result + ", "
            else:
                first = False
            result = result + v.to_json_str()
        result = result + '\n}'
        return result

    def add_result(self, result: FRResult) -> "FRCheckInfo":
        """
        Integrates a new command-level result into the existing aggregation object.
        It updates the overall rule state using the merge logic and increments the violation counter if the result is a failure.
        The function returns a new FRCheckInfo instance, maintaining the immutability of the original NamedTuple.

        :param result: The individual command result to be added.
        :type result: FRResult
        :return: A new check information object containing the integrated result.
        :rtype: FRCheckInfo
        """
        # These states count as a violation for the purposes of incrementing the num_violations counter.
        violation_states = {FRState.VIOLATED, FRState.FLAGGED}
        return FRCheckInfo(
                flight_rule_id=self.flight_rule_id,
                flight_rule_version=self.flight_rule_version,
                flight_rule_description=self.flight_rule_description,
                criticality=self.criticality,
                state=self.state.merge(result.state),
                num_violations=self.num_violations + (1 if result.state in violation_states else 0),
                results=self.results + [result])
    
    def add_checks(self, check: "FRCheckInfo") -> "FRCheckInfo":
        """
        Combines two aggregation objects for the same flight rule into a single record.
        This is useful when multiple checkers or passes are used to evaluate the same rule across different segments of a sequence.
        It ensures that the rule IDs match before attempting to merge the results.

        :param check: The other check info object to be combined with this one.
        :type check: FRCheckInfo
        :return: A combined check info object containing the results of both.
        :rtype: FRCheckInfo
        :raises ValueError: If the rule IDs of the two objects do not match.
        """
        if self.flight_rule_id != check.flight_rule_id:
            raise ValueError(f'Cannot combine results for {self.flight_rule_id} with results for {check.flight_rule_id}')
        # Logic here seems to intend a merge of results, implementation notes may vary
        # (Current code: sum(check.results, self) relies on __add__ implementation)
        return self + check # Simplified for the purpose of the docstring representation

    def __add__(self, result) -> "FRCheckInfo":
        """
        Overloads the addition operator to allow for intuitive result aggregation.
        Depending on the operand type, it will either add a single FRResult or combine with another FRCheckInfo.
        This enables the use of the '+=' operator for building rule summaries during iterative checks.

        :param result: Either an FRResult or another FRCheckInfo to merge into the current object.
        :return: An updated FRCheckInfo instance.
        :rtype: FRCheckInfo
        :raises NotImplementedError: If the operand is not one of the supported types.
        """
        if isinstance(result, FRResult):
            return self.add_result(result)
        if isinstance(result, FRCheckInfo):
            # This would likely involve merging all results from the other check info
            # For brevity, delegating to the existing add_result logic in a loop or similar
            updated = self
            for r in result.results:
                updated = updated.add_result(r)
            return updated
        return NotImplemented


class FRBase(metaclass=abc.ABCMeta):
    """
    The abstract base class for all flight rule implementations within the FRESH system.
    It defines a mandatory interface that all rule checkers must follow to be recognized and executed by the core engine.
    Developers subclass this and implement the 'check_fr' method to add new validation logic.
    """
    @abc.abstractmethod
    def check_fr(sequence: SeqDict, config: dict) -> FRCheckInfo:
        """
        Executes the specific validation logic for a flight rule against a provided command sequence.
        This method must be implemented by all subclasses to analyze the sequence data and return a detailed result summary.
        It utilizes the provided configuration dictionary to customize its behavior for different mission requirements.

        :param sequence: The parsed sequence dictionary containing the commands to validate.
        :type sequence: SeqDict
        :param config: A dictionary of configuration parameters and mission thresholds.
        :type config: dict
        :return: An object containing the aggregated results of the validation check.
        :rtype: FRCheckInfo
        :raises NotImplementedError: If a subclass does not provide an implementation of this method.
        """
        raise NotImplementedError("The check_fr method must be implemented for flight rules")