import pytest
from tts_fresh.test.test_utils import run_simple_test

def test_one_rule_multi_cmds():
    report,seq_json = run_simple_test(__file__)

    rule_result = report['fr_checks']['CAT_A']['TEST_CEFR-A-0004']
    assert rule_result['flight_rule_version'] == '1'
    # Description for the flight rule should mention all relevant information
    assert 'FIRST_CMD_THAT_SHOULD_NOT_BE_HERE' in rule_result['flight_rule_description']
    assert 'SECOND_CMD_THAT_SHOULD_NOT_BE_HERE' in rule_result['flight_rule_description']
    assert 'THIRD_CMD_THAT_SHOULD_NOT_BE_HERE' in rule_result['flight_rule_description']
    assert 'ERROR' in rule_result['flight_rule_description']
    first_message = 'First test message.'
    second_message = 'Second test message.'
    third_message = 'Third test message.'
    assert first_message in rule_result['flight_rule_description']
    assert second_message in rule_result['flight_rule_description']
    assert third_message in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 3

    # Individual violations should only have the message associated with that particular command

    result = rule_result['results'][0]
    assert result['state'] == 'VIOLATED'
    assert result['step_number'] == 2
    assert result['message'] == first_message

    result = rule_result['results'][1]
    assert result['state'] == 'VIOLATED'
    assert result['step_number'] == 3
    assert result['message'] == second_message

    result = rule_result['results'][2]
    assert result['state'] == 'VIOLATED'
    assert result['step_number'] == 5
    assert result['message'] == third_message

