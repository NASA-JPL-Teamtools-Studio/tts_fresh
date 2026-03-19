import pytest
from tts_fresh.test.test_utils import run_results_only_test

def test_a_0401_cmd_overlaps():
    run_results_only_test(__file__, 'TEST-A-0401', {
        'PASSED': [1, 3, 7, 8]
    })

def test_a_0402_cmd_overlaps():
    run_results_only_test(__file__, 'TEST-A-0402', {
        'PASSED': [1, 3, 4, 7, 8],
        'VIOLATED': [2],
    })

def test_a_0403_cmd_overlaps():
    run_results_only_test(__file__, 'TEST-A-0403', {
        'PASSED': [1, 3, 5, 7, 8]
    })

def test_a_0404_cmd_overlaps():
    run_results_only_test(__file__, 'TEST-A-0404', {
        'PASSED': [1, 3, 7, 8]
    })

def test_a_0405_cmd_overlaps():
    run_results_only_test(__file__, 'TEST-A-0405', {
        'PASSED': [2, 4],
        'VIOLATED': [5],
    })

def test_a_0406_cmd_overlaps():
    run_results_only_test(__file__, 'TEST-A-0406', {
        'PASSED': [2, 4],
        'VIOLATED': [6],
    })

