from tts_fresh.test.test_utils import run_simple_test
import pytest

def test_one_rule_multi_cmds():
    with pytest.raises(ValueError):
        report,seq_json = run_simple_test(__file__)
