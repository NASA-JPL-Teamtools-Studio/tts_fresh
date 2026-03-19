import pytest
from tts_fresh.test.test_utils import run_simple_test

def test_invalid_csv():
    report,seq_json = run_simple_test(__file__)

    rule_result = report['fr_checks']['CAT_A']['COMMAND_EXISTENCE_FLIGHT_RULES_CHECKER-A-0000']
    assert rule_result['state'] == "VIOLATED"
    # Only one line in the file we give is invalid
    assert rule_result['num_violations'] == 1
    
