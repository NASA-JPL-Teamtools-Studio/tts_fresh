import pytest
from tts_fresh.test.test_utils import run_results_only_test

# The run_test & block methods are just short forms, expanded below.
# A block should correspond to a block of commands in generate_seq_json.py,
# with a fixed step number to start and a long sep() to end the block, which mostly isolates it from other blocks.
# This has no functional effect on the test, it just loosely organizes the different kinds of checks.
# I find it easier to think about these tests one block at a time.

def test_rel_arg_matching_1001():
    run_test(1001,
        block([1, 10], [4, 7]),
        block([21, 30], [24, 27]),
        block(None, None, [41, 44, 47, 50, 53, 56]),
        )

def test_rel_arg_matching_1002():
    # This rule is equivalent to 1001
    run_test(1002,
        block([1, 10], [4, 7]),
        block([21, 30], [24, 27]),
        block(None, None, [41, 44, 47, 50, 53, 56]),
        )

def test_rel_arg_matching_1003():
    run_test(1003,
        block(104, [101, 107, 110, 113]),
        block(124, [121, 127, 130, 133]),
        block(None, 150, [141, 144, 147]),
        block(None, None, [161, 164, 167, 170]),
        )

def test_rel_arg_matching_1004():
    run_test(1004,
        block(201, [204, 207, 210, 213]),
        block(221, [224, 227, 230, 233]),
        block(244, 256, [241, 247, 250, 253]),
        block(None, None, [261, 264, 267, 270]),
        )

def test_rel_arg_matching_1005():
    # This rule is equivalent to 1004
    run_test(1005,
        block(201, [204, 207, 210, 213]),
        block(221, [224, 227, 230, 233]),
        block(244, 256, [241, 247, 250, 253]),
        block(None, None, [261, 264, 267, 270]),
        )

def test_rel_arg_matching_1006():
    run_test(1006,
        block(204, [201, 207, 210, 213]),
        block(224, [221, 227, 230, 233]),
        block(None, 250, [241, 244, 247, 253, 256]),
        block(None, None, [261, 264, 267, 270]),
        )

