import pytest
from tts_fresh.test.test_utils import run_results_only_test


def test_a_0401_cmd_followed_by():
    single_step_test('TEST-A-0401', 'PASSED', 1)

def test_a_0402_cmd_followed_by():
    single_step_test('TEST-A-0402', 'VIOLATED', 1)

def test_a_0403_cmd_followed_by():
    single_step_test('TEST-A-0403', 'VIOLATED', 2)

def test_a_0404_cmd_followed_by():
    single_step_test('TEST-A-0404', 'PASSED', 2)

def test_a_0405_cmd_followed_by():
    single_step_test('TEST-A-0405', 'VIOLATED', 2)

def test_a_0406_cmd_followed_by():
    single_step_test('TEST-A-0406', 'PASSED', 3)

def test_a_0407_cmd_followed_by():
    single_step_test('TEST-A-0407', 'VIOLATED', 3)

def test_a_0408_cmd_followed_by():
    single_step_test('TEST-A-0408', 'VIOLATED', 3)

def test_a_0409_cmd_followed_by():
    single_step_test('TEST-A-0409', 'VIOLATED', 4)

def test_a_0410_cmd_followed_by():
    single_step_test('TEST-A-0410', 'PASSED', 4)

def test_a_0411_cmd_followed_by():
    single_step_test('TEST-A-0411', 'VIOLATED', 4)

def test_a_0412_cmd_followed_by():
    single_step_test('TEST-A-0412', 'VIOLATED', 4)

def test_a_0413_cmd_followed_by():
    run_results_only_test(__file__, 'TEST-A-0413', {})

def test_a_0414_cmd_followed_by():
    single_step_test('TEST-A-0414', 'VIOLATED', 2)

def test_a_0415_cmd_followed_by():
    single_step_test('TEST-A-0415', 'VIOLATED', 7)

def test_a_0420_cmd_followed_by():
    single_step_test('TEST-A-0420', 'PASSED', 9)

def test_a_0421_cmd_followed_by():
    single_step_test('TEST-A-0421', 'FLAGGED', 9)

def test_a_0422_cmd_followed_by():
    single_step_test('TEST-A-0422', 'FLAGGED', 9)

def test_a_0423_cmd_followed_by():
    single_step_test('TEST-A-0423', 'FLAGGED', 9)

def test_a_0424_cmd_followed_by():
    single_step_test('TEST-A-0424', 'VIOLATED', 10)

def test_a_0425_cmd_followed_by():
    single_step_test('TEST-A-0425', 'VIOLATED', 10)

def test_a_0426_cmd_followed_by():
    single_step_test('TEST-A-0426', 'VIOLATED', 10)

def test_a_0427_cmd_followed_by():
    single_step_test('TEST-A-0427', 'VIOLATED', 10)

def test_a_0430_cmd_followed_by():
    single_step_test('TEST-A-0430', 'PASSED', 9)

def test_a_0431_cmd_followed_by():
    single_step_test('TEST-A-0431', 'PASSED', 9)

def test_a_0432_cmd_followed_by():
    single_step_test('TEST-A-0432', 'PASSED', 9)

def test_a_0433_cmd_followed_by():
    single_step_test('TEST-A-0433', 'VIOLATED', 9)

def test_a_0434_cmd_followed_by():
    single_step_test('TEST-A-0434', 'FLAGGED', 9)

def test_a_0435_cmd_followed_by():
    single_step_test('TEST-A-0435', 'FLAGGED', 9)

def test_a_0436_cmd_followed_by():
    single_step_test('TEST-A-0436', 'FLAGGED', 9)

def test_a_0437_cmd_followed_by():
    single_step_test('TEST-A-0437', 'FLAGGED', 9)

def test_a_0438_cmd_followed_by():
    single_step_test('TEST-A-0438', 'VIOLATED', 11)

def test_a_0440_cmd_followed_by():
    single_step_test('TEST-A-0440', 'PASSED', 10)

