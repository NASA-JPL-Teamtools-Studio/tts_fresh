import enum
import pathlib
import csv
import re

from tts_fresh.flightrules.fr_base import FRBase, FRCheckInfo, FRCriticality, FRResult, FRState
from tts_fresh.utils.step_utils import get_steps
from tts_fresh.seqdict import SeqDict, SeqArgType, SeqStepType


class CmdArgRuleType(enum.Enum):
    """
    Categorizes the type of validation to perform on a command argument. 
    It determines whether an argument should be checked against integer, float, or hexadecimal ranges, or a discrete list of allowed values.
    """
    range_int = 1
    range_float = 2
    range_hex = 3
    list_type = 4


class AllowableCmdRangeOperators(enum.Enum):
    """
    Defines the mathematical comparison operators allowed for range-based command argument validation.
    These members are used to construct the logical expressions that verify if a command argument falls within required bounds.
    """
    LT = 1
    GT = 2
    LTEQ = 3
    GTEQ = 4

    @staticmethod
    def from_symbol(symbol: str) -> "AllowableCmdRangeOperators":
        """
        Maps a string-based mathematical symbol to its corresponding enum member.
        This utility is essential for parsing rule definitions from text-based configuration files into executable logic.

        :param symbol: The string symbol to be converted (e.g., '<', '>=', etc.).
        :type symbol: str
        :return: The associated operator enum member.
        :rtype: AllowableCmdRangeOperators
        :raises NotImplementedError: If the provided symbol is not a recognized operator.
        """
        if symbol == '<':
            return AllowableCmdRangeOperators.LT
        if symbol == '<=':
            return AllowableCmdRangeOperators.LTEQ
        if symbol == '>':
            return AllowableCmdRangeOperators.GT
        if symbol == '>=':
            return AllowableCmdRangeOperators.GTEQ
        raise NotImplementedError(f'{symbol} is not a valid symbol for a command range operator.')