def test_rel_arg_matching_1007():
    run_test(1007,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1008():
    # This rule is equivalent to 1007
    run_test(1008,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1009():
    # This rule is equivalent to 1007
    run_test(1009,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1010():
    # This rule is equivalent to 1007
    run_test(1010,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1011():
    run_test(1011,
        block([301, 319, 328, 346], [304, 307, 310, 313, 316, 322, 325, 331, 334, 337, 340, 343]),
        block([351, 369, 378, 396], [354, 357, 360, 363, 366, 372, 375, 381, 384, 387, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1012():
    # This rule is equivalent to 1011
    run_test(1012,
        block([301, 319, 328, 346], [304, 307, 310, 313, 316, 322, 325, 331, 334, 337, 340, 343]),
        block([351, 369, 378, 396], [354, 357, 360, 363, 366, 372, 375, 381, 384, 387, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

# 11xx test are equivalent to 10xx tests.
# They are the same rules, but expressed from the point of view of the relative, rather than main, command.

def test_rel_arg_matching_1101():
    run_test(1101,
        block([1, 10], [4, 7]),
        block([21, 30], [24, 27]),
        block(None, None, [41, 44, 47, 50, 53, 56]),
        )

def test_rel_arg_matching_1102():
    # This rule is equivalent to 1101
    run_test(1102,
        block([1, 10], [4, 7]),
        block([21, 30], [24, 27]),
        block(None, None, [41, 44, 47, 50, 53, 56]),
        )

def test_rel_arg_matching_1103():
    run_test(1103,
        block(104, [101, 107, 110, 113]),
        block(124, [121, 127, 130, 133]),
        block(None, 150, [141, 144, 147]),
        block(None, None, [161, 164, 167, 170]),
        )

def test_rel_arg_matching_1104():
    run_test(1104,
        block(201, [204, 207, 210, 213]),
        block(221, [224, 227, 230, 233]),
        block(244, 256, [241, 247, 250, 253]),
        block(None, None, [261, 264, 267, 270]),
        )

def test_rel_arg_matching_1105():
    # This rule is equivalent to 1104
    run_test(1105,
        block(201, [204, 207, 210, 213]),
        block(221, [224, 227, 230, 233]),
        block(244, 256, [241, 247, 250, 253]),
        block(None, None, [261, 264, 267, 270]),
        )

def test_rel_arg_matching_1106():
    run_test(1106,
        block(204, [201, 207, 210, 213]),
        block(224, [221, 227, 230, 233]),
        block(None, 250, [241, 244, 247, 253, 256]),
        block(None, None, [261, 264, 267, 270]),
        )

def test_rel_arg_matching_1107():
    run_test(1107,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1108():
    # This rule is equivalent to 1107
    run_test(1108,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1109():
    # This rule is equivalent to 1107
    run_test(1109,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )
    
def test_rel_arg_matching_1110():
    # This rule is equivalent to 1107
    run_test(1110,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1111():
    run_test(1111,
        block([301, 319, 328, 346], [304, 307, 310, 313, 316, 322, 325, 331, 334, 337, 340, 343]),
        block([351, 369, 378, 396], [354, 357, 360, 363, 366, 372, 375, 381, 384, 387, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1112():
    # This rule is equivalent to 1111
    run_test(1112,
        block([301, 319, 328, 346], [304, 307, 310, 313, 316, 322, 325, 331, 334, 337, 340, 343]),
        block([351, 369, 378, 396], [354, 357, 360, 363, 366, 372, 375, 381, 384, 387, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

# 12xx tests involve checking from both sides

def test_rel_arg_matching_1201():
    # This rule is equivalent to 1007
    run_test(1201,
        block([301, 310, 337, 346], [304, 307, 313, 316, 319, 322, 325, 328, 331, 334, 340, 343]),
        block([351, 360, 387, 396], [354, 357, 363, 366, 369, 372, 375, 378, 381, 384, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1202():
    # This rule is equivalent to 1011
    run_test(1202,
        block([301, 319, 328, 346], [304, 307, 310, 313, 316, 322, 325, 331, 334, 337, 340, 343]),
        block([351, 369, 378, 396], [354, 357, 360, 363, 366, 372, 375, 381, 384, 387, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1203():
    # This rule is equivalent to 1011
    run_test(1203,
        block([301, 319, 328, 346], [304, 307, 310, 313, 316, 322, 325, 331, 334, 337, 340, 343]),
        block([351, 369, 378, 396], [354, 357, 360, 363, 366, 372, 375, 381, 384, 387, 390, 393]),
        block([401], None, [410, 437, 446, 404, 407, 413, 416, 419, 422, 425, 428, 431, 434, 440, 443]),
        )

def test_rel_arg_matching_1301():
    run_test(1301,
        block([301, 310, 325, 334], [304, 307, 328, 331]),
        block(), # Nothing in the second block (numbers) matches the literal X in the first argument
        block([401, 425], None, [404, 407, 410, 413, 416, 419, 422, 428, 431, 434, 437, 440, 443, 446]),
        block(None, None, [463, 466, 469, 472, 487, 490, 493, 496]),
        )

# Test utilities for this file

def block(passed=None, violated=None, flagged=None):
    return as_list(passed), as_list(violated), as_list(flagged)

def as_list(x):
    if isinstance(x, list):
        return x
    if x is None:
        return []
    return [x]

def run_test(fr_number, *step_blocks):
    """Notes pass/fail/flag steps in discrete blocks, to make it easier to relate the test to the sequence."""

    passed = []
    violated = []
    flagged = []

    for p,v,f in step_blocks:
        passed += p
        violated += v
        flagged += f

    return run_results_only_test(__file__, f'TEST-A-{fr_number:>04}', {
        'PASSED': passed,
        'VIOLATED': violated,
        'FLAGGED': flagged
    })

