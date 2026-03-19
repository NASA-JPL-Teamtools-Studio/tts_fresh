import pytest
from tts_fresh.test.test_utils import run_simple_test

def test_one_rule_multi_warnings():
    report,seq_json = run_simple_test(__file__)

    rule_result = report['fr_checks']['CAT_A']['TEST_CEFR-A-0004']
    assert rule_result['flight_rule_version'] == '1'
    # Description for the flight rule should mention all relevant information
    assert 'CMD_THAT_SHOULD_NOT_BE_HERE' in rule_result['flight_rule_description']
    assert 'WARNING' in rule_result['flight_rule_description']
    rule_message = 'Test flight rule for command existence flight rule checker.'
    assert rule_message in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 3

    result = rule_result['results'][0]
    assert result['state'] == 'FLAGGED'
    assert result['step_number'] == 2
    assert result['message'] == rule_message

    result = rule_result['results'][1]
    assert result['state'] == 'FLAGGED'
    assert result['step_number'] == 3
    assert result['message'] == rule_message

    result = rule_result['results'][2]
    assert result['state'] == 'FLAGGED'
    assert result['step_number'] == 5
    assert result['message'] == rule_message

