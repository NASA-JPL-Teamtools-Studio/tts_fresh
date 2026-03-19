import pathlib
import shutil
import os
import json
from dataclasses import dataclass
from tts_fresh.check_frs import check_frs_from_file
from tts_fresh.utils.step_utils import get_steps
from tts_fresh.fresh_io.seqjson_io import seqjson_to_seqdict
from tts_fresh.seqdict import SeqDict, SeqStep
from tts_fresh.mission_config import get_io_method, get_seq_file_extension, get_default_config_file_path, get_testing_cmd_dict_path


@dataclass
class CliArgs:
    '''Test stub, duplicating the interface of the argparser object when using the CLI.'''
    input_file: pathlib.Path
    output_file: pathlib.Path
    config_file: pathlib.Path
    verbose: bool
    quiet: bool

    @staticmethod
    def default_for_test(test_file: str, seq_file_pattern=None) -> "CliArgs":
        '''
        Builds a default CliArgs object for a test case with one config file and one sequence file.

        The expected, portable way to call this method is CliArgs.default_for_test(__file__).
        '''
        test_dir = pathlib.Path(test_file).absolute().parent
        if seq_file_pattern is None:
            seq_file_pattern = get_seq_file_extension()

        seq_files = list(test_dir.glob(seq_file_pattern))
        assert len(seq_files) == 1, f'Test directory contains {len(seq_files)} sequence files matching pattern "{seq_file_pattern}", but default setup expects 1.'
        seq_file = seq_files[0]

        out_dir = test_dir.joinpath('out')
        if out_dir.is_dir():
            shutil.rmtree(out_dir)
        out_dir.mkdir(exist_ok=True)

        test_config_files = [f for f in test_dir.glob('*.json') if f != seq_file]
        assert len(test_config_files) <= 1, f'Test directory contains {len(test_config_files)} config .json files, but default setup expects at most 1.'
        if len(test_config_files) == 1:
            test_config_file = test_config_files[0]
        else:
            #TODO: consider making this diffent per mission
            default_config_file = get_default_config_file_path()
            test_config_info = {
                'command_existence_rule_files': [],
                'command_timing_rule_files': [],
                'command_argument_rule_files': []
            }
            test_config_file = out_dir.joinpath("test_config.json")
            with default_config_file.open('r') as f:
                default_config_info = json.load(f)
            for k in test_config_info:
                # For each file in default config, copy that path to the test config.
                # However, paths in a config are relative to that config file's location.
                # So, locate the file absolutely by joining it to the default config location,
                # then save it relative to the location of the test config (the out dir).
                test_config_info[k] = [
                    str(os.path.relpath(default_config_file.parent.joinpath(r).resolve(), out_dir))
                    for r in default_config_info[k]
                ]

            test_config_info['command_dictionary_path'] = str(get_testing_cmd_dict_path())
            with test_config_file.open('w') as c:
                json.dump(test_config_info, c, indent=4)

        output_file = out_dir.joinpath('fresh_report.json')
        if output_file.is_file():
            output_file.unlink()

        return CliArgs(
                input_file=seq_file,
                output_file=output_file,
                config_file=test_config_file,
                verbose=False,
                quiet=False)
    
    @staticmethod
    def custom_for_test(test_file: str, sequence_file, report_file, out_dir) -> "CliArgs":
        '''
        Builds a CliArgs object for a test case with the default config file, and given seq json and output files.

        The expected, portable way to call this method is CliArgs.default_for_test(__file__, sequence_file, report_file).
        '''

        default_config_file = get_default_config_file_path()
        test_config_info = {
            'command_existence_rule_files': [],
            'command_timing_rule_files': [],
            'command_argument_rule_files': []
        }
        test_config_file = out_dir.joinpath("test_config.json")
        with default_config_file.open('r') as f:
            default_config_info = json.load(f)
        for k in test_config_info:
            # For each file in default config, copy that path to the test config.
            # However, paths in a config are relative to that config file's location.
            # So, locate the file absolutely by joining it to the default config location,
            # then save it relative to the location of the test config (the out dir).
            test_config_info[k] = [
                str(os.path.relpath(default_config_file.parent.joinpath(r).resolve(), out_dir))
                for r in default_config_info[k]
            ]
        test_config_info['command_dictionary_path'] = get_testing_cmd_dict_path()
        with test_config_file.open('w') as c:
            json.dump(test_config_info, c, indent=4)

        return CliArgs(
                input_file=sequence_file,
                output_file=report_file,
                config_file=test_config_file,
                verbose=False,
                quiet=False)


