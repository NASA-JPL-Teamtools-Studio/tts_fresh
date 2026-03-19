import pytest
import pathlib

try:
    from importlib.metadata import version
except ImportError:
    #for Pyhton versions older than 3.7
    from importlib_metadata import version

from datetime import datetime
from tts_fresh.flightrules.fr_base import FRBase, FRCheckInfo, FRCriticality, FRResult, FRState
from tts_fresh.check_frs import _is_fr_class
from tts_fresh.fresh_io.seqjson_io import seqjson_to_dict
from tts_fresh.fresh_io.report_io import make_json_dict_from_results

TEST_DIR = pathlib.Path(__file__).absolute().parent
TEST_FILE = TEST_DIR.joinpath('test.seq.json')

LIBRARY_NAME = "tts-fresh"

class FR_TESTA0001_checker(FRBase):
    def check_fr(sequence: dict, extras: dict) -> FRCheckInfo:
        result_info = FRCheckInfo(
            flight_rule_id="TEST-A-0001", 
            flight_rule_version="0",
            flight_rule_description="a testing flight rule", 
            criticality=FRCriticality.CAT_A, 
            state=FRState.VIOLATED, 
            num_violations=1,
            results=[
                FRResult(
                    state=FRState.VIOLATED,
                    step_number=-1,
                    command_stem="ANY",
                    command_args=[],
                    flight_rule_id="TEST-A-0001",
                    message="this rule will always fail"
                )
            ])
        return result_info
    
class FRNot():
    def check_fr(sequence: dict, extras: dict) -> FRCheckInfo:
        result_info = FRCheckInfo(
            flight_rule_id="TEST-A-0001", 
            flight_rule_version="0",
            flight_rule_description="a testing flight rule", 
            criticality=FRCriticality.CAT_A, 
            state=FRState.VIOLATED, 
            num_violations=1,
            results=[
                FRResult(
                    state=FRState.VIOLATED,
                    step_number=-1,
                    command_stem="ANY",
                    command_args=[],
                    flight_rule_id="TEST-A-0001",
                    message="this rule will always fail"
                )
            ])
        return result_info
    
class ThisIsSomethingElse():
    def __init__(self) -> None:
        pass


def test_is_fr_class() -> None:
    assert _is_fr_class("TESTA0001_checker", FR_TESTA0001_checker)
    assert not(_is_fr_class("FRBase", FRBase))
    assert not(_is_fr_class("FRCheckInfo", FRCheckInfo))
    assert not(_is_fr_class("FRCriticality", FRCriticality))
    assert not(_is_fr_class("FRResult", FRResult))
    assert not(_is_fr_class("FRState", FRState))
    assert not(_is_fr_class("pytest", pytest))
    assert not(_is_fr_class("FRNot", FRNot))
    assert not(_is_fr_class("ThisIsSomethingElse", ThisIsSomethingElse))


def test_make_jsondict_from_results():
    result = FR_TESTA0001_checker().check_fr(seqjson_to_dict(TEST_FILE))
    test_now = datetime.now().isoformat()
    assert make_json_dict_from_results([result], "test", test_now, False) == {
        'metadata': {'fresh_version': version(LIBRARY_NAME), 'run_creation_time': test_now},
          'summary': {'rules_checked': 1, 'rules_flagged': 0, 'rules_passed': 0, 'rules_violated': 1, 'seqId': 'test', 'violation_locations': ['TEST-A-0001: step -1']},
          'fr_checks': {'CAT_A': {'TEST-A-0001': {
          'criticality': 'CAT_A', 
          'flight_rule_description': 'a testing flight rule', 
          'flight_rule_id': 'TEST-A-0001', 
          'flight_rule_version': '0',
          'num_violations': 1,
          'results': [{
              'command_args': [],
              'step_number': -1,
              'command_stem': 'ANY',
              'flight_rule_id': 'TEST-A-0001',
              'message': 'this rule will always fail',
              'state': 'VIOLATED'
          }],
          'state': 'VIOLATED'
    }}, 'CAT_B': {}, 'CAT_C': {}, 'GUIDELINE': {}}}
    assert make_json_dict_from_results([FRCheckInfo(
        flight_rule_id="FR2",
        flight_rule_version="22",
        flight_rule_description="two",
        criticality=FRCriticality.CAT_B,
        state=FRState.PASSED,
        num_violations=0,
        results=[]
    ), FRCheckInfo(
        flight_rule_id="FR3",
        flight_rule_version="33",
        flight_rule_description="three",
        criticality=FRCriticality.CAT_C,
        state=FRState.FLAGGED,
        num_violations=0,
        results=[]
    )], "test2", test_now, False) == {'metadata': {'fresh_version': version(LIBRARY_NAME), 'run_creation_time': test_now},
          'summary': {'rules_checked': 2, 'rules_flagged': 1, 'rules_passed': 1, 'rules_violated': 0, 'seqId': 'test2','violation_locations': []},
          'fr_checks': {'CAT_A': {}, 'CAT_B': {'FR2': {
          'criticality': 'CAT_B', 
          'flight_rule_description': 'two', 
          'flight_rule_id': 'FR2', 
          'flight_rule_version': '22',
          'num_violations': 0,
          'results': [],
          'state': 'PASSED'
    }}, 'CAT_C': {'FR3': {
          'criticality': 'CAT_C', 
          'flight_rule_description': 'three', 
          'flight_rule_id': 'FR3', 
          'flight_rule_version': '33',
          'num_violations': 0,
          'results': [],
          'state': 'FLAGGED'
    }}, 'GUIDELINE': {}}}