class CmdArgRule:
    """
    Encapsulates a single flight rule governing the valid values or ranges for a specific spacecraft command argument.
    It stores the criteria for identifying the target command and argument, along with the logic for range or list-based validation.
    """
    fr_id: str
    fr_version: str
    fr_description: str
    fr_criticality: FRCriticality
    alert_level: FRState
    cmd_stem: str
    cmd_arg: str
    rule_type: CmdArgRuleType
    range_exclusion: bool
    value_list: list
    range_dict: dict
    message: str

    def __init__(self, args: dict):
        """
        Initializes the rule criteria from a configuration dictionary.
        It handles the complex setup of parsing range strings, exclusion zones, or allowed value lists depending on the rule type.

        :param args: A dictionary containing the rule parameters, typically sourced from a CSV row.
        :type args: dict
        """
        self.fr_id = args['FR_ID']
        self.fr_version = args['FR_Version']
        self.fr_description = args['Message']
        crit_letter = args['FR_ID'].split('-')[1]
        self.fr_criticality = FRCriticality.from_letter(crit_letter)
        self.alert_level = FRState[args['Alert_Level']]
        self.cmd_stem = args['Command_Stem']
        self.cmd_arg = args['Arg_Name']
        self.rule_type = CmdArgRuleType[args['Arg_Check_Type']]
        self.range_exclusion = True if len(args['Arg_Exclusion_Range']) > 0 else False
        self.message = args['Message']
        if self.rule_type == CmdArgRuleType.list_type:
            if args['Arg_Allowed_Value_List'].startswith('[') and args['Arg_Allowed_Value_List'].endswith(']'):
                self.value_list = [v.strip() for v in args['Arg_Allowed_Value_List'][1:-1].split('|')]
            else:
                raise SyntaxError("List must be of the format: [ 1 | 2 | ... | n ]")
        else:
            self.range_dict = self._make_range_dict(args['Arg_Range'], self.range_exclusion, args['Arg_Exclusion_Range'], self.rule_type)

    @staticmethod
    def _make_range_dict(range_str: str, has_ex: bool, ex_range_str: str, type: CmdArgRuleType) -> dict:
        """
        Parses a complex range string into a structured dictionary of limits and operators.
        It uses regular expressions to tokenise the input and supports both standard inclusive/exclusive ranges and specific exclusion sub-ranges.

        :param range_str: The primary range definition string (e.g., '0 <= n < 100').
        :type range_str: str
        :param has_ex: A flag indicating whether an exclusion range is defined for this rule.
        :type has_ex: bool
        :param ex_range_str: The string defining the sub-range to be excluded from the primary range.
        :type ex_range_str: str
        :param type: The data type to use when parsing numeric values (int, float, or hex).
        :type type: CmdArgRuleType
        :return: A structured dictionary containing parsed limits and comparison operators.
        :rtype: dict
        :raises SyntaxError: If the range or exclusion range strings do not match the required format.
        """
        range_tokens = re.split(r'([xX=<>]+|[\d\w.+\-]+)', range_str)
        range_tokens = [t.strip() for t in range_tokens if re.match(r'[\S]+', t.strip())]
        if len(range_tokens) != 5:
            raise SyntaxError("Range must be of the format: v1 op n op v2")
        result = {
            'range_str': range_str,
            'min_op': AllowableCmdRangeOperators.from_symbol(range_tokens[1]),
            'max_op': AllowableCmdRangeOperators.from_symbol(range_tokens[3]),
        }
        if type == CmdArgRuleType.range_int:
            result['min'] = int(range_tokens[0])
            result['max'] = int(range_tokens[4])
        elif type == CmdArgRuleType.range_float:
            result['min'] = float(range_tokens[0])
            result['max'] = float(range_tokens[4])
        else:
            result['min'] = int(range_tokens[0], base=16)
            result['max'] = int(range_tokens[4], base=16)
        if has_ex:
            ex_range_tokens = re.split(r'([xX=<>]+|[\d\w.+\-]+)', ex_range_str)
            ex_range_tokens = [t for t in ex_range_tokens if re.match(r'[\S]+', t.strip())]
            if len(ex_range_tokens) != 5:
                raise SyntaxError("Exclusion range must be of the format: v1 op n op v2")
            result['ex_range_str'] = ex_range_str
            result['ex_min_op'] = AllowableCmdRangeOperators.from_symbol(ex_range_tokens[1])
            result['ex_max_op'] = AllowableCmdRangeOperators.from_symbol(ex_range_tokens[3])
            if type == CmdArgRuleType.range_int:
                result['ex_min'] = int(ex_range_tokens[0])
                result['ex_max'] = int(ex_range_tokens[4])
            elif type == CmdArgRuleType.range_float:
                result['ex_min'] = float(ex_range_tokens[0])
                result['ex_max'] = float(ex_range_tokens[4])
            else:
                result['ex_min'] = int(ex_range_tokens[0], base=16)
                result['ex_max'] = int(ex_range_tokens[4], base=16)
        return result
    
    def value_in_list(self, n: any) -> bool:
        """
        Checks if a specific argument value is present within the rule's predefined list of allowed values.

        :param n: The value extracted from a sequence command argument.
        :type n: any
        :return: True if the value is found in the allowed list, False otherwise.
        :rtype: bool
        """
        return str(n) in self.value_list

    def value_in_range(self, n: any) -> bool:
        """
        Evaluates whether a numeric or hex argument value falls within the valid range defined by the rule.
        It also accounts for any exclusion ranges, ensuring that values falling inside an exclusion zone are treated as invalid.

        :param n: The numeric or hex value to be validated.
        :type n: any
        :return: True if the value is within the allowed range and outside any exclusion zone, False otherwise.
        :rtype: bool
        """
        in_range = self._eval_single_op(self.range_dict['min'], self.range_dict['min_op'], n) and self._eval_single_op(n, self.range_dict['max_op'], self.range_dict['max'])
        if self.range_exclusion:
            in_exclusion = self._eval_single_op(self.range_dict['ex_min'], self.range_dict['ex_min_op'], n) and self._eval_single_op(n, self.range_dict['ex_max_op'], self.range_dict['ex_max'])
            in_range = in_range and (not in_exclusion)
        return in_range
    
    @staticmethod
    def _eval_single_op(v1: any, op: AllowableCmdRangeOperators, v2: any) -> bool:
        """
        Internal helper to execute a single comparison operation between two values using a specified operator.

        :param v1: The left-hand operand for the comparison.
        :param op: The operator enum member representing the comparison type.
        :type op: AllowableCmdRangeOperators
        :param v2: The right-hand operand for the comparison.
        :return: The result of the boolean comparison.
        :rtype: bool
        :raises NotImplementedError: If the operator member is not explicitly handled.
        """
        if op == AllowableCmdRangeOperators.LT:
            return (v1 < v2)
        if op == AllowableCmdRangeOperators.LTEQ:
            return (v1 <= v2)
        if op == AllowableCmdRangeOperators.GT:
            return (v1 > v2)
        if op == AllowableCmdRangeOperators.GTEQ:
            return (v1 >= v2)
        raise NotImplementedError
        

