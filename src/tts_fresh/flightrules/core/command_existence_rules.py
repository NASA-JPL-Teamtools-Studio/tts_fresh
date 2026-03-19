import enum
import pathlib
import csv
from dataclasses import dataclass
from tts_fresh.flightrules.fr_base import FRBase, FRCheckInfo, FRCriticality, FRResult, FRState
from tts_fresh.utils.step_utils import get_criticality, get_steps
from tts_fresh.seqdict import SeqDict

DEFAULT_HEADER = ['FR_ID', 'FR_Version', 'Alert_Level', 'Command_Stem', 'Message']

# Dummy flight rule name, used to signal that something in the checker itself failed.
DUMMY_FR = 'COMMAND_EXISTENCE_FLIGHT_RULES_CHECKER-A-0000'

class CommandExistenceRulesChecker(FRBase):
    """
    Do not send command X in condition Y.
    
    Validates a command sequence against a set of rules that restrict or flag the existence of specific commands.
    This checker reads external CSV files to identify which command stems are prohibited or require warnings when present in a sequence.
    It provides a centralized way to enforce mission-wide constraints on command usage for various operational modes.
    """

    def check_fr(sequence: SeqDict, config: dict) -> FRCheckInfo:
        """
        Executes the command existence validation logic by scanning the provided sequence for restricted command stems.
        It dynamically loads multiple rule files defined in the mission configuration and aggregates findings for every unique rule ID encountered.
        If a restricted command is found, the checker records the specific step number and generates a corresponding violation or warning result.

        :param sequence: The parsed sequence dictionary containing the list of command steps to be validated.
        :type sequence: SeqDict
        :param config: The configuration dictionary containing the paths to the CSV files that define command existence rules.
        :type config: dict
        :return: A sorted list of check information objects summarizing the results for every evaluated command existence rule.
        :rtype: list[FRCheckInfo]
        """
        config_dir = pathlib.Path(config['config_dir'])
        command_existence_rules_files = [config_dir.joinpath(p) for p in config['command_existence_rule_files']]
        results_by_rule_name = dict()
        for command_existence_rules_file in command_existence_rules_files:
            for row_number, rule in CommandExistenceRulesChecker.read_command_existence_rules_csv(command_existence_rules_file):
                if rule is None:
                    # Something went wrong reading this rule!
                    if DUMMY_FR not in results_by_rule_name:
                        results_by_rule_name[DUMMY_FR] = FRCheckInfo(
                                flight_rule_id=DUMMY_FR,
                                flight_rule_version="0",
                                flight_rule_description=(
                                    "This is a dummy flight rule added by the command existence flight rules checker"
                                    " when something goes wrong in the checker itself."
                                    " The presence of this result indicates a serious problem with"
                                    " the input or code of the checker."
                                    ),
                                criticality=FRCriticality.CAT_A,
                                state=FRState.VIOLATED, # TODO - should this be another state instead?
                                num_violations=0,
                                results=[])
                    results_by_rule_name[DUMMY_FR] = results_by_rule_name[DUMMY_FR].add_result(
                            FRResult(
                                state=FRState.VIOLATED,
                                step_number=-1,
                                command_stem="SEQUENCE",
                                command_args=[],
                                flight_rule_id=DUMMY_FR,
                                message=(
                                    f"There was an error reading row {row_number} of {command_existence_rules_file}."
                                    f" Some flight rules may not be checked!")))
                    continue
                # Otherwise, the rule was read properly.

                if rule.rule_name not in results_by_rule_name:
                    results_by_rule_name[rule.rule_name] = FRCheckInfo(
                            flight_rule_id=rule.rule_name,
                            flight_rule_version=rule.rule_version,
                            flight_rule_description="",
                            criticality=get_criticality(rule.rule_name),
                            state=FRState.PASSED,
                            num_violations=0,
                            results=[])
                if rule.message != '':
                    results_by_rule_name[rule.rule_name] = CommandExistenceRulesChecker.append_to_description(
                            results_by_rule_name[rule.rule_name],
                            rule.message)
                level_word = "ERROR" if rule.level == FRState.VIOLATED else "WARNING"
                results_by_rule_name[rule.rule_name] = CommandExistenceRulesChecker.append_to_description(
                        results_by_rule_name[rule.rule_name],
                        f"It is a {level_word} for {rule.command} to appear in a sequence.")

                steps = get_steps(sequence)
                for step_number, step in enumerate(steps, 1):
                    if step.stem == rule.command:
                        results_by_rule_name[rule.rule_name] = results_by_rule_name[rule.rule_name].add_result(
                                FRResult(
                                    state=rule.level,
                                    step_number=step_number,
                                    command_stem=step.stem,
                                    command_args=step.args,
                                    flight_rule_id=rule.rule_name,
                                    message=rule.message))

        return sorted(results_by_rule_name.values(), key=lambda fr_check_info: fr_check_info.flight_rule_id)


    @staticmethod
    def read_command_existence_rules_csv(file_name):
        """
        Parses a CSV file containing definitions for command existence flight rules.
        It identifies headers, skips blank lines, and yields validated rule objects for every row in the file.
        The function includes fallback logic to use default headers if a valid header row is not detected at the start of the file.

        :param file_name: The filesystem path to the CSV file to be read.
        :type file_name: pathlib.Path
        :return: A generator yielding tuples containing the row number and the parsed rule object (or None if an error occurred).
        :rtype: generator
        """
        with open(file_name) as f:
            header = None
            for row_number,csv_row in enumerate(csv.reader(f), 1):
                if len(csv_row) == 0 or ''.join(csv_row) == '':
                    # Skip blank lines entirely
                    continue
                # Parse header if we haven't already
                if header is None:
                    if set(csv_row) == set(DEFAULT_HEADER):
                        header = csv_row
                        continue
                    else:
                        print(
                                f"Warning! Command existence rules file {file_name} does not have a valid header."
                                f" Assuming the default column layout: {','.join(DEFAULT_HEADER)}")
                        header = DEFAULT_HEADER

                if len(csv_row) != len(header):
                    print(f"Warning! Row {row_number} of {file_name} is not consistent with the file header. Skipping...")
                    yield (row_number, None)
                    continue

                command = csv_row[header.index('Command_Stem')]
                rule_name = csv_row[header.index('FR_ID')]
                rule_version = csv_row[header.index('FR_Version')]
                level = FRState[csv_row[header.index('Alert_Level')]]
                message = csv_row[header.index('Message')]

                yield (row_number, _CommandExistenceRule(command, rule_name, rule_version, level, message))


    @staticmethod
    def append_to_description(fr_check_info: FRCheckInfo, additional_description: str) -> FRCheckInfo:
        """
        Utility method to augment the description field of an existing flight rule check information object.
        It ensures proper spacing between existing text and the new content while maintaining the immutability of the original NamedTuple.
        This is used to build complex, multi-part descriptions that explain both the rule's intent and its operational severity.

        :param fr_check_info: The existing check information object to be updated.
        :type fr_check_info: FRCheckInfo
        :param additional_description: The string content to append to the rule's description.
        :type additional_description: str
        :return: A new FRCheckInfo instance with the extended description string.
        :rtype: FRCheckInfo
        """
        if not fr_check_info.flight_rule_description.endswith(" "):
            additional_description = " " + additional_description
        return FRCheckInfo(
                flight_rule_id=fr_check_info.flight_rule_id,
                flight_rule_version=fr_check_info.flight_rule_version,
                flight_rule_description=fr_check_info.flight_rule_description + additional_description,
                criticality=fr_check_info.criticality,
                state=fr_check_info.state,
                num_violations=fr_check_info.num_violations,
                results=fr_check_info.results)


@dataclass
class _CommandExistenceRule:
    """
    An internal data container for the criteria that define a single command existence flight rule.
    It stores the target command stem, metadata for identifying the rule, and the severity level to apply if the command is found.
    This class simplifies the management of rule parameters during the parsing and evaluation phases.
    """
    command: str
    rule_name: str
    rule_version: str
    level: str
    message: str