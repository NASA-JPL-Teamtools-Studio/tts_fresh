# This file is a sample of how we might use Pytest to test a FR implementation.
# The basic idea is to call check_frs, passing arguments as if the CLI were being used.
# That writes the report out, which we can read in and assert on as an end-to-end test.
import pytest

from tts_fresh.check_frs import check_flight_rules
from tts_fresh.test.test_utils import run_simple_test

# the pytest marker indicates which mission (or core) this test belongs to 
def _test_a_sequence_with_a_violation():
# Leading underscore disables this test, but keeping the code as a sample to go with the corresponding sample flight rule.
    report, seq_json = run_simple_test(__file__)

    test_a_0001 = report['fr_checks']['CAT_A']['TEST-A-0001']
    assert test_a_0001['state'] == 'VIOLATED'
    assert len(test_a_0001['results']) == 1
    # etc.