class FR_Command_Arg_Checker(FRBase):
    """
    Implements validation logic for checking individual command arguments against mission-specific range and list rules.
    It serves as a core flight rule checker within the FRESH framework, capable of processing CSV-defined argument constraints.
    """

    @staticmethod
    def _read_cmd_arg_rule_file(file: pathlib.Path) -> "list[CmdArgRule]":
        """
        Loads and parses a CSV file containing command argument validation rules into a list of rule objects.

        :param file: The path to the rule CSV file to be loaded.
        :type file: pathlib.Path
        :return: A list of initialized CmdArgRule objects.
        :rtype: list[CmdArgRule]
        """
        rules = []
        with open(file, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rule = CmdArgRule(row)
                rules.append(rule)
        return rules
    
    @staticmethod
    def _eval_cmd_arg_fr(seq: SeqDict, rule: CmdArgRule) -> FRCheckInfo:
        """
        Evaluates a single argument rule against all applicable commands within a sequence to identify violations.
        It iterates through the sequence, identifying steps that match the rule's target command stem, and performs the required range or list checks on the specified argument.

        :param seq: The sequence dictionary containing the commands to be validated.
        :type seq: SeqDict
        :param rule: The specific argument validation rule to apply.
        :type rule: CmdArgRule
        :return: An aggregated check info object containing all findings for this rule across the sequence.
        :rtype: FRCheckInfo
        """
        result = FRCheckInfo(
            flight_rule_id=rule.fr_id,
            flight_rule_version=rule.fr_version,
            flight_rule_description=rule.fr_description,
            criticality=rule.fr_criticality,
            state=FRState.PASSED,
            num_violations=0,
            results=[]
        )
        for step_num, step in enumerate(seq.steps, 1):
            if step.steptype == SeqStepType.COMMAND and step.stem == rule.cmd_stem:
                rule_passed = False
                target_arg = None
                for arg in step.args:
                    if arg.name == rule.cmd_arg:
                        target_arg = arg
                if target_arg is None or target_arg.argtype == SeqArgType.SYMBOL: 
                    rule_passed = False
                elif rule.rule_type == CmdArgRuleType.list_type:
                    rule_passed = rule.value_in_list(target_arg.value)
                elif rule.rule_type == CmdArgRuleType.range_int:
                    rule_passed = rule.value_in_range(int(target_arg.value))
                elif rule.rule_type == CmdArgRuleType.range_float:
                    rule_passed = rule.value_in_range(float(target_arg.value))
                elif rule.rule_type == CmdArgRuleType.range_hex:
                    if target_arg.argtype == SeqArgType.HEX:
                        rule_passed = rule.value_in_range(int(target_arg.value, base=16))
                    else:
                        rule_passed = rule.value_in_range(int(target_arg.value, base=10))
                if not rule_passed:
                    result += FRResult(
                        state=rule.alert_level,
                        step_number=step_num,
                        command_stem=step.stem,
                        command_args=step.args,
                        flight_rule_id=rule.fr_id,
                        message=rule.message
                    )
        return result

    @staticmethod
    def check_fr(sequence: SeqDict, config: dict) -> "list[FRCheckInfo]":
        """
        Entry point for the checker, coordinating the loading of multiple rule files and the evaluation of each rule against the sequence.
        It locates the relevant rule files from the configuration and returns a collection of results for every rule processed.

        :param sequence: The parsed sequence to be validated.
        :type sequence: SeqDict
        :param config: The mission configuration dictionary containing rule file paths.
        :type config: dict
        :return: A list of aggregated check info objects, one for every evaluated rule.
        :rtype: list[FRCheckInfo]
        """
        config_dir = pathlib.Path(config['config_dir'])
        rule_files = [config_dir.joinpath(p) for p in config['command_argument_rule_files']]
        rules = []
        for file in rule_files:
            rules += FR_Command_Arg_Checker._read_cmd_arg_rule_file(file)
        results = []
        for rule in rules:
            results.append(FR_Command_Arg_Checker._eval_cmd_arg_fr(sequence, rule))
        return results