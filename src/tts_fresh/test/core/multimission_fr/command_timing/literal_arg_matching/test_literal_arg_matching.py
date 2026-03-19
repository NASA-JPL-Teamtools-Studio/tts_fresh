import pytest
from tts_fresh.test.test_utils import run_results_only_test

# The run_test & block methods are just short forms, expanded below.
# A block should correspond to a block of commands in generate_seq_json.py,
# with a fixed step number to start and a long sep() to end the block, which mostly isolates it from other blocks.
# This has no functional effect on the test, it just loosely organizes the different kinds of checks.
# I find it easier to think about these tests one block at a time.

# If you use 0-based indexing and set offset to the STEP_NUMBER for that block, it'll scale and align properly.

# 10xx tests apply a single argument restriction to the A command, which uses a single argument.
# Since no restriction is applied to B, they pass when they match and aren't present when they don't match.

def test_literal_arg_matching_1001():
    run_test(1001,
        block([0, 9, 18], offset=1),
        block(None, offset=31),
        block([0, 9, 18], None, [6, 15, 24], offset=61),
        block([0], None, [9, 12, 15], offset=91),
        )

def test_literal_arg_matching_1002():
    run_test(1002,
        block(None, offset=1),
        block([0, 9, 18], offset=31),
        block(None, None, [6, 15, 24], offset=61),
        block(None, None, [9, 12, 15], offset=91),
        )

def test_literal_arg_matching_1003():
    # This rule is equivalent to 1001
    run_test(1003,
        block([0, 9, 18], offset=1),
        block(None, offset=31),
        block([0, 9, 18], None, [6, 15, 24], offset=61),
        block([0], None, [9, 12, 15], offset=91),
        )

def test_literal_arg_matching_1004():
    # This rule is equivalent to 1002
    run_test(1004,
        block(None, offset=1),
        block([0, 9, 18], offset=31),
        block(None, None, [6, 15, 24], offset=61),
        block(None, None, [9, 12, 15], offset=91),
        )

def test_literal_arg_matching_1005():
    run_test(1005,
        block([0, 3, 9, 12, 18, 21], offset=1),
        block(None, offset=31),
        block([0, 3, 9, 12, 18, 21], None, [6, 15, 24], offset=61),
        block([0, 3], None, [9, 12, 15], offset=91),
        )

def test_literal_arg_matching_1006():
    run_test(1006,
        block(None, offset=1),
        block([0, 3, 9, 12, 18, 21], offset=31),
        block(None, None, [6, 15, 24], offset=61),
        block(None, None, [9, 12, 15], offset=91),
        )


# 11xx are the same as 100x, but the argument restriction is applied to B instead of A.
# This means *every* A command matches, and we get pass or fail depending on whether B matches.

def test_literal_arg_matching_1101():
    run_test(1101,
        block([0, 3, 6], [9, 12, 15, 18, 21, 24], offset=1),
        block(None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=31),
        # Steps 9, 12, 15 (really 70, 73, 76) "should" fail in this test, but match a later command in this block with a symbolic arg, and are flagged instead.
        block([0, 3, 6], None, [9, 12, 15, 18, 21, 24], offset=61),
        block([9], [12, 15], [0, 3, 6], offset=91),
        )

def test_literal_arg_matching_1102():
    run_test(1102,
        block(None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=1),
        block([0, 3, 6], [9, 12, 15, 18, 21, 24], offset=31),
        # Steps 0 - 15 (really 61 - 76) "should" fail in this test, but match a later command in this block with a symbolic arg, and are flagged instead.
        block(None, None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=61),
        block(None, [9, 12, 15], [0, 3, 6], offset=91),
        )

def test_literal_arg_matching_1103():
    # This rule is equivalent to 1101
    run_test(1103,
        block([0, 3, 6], [9, 12, 15, 18, 21, 24], offset=1),
        block(None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=31),
        # Steps 9, 12, 15 (really 70, 73, 76) "should" fail in this test, but match a later command in this block with a symbolic arg, and are flagged instead.
        block([0, 3, 6], None, [9, 12, 15, 18, 21, 24], offset=61),
        block([9], [12, 15], [0, 3, 6], offset=91),
        )

