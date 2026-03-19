import pathlib, sys
import datetime
import json

from tts_fresh.flightrules.fr_base import FRCheckInfo, FRState
from tts_fresh.seqdict import SeqDict

try:
    from importlib.metadata import version
except ImportError:
    #For Pyhton 3.7 and before
    from importlib_metadata import version

LIBRARY_NAME = "tts-fresh"

def make_json_dict_from_results(fr_results: "dict[FRCheckInfo]", sequence_name: str, now_str: str, quiet: bool) -> dict:
    """
    Converts raw flight rule check results into a structured dictionary suitable for JSON serialization. 
    It aggregates results by criticality, calculates summary statistics like the number of rules passed 
    or violated, and extracts specific locations for any detected violations. The function also handles 
    the final conversion of result objects into their dictionary representations, optionally filtering 
    out successful checks based on the quiet flag.

    :param fr_results: A collection of flight rule check results to be processed.
    :type fr_results: list[FRCheckInfo]
    :param sequence_name: The identifier or name of the command sequence that was validated.
    :type sequence_name: str
    :param now_str: An ISO-formatted string representing the creation time of the report.
    :type now_str: str
    :param quiet: A flag that determines whether to omit 'PASSED' results from the final check details.
    :type quiet: bool
    :return: A structured dictionary containing metadata, summary statistics, and detailed check results.
    :rtype: dict
    """
    report_data = {
        "metadata": {
            "fresh_version": version(LIBRARY_NAME),
            "run_creation_time": now_str
        },
        "summary": {
            "seqId": sequence_name,
            "rules_checked": 0,
            "rules_passed": 0,
            "rules_violated": 0,
            "rules_flagged": 0,
            "violation_locations": []
        },
        "fr_checks": {
            "CAT_A": {},
            "CAT_B": {},
            "CAT_C": {},
            "GUIDELINE" :{}
        }
    }
    rules_passed = 0
    rules_failed = 0
    rules_flagged = 0
    violation_locations = []
    # add results to dictionary, adding as necessary
    for fr_result_obj in fr_results:
        if fr_result_obj.flight_rule_id in report_data["fr_checks"][fr_result_obj.criticality.name].keys():
            report_data["fr_checks"][fr_result_obj.criticality.name][fr_result_obj.flight_rule_id] += fr_result_obj
        else:
            report_data["fr_checks"][fr_result_obj.criticality.name][fr_result_obj.flight_rule_id] = fr_result_obj
        if fr_result_obj.state == FRState.PASSED:
            rules_passed += 1
        elif fr_result_obj.state == FRState.FLAGGED:
            rules_flagged += 1
        else:
            rules_failed += 1
    # turn results into dicts for nice JSON
    for criticality in report_data["fr_checks"]:
        for fr in report_data["fr_checks"][criticality]:
            for result in report_data["fr_checks"][criticality][fr].results:
                if result.state == FRState.VIOLATED:
                    vloc_str = f"{result.flight_rule_id}: step {result.step_number}"
                    violation_locations.append(vloc_str)
            report_data["fr_checks"][criticality][fr] = report_data["fr_checks"][criticality][fr].to_json_dict(quiet)

    report_data["summary"]["rules_checked"] = rules_passed + rules_failed + rules_flagged
    report_data["summary"]["rules_passed"] = rules_passed
    report_data["summary"]["rules_violated"] = rules_failed
    report_data["summary"]["rules_flagged"] = rules_flagged
    report_data["summary"]["violation_locations"] = violation_locations
    pprint_output_summary(report_data["summary"])
    return report_data

def pprint_output_summary(summary) -> None:
    """
    Prints a human-readable summary of the flight rule validation results directly to the console. 
    It displays key metrics such as the total rules checked and the breakdown of passes, violations, 
    and flags to give the user immediate feedback. Additionally, it lists specific violation 
    locations to help developers quickly identify where the sequence failed validation.

    :param summary: A dictionary containing the aggregated summary data for the validation run.
    :type summary: dict
    :return: None
    :rtype: None
    """
    print (f"SEQ ID: {summary['seqId']}")
    print (f"Rules Checked: {summary['rules_checked']}")
    print (f"Rules Passed: {summary['rules_passed']}")
    print (f"Rules Violated: {summary['rules_violated']}")
    print (f"Rules Flagged: {summary['rules_flagged']}")
    print (f"Violation Locations: {summary['violation_locations']}")

def write_fresh_json_report(sequence: SeqDict, fr_results: dict, file_path: pathlib.Path, quiet) -> None:
    """
    Generates and saves a comprehensive JSON report file containing the results of all flight rule checks 
    performed on a sequence. It establishes a timestamp for the run, compiles the final report data 
    structure, and manages file I/O operations including default filename generation. The function also 
    includes error handling for file system issues to ensure the validation process exits gracefully if 
    the report cannot be saved.

    :param sequence: The parsed sequence dictionary object that was checked.
    :type sequence: SeqDict
    :param fr_results: The results of the flight rule validation to be included in the report.
    :type fr_results: list[FRCheckInfo]
    :param file_path: The filesystem path where the JSON report should be saved. If None, a default filename is generated.
    :type file_path: pathlib.Path
    :param quiet: A flag indicating whether to suppress individual passed results in the output file.
    :type quiet: bool
    :return: None
    :rtype: None
    """
    now_str = datetime.datetime.now().isoformat()
    report_data = make_json_dict_from_results(fr_results, sequence.id, now_str, quiet)    

    if file_path is None:
        file_path = sequence.id + "_" + now_str.replace(':', '-').split('.')[0].replace('-', '') + ".fresh_report.json"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(report_data, json_file, indent=4, sort_keys=False, separators=(',', ': '))
    except FileNotFoundError:
        print(f'File not found: {file_path}')
        sys.exit(1)