def run_results_only_test(test_file: str, fr_id: str, steps_by_state: dict, seq_file_pattern=None) -> "tuple[dict, dict]":
    '''
    Runs a simple test (see run_simple_test), and checks that the results for flight rule fr_id match steps_by_state (see match_steps_by_state).

    This can be used as an all-in-one test method when only the result state for each step needs to be checked, or as the first step in a more comprehensive test.

    Returns a tuple of two values:
    1. The result of match_steps_by_state, a dictionary with the same structure as steps_by_state, where step numbers are replaced by the matching result objects.
    2. The seq_dict
    '''
    _,criticality,_ = fr_id.split('-')
    criticality_category = ('CAT_' + criticality) if criticality in {'A', 'B', 'C'} else 'GUIDELINE'
    report, seq_dict = run_simple_test(test_file, seq_file_pattern=seq_file_pattern)
    fr_report = report['fr_checks'][criticality_category][fr_id]
    results = match_steps_by_state(fr_report['results'], steps_by_state)
    return results, seq_dict


def run_simple_test(test_file: str, seq_file_pattern=None) -> "tuple[dict, dict]":
    '''
    Runs the test described by CliArgs.default_for_test(test_file), and returns a tuple of the report generated by that run and the SeqDict object.

    The expected, portable way to call this method is run_simple_test(__file__) from a test file in the same directory as your test inputs.
    '''
    args = CliArgs.default_for_test(test_file, seq_file_pattern=seq_file_pattern)
    return run_test(args)


def run_test(args: CliArgs) -> "tuple[dict, dict]":
    '''
    Runs the test described by args, and returns a tuple of the report generated by that run and the SeqDict object.
    '''

    check_frs_from_file(
        io_method=get_io_method(), 
        input_file=args.input_file, 
        output_file=args.output_file, 
        config_file=args.config_file,
        verbose=args.verbose,
        quiet=args.quiet
    )

    report_file = args.output_file
    with open(report_file) as f:
        report = json.load(f)

    seq_file = args.input_file

    #TODO: I think we can do better here if we unify the way 
    #dotseq_io and seqjson_io work, but for now this
    #should do the trick.
    from tts_fresh.mission import MISSION
    if MISSION == 'EURC':
        config = None
    elif MISSION == 'NISAR':
        config = json.load(open(args.config_file))
    else:
        raise ValueError(f'{MISSION} is not known to FRESH.')

    seq_dict = get_io_method()(seq_file, config=config)

    steps = get_steps(seq_dict)
    # Check that the report is internally consistent, and consistent with the sequence.
    for criticality,criticality_section in report['fr_checks'].items():
        # Only these values are supported for criticality
        assert criticality in {'CAT_A', 'CAT_B', 'CAT_C', 'GUIDELINE'}

        for fr_id, fr_report in criticality_section.items():
            assert fr_report['flight_rule_id'] == fr_id
            assert fr_report['criticality'] == criticality

            fr_state = fr_report['state']
            results = fr_report['results']

            # The reported number of violations agrees with the counted number of violations
            num_violated = sum(1 for result in results if result['state'] == 'VIOLATED')
            num_flagged = sum(1 for result in results if result['state'] == 'FLAGGED')
            assert fr_report['num_violations'] == num_violated + num_flagged

            # Only these values are recognized for the state:
            assert fr_state in {'PASSED', 'VIOLATED', 'FLAGGED', 'NA', 'PENDING'}
            # The state is VIOLATED if and only if there is at least 1 VIOLATED result
            assert (fr_state == 'VIOLATED') == (num_violated >= 1)
            # The state is FLAGGED if and only if there are 0 violations and at least one FLAGGED result.
            assert (fr_state == 'FLAGGED') == (num_violated == 0 and num_flagged >= 1)
            # The state is PASSED if and only if all results PASSED
            assert (fr_state == 'PASSED') == all(result['state'] == 'PASSED' for result in results)
            # We currently don't support NA or PENDING results
            assert fr_state != 'NA'
            assert fr_state != 'PENDING'

            for result in fr_report['results']:
                assert result['flight_rule_id'] == fr_id

                step_number = result['step_number']
                if step_number == -1:
                    # Special case: Step -1 is used to run_test a failure not related to a particular step
                    assert result['command_stem'] == 'SEQUENCE'
                    assert result['command_args'] == []
                else:
                    # General case: Step number is a 1-based index of sequence steps
                    assert 1 <= step_number <= len(steps)
                    step = steps[step_number - 1]
                    assert result['command_stem'] == step.stem
                    assert step.args == result['command_args']

    return report, seq_dict