def test_literal_arg_matching_1104():
    # This rule is equivalent to 1102
    run_test(1104,
        block(None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=1),
        block([0, 3, 6], [9, 12, 15, 18, 21, 24], offset=31),
        # Steps 0 - 15 (really 61 - 76) "should" fail in this test, but match a later command in this block with a symbolic arg, and are flagged instead.
        block(None, None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=61),
        block(None, [9, 12, 15], [0, 3, 6], offset=91),
        )

def test_literal_arg_matching_1105():
    run_test(1105,
        block([0, 3, 6, 9, 12, 15], [18, 21, 24], offset=1),
        block(None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=31),
        block([0, 3, 6, 9, 12, 15], None, [18, 21, 24], offset=61),
        block([9, 12], [15], [0, 3, 6], offset=91),
        )

def test_literal_arg_matching_1106():
    run_test(1106,
        block(None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=1),
        block([0, 3, 6, 9, 12, 15], [18, 21, 24], offset=31),
        # Steps 0 - 15 (really 61 - 76) "should" fail in this test, but match a later command in this block with a symbolic arg, and are flagged instead.
        block(None, None, [0, 3, 6, 9, 12, 15, 18, 21, 24], offset=61),
        block(None, [9, 12, 15], [0, 3, 6], offset=91),
        )

# 12xx combine a single-argument rule on each command, for single-argument commands

def test_literal_arg_matching_1201():
    run_test(1201,
        block([9], [0, 18], offset=1),
        block(None, offset=31),
        block([9], [0], [6, 15, 18, 24], offset=61),
        block(None, None, [0, 9, 12, 15], offset=91),
        )

def test_literal_arg_matching_1202():
    run_test(1202,
        block([9, 15], [0, 6, 18, 24], offset=1),
        block(None, offset=31),
        block([9], [0], [6, 15, 18, 24], offset=61),
        block(None, None, [0, 6, 9, 12, 15], offset=91),
        )

# 2xxx tests apply to commands with multiple arguments.

# The two-arg commands were laid out in power-of-three size blocks, such that 
# the index in ternary corresponds digit-by-digit with the arguments.
# This lets us concisely represent a set of cases as a pattern on the ternary digits.

# 20xx tests apply a single restriction to one argument of the main command

def test_literal_arg_matching_2001():
    run_test(2001,
        block(ternary_pattern('*0**'), scale=3, offset=121),
        block(None, scale=3, offset=371),
        block(ternary_pattern('*0**'), None, ternary_pattern('*2**'), scale=3, offset=621),
        block(ternary_pattern('*0*'), scale=3, offset=871),
        block(None, None, ternary_pattern('***'), scale=3, offset=871+81),
        block(ternary_pattern('*0'), scale=3, offset=871+81+81),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27+9),
        block(None, None, ternary_pattern(''), scale=3, offset=871+81+81+27+27+27+9+9),
        )

def test_literal_arg_matching_2002():
    run_test(2002,
        block(None, ternary_pattern('****'), scale=3, offset=121),
        block(ternary_pattern('***1'), ternary_pattern('***0', '***2'), scale=3, offset=371),
        # offset=621 tests "should" fail for ***0 and ***1, but they match later commands with symbolic args and get flagged instead.
        block(None, None, ternary_pattern('****'), scale=3, offset=621),
        block(None, None, ternary_pattern('***'), scale=3, offset=871),
        # offset=871+81 tests "should" all fail, but they match later commands with missing args and get flagged instead
        block(None, None, ternary_pattern('***'), scale=3, offset=871+81),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27),
        # offset=871+81+81+27+27 tests "should" all fail, but they match later commands with missing args and get flagged instead
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27+9),
        block(None, None, ternary_pattern(''), scale=3, offset=871+81+81+27+27+27+9+9),
        )

