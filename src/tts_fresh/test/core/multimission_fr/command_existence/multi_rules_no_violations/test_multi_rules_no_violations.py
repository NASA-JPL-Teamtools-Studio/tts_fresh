import pytest
from tts_fresh.test.test_utils import run_simple_test

def test_multi_rules_no_violations():
    report,seq_json = run_simple_test(__file__)

    rule_result = report['fr_checks']['CAT_A']['TEST_CEFR-A-0001']
    assert rule_result['flight_rule_version'] == '4'
    # Description for the flight rule should mention all relevant information
    assert 'CMD_NOT_IN_SEQUENCE' in rule_result['flight_rule_description']
    assert 'ERROR' in rule_result['flight_rule_description']
    assert 'Test flight rule for command existence flight rule checker.' in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 0

    rule_result = report['fr_checks']['CAT_A']['TEST_CEFR-A-0002']
    assert rule_result['flight_rule_version'] == '2'
    # Description for the flight rule should mention all relevant information
    assert 'OTHER_CMD_NOT_IN_SEQUENCE' in rule_result['flight_rule_description']
    assert 'WARNING' in rule_result['flight_rule_description']
    assert 'Different test flight rule for command existence flight rule checker.' in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 0

    rule_result = report['fr_checks']['CAT_B']['TEST_CEFR-B-0003']
    assert rule_result['flight_rule_version'] == '1'
    # Description for the flight rule should mention all relevant information
    assert 'FINAL_CMD_NOT_IN_SEQUENCE' in rule_result['flight_rule_description']
    assert 'ERROR' in rule_result['flight_rule_description']
    assert 'Final test flight rule for command existence flight rule checker.' in rule_result['flight_rule_description']

    assert len(rule_result['results']) == 0
