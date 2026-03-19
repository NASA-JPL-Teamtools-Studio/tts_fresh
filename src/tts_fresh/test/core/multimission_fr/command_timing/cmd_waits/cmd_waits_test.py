import pytest
from tts_fresh.test.test_utils import run_results_only_test


def test_a_0401_cmd_waits():
    run_results_only_test(__file__, 'TEST-A-0401', {
        'PASSED': [1, 5, 6]
    })

def test_a_0402_cmd_waits():
    single_step_test('TEST-A-0402', 'PASSED', 2)

def test_a_0403_cmd_waits():
    run_results_only_test(__file__, 'TEST-A-0403', {
        'PASSED': [1, 5, 6]
    })

def test_a_0404_cmd_waits():
    single_step_test('TEST-A-0404', 'PASSED', 3)

def test_a_0405_cmd_waits():
    single_step_test('TEST-A-0405', 'VIOLATED', 4)

def test_a_0406_cmd_waits():
    run_results_only_test(__file__, 'TEST-A-0406', {
        'PASSED': [1],
        'VIOLATED': [5, 6],
    })

def test_a_0407_cmd_waits():
    run_results_only_test(__file__, 'TEST-A-0407', {
        'PASSED': [1],
        'VIOLATED': [5],
    })

def test_a_0408_cmd_waits():
    run_results_only_test(__file__, 'TEST-A-0408', {})

def single_step_test(fr_id, state, step_number):
    results, seq_json = run_results_only_test(__file__, fr_id, {state: [step_number]})
    return results[state][0]

