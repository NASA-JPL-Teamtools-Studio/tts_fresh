import pytest
from tts_fresh.test.test_utils import run_simple_test
import json

def test_all_together():
    report,seq_json = run_simple_test(__file__)

    rule_result = report['fr_checks']['CAT_A']['TEST_CEFR-A-0004']

    assert rule_result['flight_rule_version'] == '1'
    # Description for the flight rule should mention all relevant information
    assert 'CMD_THAT_SHOULD_NOT_BE_HERE' in rule_result['flight_rule_description']
    assert 'ERROR' in rule_result['flight_rule_description']
    rule_message = 'From command_existence_rules'
    assert rule_message in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 2

    result = rule_result['results'][0]
    assert result['state'] == 'VIOLATED'
    assert result['step_number'] == 2
    assert result['message'] == rule_message

    result = rule_result['results'][1]
    assert result['state'] == 'VIOLATED'
    assert result['step_number'] == 3
    assert result['message'] == rule_message

    rule_result = report['fr_checks']['CAT_A']['TEST_CEFR-A-0005']
    assert rule_result['flight_rule_version'] == '2'
    # Description for the flight rule should mention all relevant information
    assert 'ANOTHER_CMD_THAT_SHOULD_NOT_BE_HERE' in rule_result['flight_rule_description']
    assert 'WARNING' in rule_result['flight_rule_description']
    rule_message = 'From more_command_existence_rules'
    assert rule_message in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 1

    result = rule_result['results'][0]
    assert result['state'] == 'FLAGGED'
    assert result['step_number'] == 5
    assert result['message'] == rule_message

    rule_result = report['fr_checks']['CAT_B']['TEST_CEFR-B-0006']
    assert rule_result['flight_rule_version'] == '3'
    # Description for the flight rule should mention all relevant information
    assert 'CMD_NOT_IN_SEQUENCE' in rule_result['flight_rule_description']
    assert 'ERROR' in rule_result['flight_rule_description']
    rule_message = 'From more_command_existence_rules'
    assert rule_message in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 0

    rule_result = report['fr_checks']['CAT_C']['TEST_CEFR-C-0007']
    assert rule_result['flight_rule_version'] == '4'
    # Description for the flight rule should mention all relevant information
    assert 'YET_ANOTHER_CMD_THAT_SHOULD_NOT_BE_HERE' in rule_result['flight_rule_description']
    assert 'WARNING' in rule_result['flight_rule_description']
    rule_message = 'From even_more_command_existence_rules'
    assert rule_message in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 1

    result = rule_result['results'][0]
    assert result['state'] == 'FLAGGED'
    assert result['step_number'] == 7
    assert result['message'] == rule_message