def test_a_0441_cmd_followed_by():
    single_step_test('TEST-A-0441', 'PASSED', 10)

def test_a_0442_cmd_followed_by():
    single_step_test('TEST-A-0442', 'PASSED', 10)

def test_a_0443_cmd_followed_by():
    single_step_test('TEST-A-0443', 'VIOLATED', 10)

def test_a_0444_cmd_followed_by():
    single_step_test('TEST-A-0444', 'FLAGGED', 10)

def test_a_0445_cmd_followed_by():
    single_step_test('TEST-A-0445', 'FLAGGED', 10)

def test_a_0446_cmd_followed_by():
    single_step_test('TEST-A-0446', 'FLAGGED', 10)

def test_a_0447_cmd_followed_by():
    single_step_test('TEST-A-0447', 'FLAGGED', 10)

def test_a_0448_cmd_followed_by():
    single_step_test('TEST-A-0448', 'FLAGGED', 10)

def test_a_0449_cmd_followed_by():
    single_step_test('TEST-A-0449', 'VIOLATED', 12)

def test_a_0450_cmd_followed_by():
    single_step_test('TEST-A-0450', 'PASSED', 10)

def test_a_0451_cmd_followed_by():
    single_step_test('TEST-A-0451', 'PASSED', 10)

def test_a_0452_cmd_followed_by():
    single_step_test('TEST-A-0452', 'PASSED', 10)

def test_a_0453_cmd_followed_by():
    single_step_test('TEST-A-0453', 'VIOLATED', 10)

def test_a_0454_cmd_followed_by():
    single_step_test('TEST-A-0454', 'FLAGGED', 10)

def test_a_0455_cmd_followed_by():
    single_step_test('TEST-A-0455', 'FLAGGED', 10)

def test_a_0456_cmd_followed_by():
    single_step_test('TEST-A-0456', 'FLAGGED', 10)

def test_a_0457_cmd_followed_by():
    single_step_test('TEST-A-0457', 'FLAGGED', 10)

def test_a_0458_cmd_followed_by():
    single_step_test('TEST-A-0458', 'FLAGGED', 10)

def test_a_0459_cmd_followed_by():
    single_step_test('TEST-A-0459', 'VIOLATED', 13)

def test_a_0460_cmd_followed_by():
    single_step_test('TEST-A-0460', 'PASSED', 13)

def test_a_0461_cmd_followed_by():
    single_step_test('TEST-A-0461', 'PASSED', 13)

def test_a_0462_cmd_followed_by():
    single_step_test('TEST-A-0462', 'PASSED', 13)

def test_a_0463_cmd_followed_by():
    single_step_test('TEST-A-0463', 'PASSED', 13)

def test_a_0464_cmd_followed_by():
    single_step_test('TEST-A-0464', 'VIOLATED', 13)

def test_a_0465_cmd_followed_by():
    single_step_test('TEST-A-0465', 'VIOLATED', 13)

def test_a_0466_cmd_followed_by():
    single_step_test('TEST-A-0466', 'VIOLATED', 15)

def test_a_0470_cmd_followed_by():
    single_step_test('TEST-A-0470', 'PASSED', 14)

def test_a_0471_cmd_followed_by():
    single_step_test('TEST-A-0471', 'PASSED', 14)

def test_a_0472_cmd_followed_by():
    single_step_test('TEST-A-0472', 'PASSED', 14)

def test_a_0473_cmd_followed_by():
    single_step_test('TEST-A-0473', 'PASSED', 14)

def test_a_0474_cmd_followed_by():
    single_step_test('TEST-A-0474', 'VIOLATED', 14)

def test_a_0475_cmd_followed_by():
    single_step_test('TEST-A-0475', 'VIOLATED', 14)

def test_a_0476_cmd_followed_by():
    single_step_test('TEST-A-0476', 'VIOLATED', 15)

def test_a_0480_cmd_followed_by():
    single_step_test('TEST-A-0480', 'PASSED', 10)

def test_a_0481_cmd_followed_by():
    single_step_test('TEST-A-0481', 'PASSED', 10)

