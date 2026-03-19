import pytest
from tts_fresh.test.test_utils import run_results_only_test


def test_a_0401_cmd_follows():
    single_step_test('TEST-A-0401', 'PASSED', 2)

def test_a_0402_cmd_follows():
    single_step_test('TEST-A-0402', 'VIOLATED', 2)

def test_a_0403_cmd_follows():
    single_step_test('TEST-A-0403', 'VIOLATED', 3)

def test_a_0404_cmd_follows():
    single_step_test('TEST-A-0404', 'PASSED', 4)

def test_a_0405_cmd_follows():
    single_step_test('TEST-A-0405', 'VIOLATED', 1)

def test_a_0406_cmd_follows():
    single_step_test('TEST-A-0406', 'PASSED', 4)

def test_a_0407_cmd_follows():
    single_step_test('TEST-A-0407', 'VIOLATED', 5)

def test_a_0408_cmd_follows():
    single_step_test('TEST-A-0408', 'VIOLATED', 1)

def test_a_0409_cmd_follows():
    single_step_test('TEST-A-0409', 'VIOLATED', 5)

def test_a_0410_cmd_follows():
    single_step_test('TEST-A-0410', 'PASSED', 6)

def test_a_0411_cmd_follows():
    single_step_test('TEST-A-0411', 'VIOLATED', 7)

def test_a_0412_cmd_follows():
    single_step_test('TEST-A-0412', 'VIOLATED', 1)

def test_a_0413_cmd_follows():
    run_results_only_test(__file__, 'TEST-A-0413', {})

def test_a_0414_cmd_follows():
    single_step_test('TEST-A-0414', 'VIOLATED', 7)
    
def test_a_0415_cmd_follows():
    single_step_test('TEST-A-0415', 'VIOLATED', 1)

def test_a_0416_cmd_follows():
    run_results_only_test(__file__, 'TEST-A-0416', {
        'PASSED': [9],
        'VIOLATED': [10]
    })

def single_step_test(fr_id, state, step_number):
    results, seq_json = run_results_only_test(__file__, fr_id, {state: [step_number]})
    return results[state][0]

