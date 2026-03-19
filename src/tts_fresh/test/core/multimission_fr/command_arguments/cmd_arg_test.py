import pytest
from tts_fresh.test.test_utils import run_simple_test

def test_a_0301_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_a_0301 = report['fr_checks']['CAT_A']['TEST-A-0301']
    assert test_a_0301['state'] == 'VIOLATED'
    assert len(test_a_0301['results']) == 2
    assert test_a_0301['results'][0]['state'] == 'VIOLATED'
    assert test_a_0301['results'][0]['step_number'] == 1
    assert test_a_0301['results'][1]['state'] == 'VIOLATED'
    assert test_a_0301['results'][1]['step_number'] == 2

def test_a_0302_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_a_0302 = report['fr_checks']['CAT_A']['TEST-A-0302']
    assert test_a_0302['state'] == 'VIOLATED'
    assert len(test_a_0302['results']) == 2
    assert test_a_0302['results'][0]['state'] == 'VIOLATED'
    assert test_a_0302['results'][0]['step_number'] == 1
    assert test_a_0302['results'][1]['state'] == 'VIOLATED'
    assert test_a_0302['results'][1]['step_number'] == 3

def test_b_0303_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_b_0303 = report['fr_checks']['CAT_B']['TEST-B-0303']
    assert test_b_0303['state'] == 'VIOLATED'
    assert len(test_b_0303['results']) == 2
    assert test_b_0303['results'][0]['state'] == 'VIOLATED'
    assert test_b_0303['results'][0]['step_number'] == 2
    assert test_b_0303['results'][1]['state'] == 'VIOLATED'
    assert test_b_0303['results'][1]['step_number'] == 3

def test_c_0304_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_c_0304 = report['fr_checks']['CAT_C']['TEST-C-0304']
    assert test_c_0304['state'] == 'VIOLATED'
    assert len(test_c_0304['results']) == 1
    assert test_c_0304['results'][0]['state'] == 'VIOLATED'
    assert test_c_0304['results'][0]['step_number'] == 1

def test_a_0305_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_a_0305 = report['fr_checks']['CAT_A']['TEST-A-0305']
    assert test_a_0305['state'] == 'VIOLATED'
    assert len(test_a_0305['results']) == 2
    assert test_a_0305['results'][0]['state'] == 'VIOLATED'
    assert test_a_0305['results'][0]['step_number'] == 2
    assert test_a_0305['results'][1]['state'] == 'VIOLATED'
    assert test_a_0305['results'][1]['step_number'] == 3

def test_a_0306_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_a_0306 = report['fr_checks']['CAT_A']['TEST-A-0306']
    assert test_a_0306['state'] == 'FLAGGED'
    assert len(test_a_0306['results']) == 1
    assert test_a_0306['results'][0]['state'] == 'FLAGGED'
    assert test_a_0306['results'][0]['step_number'] == 3

def test_a_0307_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_a_0307 = report['fr_checks']['CAT_A']['TEST-A-0307']
    assert test_a_0307['state'] == 'VIOLATED'
    assert len(test_a_0307['results']) == 2
    assert test_a_0307['results'][0]['state'] == 'VIOLATED'
    assert test_a_0307['results'][0]['step_number'] == 1
    assert test_a_0307['results'][1]['state'] == 'VIOLATED'
    assert test_a_0307['results'][1]['step_number'] == 3

def test_a_0308_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    test_a_0308 = report['fr_checks']['CAT_A']['TEST-A-0308']
    assert test_a_0308['state'] == 'VIOLATED'
    assert len(test_a_0308['results']) == 2
    assert test_a_0308['results'][0]['state'] == 'VIOLATED'
    assert test_a_0308['results'][0]['step_number'] == 1
    assert test_a_0308['results'][1]['state'] == 'VIOLATED'
    assert test_a_0308['results'][1]['step_number'] == 2

def test_sm_a_0001_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    sm_a_0001 = report['fr_checks']['CAT_A']['SM-A-0001']
    assert sm_a_0001['state'] == 'VIOLATED'
    assert len(sm_a_0001['results']) == 4
    assert sm_a_0001['results'][0]['state'] == 'VIOLATED'
    assert sm_a_0001['results'][0]['step_number'] == 5
    assert sm_a_0001['results'][1]['state'] == 'VIOLATED'
    assert sm_a_0001['results'][1]['step_number'] == 6
    assert sm_a_0001['results'][2]['state'] == 'VIOLATED'
    assert sm_a_0001['results'][2]['step_number'] == 7
    assert sm_a_0001['results'][3]['state'] == 'VIOLATED'
    assert sm_a_0001['results'][3]['step_number'] == 8

def test_avs_a_0010_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    avs_a_0010 = report['fr_checks']['CAT_A']['AVS-A-0010']
    assert avs_a_0010['state'] == 'VIOLATED'
    assert len(avs_a_0010['results']) == 2
    assert avs_a_0010['results'][0]['state'] == 'VIOLATED'
    assert avs_a_0010['results'][0]['step_number'] == 10
    assert avs_a_0010['results'][1]['state'] == 'VIOLATED'
    assert avs_a_0010['results'][1]['step_number'] == 13

def test_pwr_a_0009_cmd_arg():
    report, seq_json = run_simple_test(__file__)

    pwr_a_0009 = report['fr_checks']['CAT_A']['PWR-A-0009']
    assert pwr_a_0009['state'] == 'VIOLATED'
    assert len(pwr_a_0009['results']) == 2
    assert pwr_a_0009['results'][0]['state'] == 'VIOLATED'
    assert pwr_a_0009['results'][0]['step_number'] == 15
    assert pwr_a_0009['results'][1]['state'] == 'VIOLATED'
    assert pwr_a_0009['results'][1]['step_number'] == 16