def get_step(result: dict, seq_dict: SeqDict) -> SeqStep:
    '''
    Given a single result, the json object in a report corresponding with a FRResult object, look up the corresponding step in the SeqDict object.
    '''
    step_number = result['step_number']
    assert 1 <= step_number <= len(seq_dict.steps)
    return seq_dict.steps[step_number - 1]


def get_arg(args_list: "list[SeqStep]", arg_name: str) -> object:
    try:
        return next(a.value for a in args_list if a.name == arg_name)
    except StopIteration:
        raise KeyError(f'No argument named {arg_name}')


def match_to_steps(results: "list[dict]", step_numbers: "int or [int]") -> "list[dict]":
    '''
    Attempts to match a list of results, json objects in a report corresponding with FRResult objects, to step numbers.

    Attempts to match one result object to each step number. Duplicate step numbers will be matched to different results.

    Fails if there is not a result for each step number, or if there is not a step number for one of the results.

    If step_numbers is an integer n, this is equivalent to [1, 2, ..., n].

    Returns the matching results, in the same order as the given step numbers.
    '''
    if isinstance(step_numbers, int):
        step_numbers = list(range(1, step_numbers + 1))

    # Shallow copy the results so we can modify them
    results = list(results)
    matches = []
    for step_number in step_numbers:
        k, match = next(((k, r) for k, r in enumerate(results) if r['step_number'] == step_number), (None, None))
        # Assert that there is a match for step_number
        assert match is not None, f'There was no matching result for step {step_number}'
        matches.append(match)
        del results[k]
    # Assert that all results were matched
    assert len(results) == 0, f"There were unmatched results for step(s) {', '.join(str(r['step_number']) for r in results)}"
    return matches


def assert_all_steps_have_state(state: str, fr_report: dict, steps_or_seq_dict: "list[int] or SeqDict") -> None:
    '''
    Assert for a given flight rule that all steps in a sequence have a single result, and that result has the given state.

    If steps_or_seq_dict is a list of integers, will match results for those step numbers. If it is a SeqDict, will match results for every step in that seq.json.
    '''
    if isinstance(steps_or_seq_dict, SeqDict):
        steps_or_seq_dict = list(range(1, len(get_steps(steps_or_seq_dict)) + 1))

    # First assert there is exactly one result per step
    matched_results = match_to_steps(fr_report['results'], steps_or_seq_dict)
    for result in matched_results:
        assert state == result['state']


def match_steps_by_state(results: "list[dict]", steps_by_state: dict) -> dict:
    '''
    Attempts to match a list of results, json objects in a report corresponding with FRResult objects, to step numbers and expected states.

    Attempts to match one result object to each (step number, expected state) pair. Duplicate step numbers will be matched to different results.

    Fails if there is not a result for each (step number, expected state) pair, or if there is not a pair for one of the results.

    steps_by_state should be a dictionary from expected state to a list of step numbers expected to have that state.

    Returns a dictionary with the same structured as steps_by_state, with each step number replaced by the matching result.
    '''
    # Shallow-copy results so we can modify this version safely
    results = list(results)
    results_by_state = {}
    for state, step_numbers in steps_by_state.items():
        results_by_state[state] = []
        for step_number in step_numbers:
            k, match = next(((k,r) for k, r in enumerate(results) if r['step_number'] == step_number and state == r['state']), (None, None))
            assert match is not None, f'There was no result for step {step_number} with state {state}'
            results_by_state[state].append(match)
            del results[k]
    # Assert all results were matched
    assert len(results) == 0, f"There were unmatched results for step(s) {', '.join(str(r['step_number']) for r in results)}"
    return results_by_state