def test_literal_arg_matching_2003():
    run_test(2003,
        block(ternary_pattern('*10*'), ternary_pattern('*11*', '*12*'), scale=3, offset=121),
        block(None, scale=3, offset=371),
        # offset=621 "should" fail for *11*, but they match later commands with symbolic args and get flagged instead
        block(ternary_pattern('*10*'), None, ternary_pattern('*11*', '*12*', '*2**'), scale=3, offset=621),
        block(ternary_pattern('*10'), ternary_pattern('*11', '*12'), scale=3, offset=871),
        block(None, None, ternary_pattern('***'), scale=3, offset=871+81),
        block(None, None, ternary_pattern('*1'), scale=3, offset=871+81+81),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27+9),
        block(None, None, ternary_pattern(''), scale=3, offset=871+81+81+27+27+27+9+9),
        )

def test_literal_arg_matching_2004():
    run_test(2004,
        block(ternary_pattern('10**', '12**'), scale=3, offset=121),
        block(None, scale=3, offset=371),
        block(ternary_pattern('10**'), None, ternary_pattern('12**', '20**', '22**'), scale=3, offset=621),
        block(ternary_pattern('10*', '12*'), scale=3, offset=871),
        # When one argument for the main command is missing,
        # we only flag if the arg that's present is compatible with the FR's inclusion requirements
        block(None, None, ternary_pattern('1**'), scale=3, offset=871+81),
        block(ternary_pattern('10', '12'), scale=3, offset=871+81+81),
        block(None, None, ternary_pattern('1*'), scale=3, offset=871+81+81+27),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27+27),
        block(None, None, ternary_pattern('1'), scale=3, offset=871+81+81+27+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27+9),
        block(None, None, ternary_pattern(''), scale=3, offset=871+81+81+27+27+27+9+9),
        )

def test_literal_arg_matching_2005():
    run_test(2005,
        block(ternary_pattern('1010', '1011', '1210', '1211'), ternary_pattern('100*', '102*', '1012', '120*', '122*', '1212'), scale=3, offset=121),
        block(None, scale=3, offset=371),
        block(ternary_pattern('1010', '1011'), ternary_pattern('1000', '1001', '1002'), ternary_pattern('1012', '102*', '12**', '20**', '22**'), scale=3, offset=621),
        # When one argument for the main command is missing,
        # we only flag if the arg that's present is compatible with the FR's inclusion requirements
        block(None, None, ternary_pattern('10*', '12*'), scale=3, offset=871),
        block(None, None, ternary_pattern('1**'), scale=3, offset=871+81),
        block(None, None, ternary_pattern('10', '12'), scale=3, offset=871+81+81),
        block(None, None, ternary_pattern('1*'), scale=3, offset=871+81+81+27),
        block(None, None, ternary_pattern('**'), scale=3, offset=871+81+81+27+27),
        block(None, None, ternary_pattern('1'), scale=3, offset=871+81+81+27+27+27),
        block(None, None, ternary_pattern('*'), scale=3, offset=871+81+81+27+27+27+9),
        block(None, None, ternary_pattern(''), scale=3, offset=871+81+81+27+27+27+9+9),
        )

# Test utilities for this file
def ternary_pattern(*patterns):
    def _expand(pattern):
        if pattern:
            final_digits = (0, 1, 2) if pattern[-1] == '*' else (int(pattern[-1]),)
            for n in _expand(pattern[:-1]):
                for d in final_digits:
                    yield 3*n + d
        else:
            yield 0
    return [n for pattern in patterns for n in _expand(pattern)]

def block(passed=None, violated=None, flagged=None, *, scale=1, offset=0):
    return tuple(scale_step_numbers(as_list(x), scale, offset) for x in (passed, violated, flagged))

def as_list(x):
    if isinstance(x, list):
        return x
    if x is None:
        return []
    return [x]

def scale_step_numbers(step_numbers, scale=1, offset=0):
    return [offset + (n * scale) for n in step_numbers]

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