def test_a_0482_cmd_followed_by():
    single_step_test('TEST-A-0482', 'VIOLATED', 10)

def test_a_0483_cmd_followed_by():
    single_step_test('TEST-A-0483', 'FLAGGED', 10)

def test_a_0484_cmd_followed_by():
    single_step_test('TEST-A-0484', 'FLAGGED', 10)

def test_a_0485_cmd_followed_by():
    single_step_test('TEST-A-0485', 'FLAGGED', 10)

def test_a_0486_cmd_followed_by():
    single_step_test('TEST-A-0486', 'VIOLATED', 16)

def test_a_0490_cmd_followed_by():
    single_step_test('TEST-A-0490', 'PASSED', 16)

def test_a_0491_cmd_followed_by():
    single_step_test('TEST-A-0491', 'PASSED', 16)

def test_a_0492_cmd_followed_by():
    single_step_test('TEST-A-0492', 'PASSED', 16)

def test_a_0493_cmd_followed_by():
    single_step_test('TEST-A-0493', 'VIOLATED', 16)

def test_a_0494_cmd_followed_by():
    single_step_test('TEST-A-0494', 'VIOLATED', 16)

def test_a_0495_cmd_followed_by():
    single_step_test('TEST-A-0495', 'VIOLATED', 18)

def test_a_1400_cmd_followed_by():
    single_step_test('TEST-A-1400', 'PASSED', 15)

def test_a_1401_cmd_followed_by():
    single_step_test('TEST-A-1401', 'PASSED', 15)

def test_a_1402_cmd_followed_by():
    single_step_test('TEST-A-1402', 'PASSED', 15)

def test_a_1403_cmd_followed_by():
    single_step_test('TEST-A-1403', 'VIOLATED', 15)

def test_a_1404_cmd_followed_by():
    single_step_test('TEST-A-1404', 'FLAGGED', 15)

def test_a_1405_cmd_followed_by():
    single_step_test('TEST-A-1405', 'FLAGGED', 15)

def test_a_1406_cmd_followed_by():
    single_step_test('TEST-A-1406', 'FLAGGED', 15)

def test_a_1407_cmd_followed_by():
    single_step_test('TEST-A-1407', 'FLAGGED', 15)

def test_a_1408_cmd_followed_by():
    single_step_test('TEST-A-1408', 'VIOLATED', 20)

def test_a_1410_cmd_followed_by():
    # Note - This should probably be FLAGGED rather than VIOLATED.
    # Currently, we compute a result for the linear portion of a sequence,
    # then merge in a result for the nonlinear portion.
    # This can only escalate severity, to be conservative.
    # Since there's no matching command in the linear portion, that's a violation,
    # even though the nonlinear portion maybe should de-escalate this to just a flag.
    single_step_test('TEST-A-1410', 'VIOLATED', 22)

def test_a_1411_cmd_followed_by():
    single_step_test('TEST-A-1411', 'VIOLATED', 24)

# Note - Although it's correct for 1412 and 1413 to be VIOLATED, the code gets there in a strange way.
# It first considers only the linear steps, finds no match, and signals a violation.
# Then it considers the nonlinear steps, finds an ambiguous match, and signals a flag.
# To be conservative, the combining logic will only escalate the severity of a result, so the violation wins.
# Notice this isn't because we understand these are on different branches of an if,
# but by a quirk of how the checker considers steps. We'd get the same result if these were on the same if branch.
# It would be acceptable, maybe even preferable, for the code to report FLAGGED here instead, given the uncertainty of our analysis.

def test_a_1412_cmd_followed_by():
    single_step_test('TEST-A-1412', 'VIOLATED', 24)

def test_a_1413_cmd_followed_by():
    single_step_test('TEST-A-1413', 'VIOLATED', 26)

def single_step_test(fr_id, state, step_number):
    results, seq_json = run_results_only_test(__file__, fr_id, {state: [step_number]})
    return results[state][0]

