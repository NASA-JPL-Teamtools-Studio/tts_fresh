import importlib, inspect, pkgutil
import os.path
import json
import pathlib

import tts_fresh.fresh_io.report_io
import tts_fresh.flightrules.core as flightrules_core
from tts_fresh.flightrules.fr_base import FRBase, FRCheckInfo, FRState
from tts_fresh.seqdict import SeqDict
import tts_fresh.mission_config as mission_config


def _eval_fr(fr_class_ref, sequence, config, verbose) -> FRCheckInfo:
    """
    Evaluates a single flight rule class against the provided sequence.
    
    This helper function invokes the check_fr method of a flight rule class and,
    if verbose mode is enabled, immediately prints any violated rules to the console.

    :param fr_class_ref: A reference to the flight rule class (subclass of FRBase) to evaluate.
    :param sequence: The sequence dictionary containing spacecraft commands.
    :type sequence: SeqDict
    :param config: A dictionary containing configuration parameters for the rules.
    :type config: dict
    :param verbose: If True, details of failed rules are printed to stdout.
    :type verbose: bool
    :return: An object containing the aggregated results of the flight rule check.
    :rtype: FRCheckInfo
    """
    if issubclass(fr_class_ref, FRBase):
        results = fr_class_ref.check_fr(sequence, config)
    for result in results:
        if (result.state == FRState.VIOLATED) and verbose:
            for v in result.results:
                print (v.to_string())  # immediately print failed rules to console
    return results

def _is_fr_class(fr_class_name: str, fr_class_ref) -> bool:
    """
    Determines if a class is a valid flight rule checker.

    Filters out base classes, non-FRBase subclasses, and private classes to identify 
    executable flight rule implementations.

    :param fr_class_name: The name of the class being inspected.
    :type fr_class_name: str
    :param fr_class_ref: A reference to the class object.
    :return: True if the class is a valid flight rule implementation, False otherwise.
    :rtype: bool
    """
    try:
        return fr_class_name not in ["FRBase", "FRCheckInfo"] and issubclass(fr_class_ref, FRBase) and not fr_class_name.startswith("_")
    except TypeError as e:
        if fr_class_name.startswith("FR"):  # if the class starts with FR then it is probably a broken FR
            print (f'{fr_class_name} is not properly formatted and could not be evaluated. Error: {e}')
            return False
        else:  # otherwise we are probably catching imports, this is left for debugging
            return False

def check_frs_from_file(io_method, 
                       input_file, 
                       output_file=None, 
                       config_file=pathlib.Path.joinpath(pathlib.Path(__file__).absolute().parent, "config/default_config.json"), 
                       verbose=False, 
                       quiet=False
        ) -> None:
    """
    Main entry point to run flight rule checks on a sequence file and generate a report.

    This function loads configuration, parses the sequence file using the provided IO method, 
    executes all discovered flight rules, and writes the final JSON report.

    :param io_method: A function used to parse the input file into a SeqDict.
    :type io_method: callable
    :param input_file: The path to the sequence file to be checked.
    :type input_file: pathlib.Path
    :param output_file: Custom path to save the JSON report.
    :type output_file: pathlib.Path, optional
    :param config_file: Path to the JSON configuration file.
    :type config_file: pathlib.Path
    :param verbose: If True, enables detailed console logging during execution.
    :type verbose: bool
    :param quiet: If True, suppresses individual 'PASSED' results in the final report.
    :type quiet: bool
    :return: None
    """
    config = {}

    with open(config_file) as f:
        config = json.load(f)
    # Add the config directory to the config, in case FR checkers need to resolve paths relative to the config file.
    config['config_dir'] = os.path.dirname(config_file)

    #use io class here to read sequence file
    sequence = io_method(input_file, config)

    # get results
    fr_results = check_flight_rules(sequence, config, verbose)

    # write report
    tts_fresh.fresh_io.report_io.write_fresh_json_report(sequence, fr_results, output_file, quiet)

def check_flight_rules(sequence: SeqDict, 
                       config: dict,
                       verbose=False) -> "list[FRCheckInfo]":
    """
    Discovers and executes all applicable flight rules for the current mission.

    Iterates through both 'core' flight rule modules and mission-specific modules 
    defined in the mission configuration. It dynamically imports these modules 
    and evaluates any valid flight rule classes found within.

    :param sequence: The sequence dictionary to validate.
    :type sequence: SeqDict
    :param config: The configuration dictionary.
    :type config: dict
    :param verbose: If True, prints violation details to the console.
    :type verbose: bool
    :return: A list of result objects for every evaluated flight rule.
    :rtype: list[FRCheckInfo]
    """
    # get all modules in the flightrules folder
    core_pkgpath = os.path.dirname(flightrules_core.__file__)
    fr_modules = ["core." + name for module_finder, name, ispkg in pkgutil.iter_modules([core_pkgpath])]
    mission_package = mission_config.import_mission_fr_folder()
    if mission_package is not None:
        mission_pkgpath = os.path.dirname(mission_package.__file__)
        fr_modules += [mission_package.__name__ + "." + name for module_finder, name, ispkg in pkgutil.iter_modules([mission_pkgpath])] 
    fr_results = []

    # check every flightrules module (except for fr_base) to see if it is actually a flight rule
    # if it is, evaluate it and add its results to fr_results
    for fr_file_name in fr_modules:
        if (fr_file_name != "fr_base"):
            if fr_file_name.startswith('core'):
                fr_module = importlib.import_module("tts_fresh.flightrules."+fr_file_name)
            else:
                fr_module = importlib.import_module(fr_file_name)
            for fr_class in inspect.getmembers(fr_module):
                fr_class_name = fr_class[0]
                fr_class_ref = getattr(fr_module, fr_class_name)
                if _is_fr_class(fr_class_name, fr_class_ref):
                    fr_results += _eval_fr(fr_class_ref, sequence, config, verbose)

    # return results as a list of FRCheckInfo objects
    return fr_results