import pytest
from tts_fresh.test.test_utils import run_results_only_test

def test_a_0401_symbol_args():
    run_results_only_test(__file__, 'TEST-A-0401', {
        'PASSED': [1, 4, 7, 10, 13, 16, 19, 22],
        'VIOLATED': [2, 5, 8, 11, 14, 17, 20, 23],
    })

def test_a_0402_symbol_args():
    run_results_only_test(__file__, 'TEST-A-0402', {
        'PASSED': [1, 4, 10],
        'VIOLATED': [2, 8, 14],
        'FLAGGED': [11, 13, 17, 19, 22, 23],
    })

def test_a_0403_symbol_args():
    run_results_only_test(__file__, 'TEST-A-0403', {
        'PASSED': [1, 4, 7, 8, 10, 16, 17],
        'VIOLATED': [2, 5, 11],
        'FLAGGED': [13, 14, 19, 20, 22, 23],
    })

def test_a_0404_symbol_args():
    run_results_only_test(__file__, 'TEST-A-0404', {
        'PASSED': [1, 4, 8, 10],
        'VIOLATED': [2],
        'FLAGGED': [11, 13, 14, 17, 19, 22, 23],
    })

def test_a_0405_symbol_args():
    run_results_only_test(__file__, 'TEST-A-0405', {
        'PASSED': [1, 4, 5, 7, 8, 10],
        'VIOLATED': [2],
        'FLAGGED': [11, 13, 14, 16, 17, 19, 20, 22, 23],
    })

