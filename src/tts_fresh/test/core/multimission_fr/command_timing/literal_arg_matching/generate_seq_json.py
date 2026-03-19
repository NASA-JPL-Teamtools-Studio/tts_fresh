import json
import os
from dataclasses import dataclass

# Since this is a long and involved sequence, this python script serves as a more legible version of the sequence.
# To update the sequence, update this script and re-generate the seq.json file.

def main():
    steps = [
        STEP_NUMBER(1),
        cmd('A1', 'X'),
        cmd('B1', 'X'),
        sep(),
        cmd('A1', 'Y'),
        cmd('B1', 'X'),
        sep(),
        cmd('A1', 'Z'),
        cmd('B1', 'X'),
        sep(),
        cmd('A1', 'X'),
        cmd('B1', 'Y'),
        sep(),
        cmd('A1', 'Y'),
        cmd('B1', 'Y'),
        sep(),
        cmd('A1', 'Z'),
        cmd('B1', 'Y'),
        sep(),
        cmd('A1', 'X'),
        cmd('B1', 'Z'),
        sep(),
        cmd('A1', 'Y'),
        cmd('B1', 'Z'),
        sep(),
        cmd('A1', 'Z'),
        cmd('B1', 'Z'),
        sep(),

        STEP_NUMBER(31),
        cmd('A2', 0),
        cmd('B2', 0),
        sep(),
        cmd('A2', 1),
        cmd('B2', 0),
        sep(),
        cmd('A2', 2),
        cmd('B2', 0),
        sep(),
        cmd('A2', 0),
        cmd('B2', 1),
        sep(),
        cmd('A2', 1),
        cmd('B2', 1),
        sep(),
        cmd('A2', 2),
        cmd('B2', 1),
        sep(),
        cmd('A2', 0),
        cmd('B2', 2),
        sep(),
        cmd('A2', 1),
        cmd('B2', 2),
        sep(),
        cmd('A2', 2),
        cmd('B2', 2),
        sep(),

        STEP_NUMBER(61),
        cmd('A3', 'X'),
        cmd('B3', 'X'),
        sep(),
        cmd('A3', 'Y'),
        cmd('B3', 'X'),
        sep(),
        cmd('A3', symbol('X')),
        cmd('B3', 'X'),
        sep(),
        cmd('A3', 'X'),
        cmd('B3', 'Y'),
        sep(),
        cmd('A3', 'Y'),
        cmd('B3', 'Y'),
        sep(),
        cmd('A3', symbol('X')),
        cmd('B3', 'Y'),
        sep(),
        cmd('A3', 'X'),
        cmd('B3', symbol('X')),
        sep(),
        cmd('A3', 'Y'),
        cmd('B3', symbol('X')),
        sep(),
        cmd('A3', symbol('X')),
        cmd('B3', symbol('X')),
        sep(),

        STEP_NUMBER(91),
        cmd('A4', 'X'),
        cmd('B4'),
        sep(),
        cmd('A4', 'Y'),
        cmd('B4'),
        sep(),
        cmd('A4', 'Z'),
        cmd('B4'),
        sep(),
        cmd('A4'),
        cmd('B4', 'X'),
        sep(),
        cmd('A4'),
        cmd('B4', 'Y'),
        sep(),
        cmd('A4'),
        cmd('B4', 'Z'),
        sep(),

        STEP_NUMBER(121),
        [
            # We want to generate every combination of 2-arg commands, with three options per arg
            # We'll put block "C a3 a2, D a1 a0, sep" at the position "a3 a2 a1 a0", a 4-digit ternary number
            # where X = 0, Y = 1, Z = 2.
            [
                cmd('C1', a3, a2),
                cmd('D1', a1, a0),
                sep(),
            ]
            for a3 in 'XYZ'
            for a2 in 'XYZ'
            for a1 in 'XYZ'
            for a0 in 'XYZ'
            # Since this adds 3^4 = 81 combinations, each with 3 commands, it adds 243 commands.
        ],

        STEP_NUMBER(371),
        [
            # Do the same, but with numbers this time
            [
                cmd('C2', a3, a2),
                cmd('D2', a1, a0),
                sep(),
            ]
            for a3 in range(3)
            for a2 in range(3)
            for a1 in range(3)
            for a0 in range(3)
        ],

        STEP_NUMBER(621),
        [
            # Finally, do the same thing again but use a symbol instead of 'Z'
            [
                cmd('C3', a3, a2),
                cmd('D3', a1, a0),
                sep(),
            ]
            for a3 in ['X', 'Y', symbol('X')]
            for a2 in ['X', 'Y', symbol('X')]
            for a1 in ['X', 'Y', symbol('X')]
            for a0 in ['X', 'Y', symbol('X')]
        ],

        STEP_NUMBER(871),
        # Now, we want to try versions that are missing some of the arguments
        [
            [
                cmd('C4', a2, a1),
                cmd('D4', a0),
                sep(),
            ]
            for a2 in 'XYZ'
            for a1 in 'XYZ'
            for a0 in 'XYZ'
            # Adds 3^3 * 3 = 81 commands
        ],
        [
            [
                cmd('C4', a2),
                cmd('D4', a1, a0),
                sep(),
            ]
            for a2 in 'XYZ'
            for a1 in 'XYZ'
            for a0 in 'XYZ'
            # Adds 3^3 * 3 = 81 commands
        ],
        [
            [
                cmd('C4', a1, a0),
                cmd('D4'),
                sep(),
            ]
            for a1 in 'XYZ'
            for a0 in 'XYZ'
            # Adds 3^2 * 3 = 27 commands
        ],
        [
            [
                cmd('C4', a1),
                cmd('D4', a0),
                sep(),
            ]
            for a1 in 'XYZ'
            for a0 in 'XYZ'
            # Adds 3^2 * 3 = 27 commands
        ],
        [
            [
                cmd('C4'),
                cmd('D4', a1, a0),
                sep(),
            ]
            for a1 in 'XYZ'
            for a0 in 'XYZ'
            # Adds 3^2 * 3 = 27 commands
        ],
        [
            [
                cmd('C4', a0),
                cmd('D4'),
                sep(),
            ]
            for a0 in 'XYZ'
            # Adds 3^1 * 3 = 9 commands
        ],
        [
            [
                cmd('C4'),
                cmd('D4', a0),
                sep(),
            ]
            for a0 in 'XYZ'
            # Adds 3^1 * 3 = 9 commands
        ],
        [
            cmd('C4'),
            cmd('D4'),
            sep(),
            # Adds 3^0 * 3 = 3 commands
        ]
    ]
    print(f'Building sequence...')
    steps = expand_steps(steps)
    print(f'Built sequence: {len(steps)} total steps.')
    seq_json = {
        "id": "test",
        "metadata": {
            "comment": f"This test sequence was generated by {os.path.basename(__file__)}. Look to that file for a more legible description of the sequence."
        },
        "steps": steps
    }
    seq_json_file = os.path.join(os.path.dirname(__file__), 'test.seq.json')
    print(f'Writing sequence to {seq_json_file}')
    with open(seq_json_file, 'w') as f:
        json.dump(seq_json, f, indent=2)

def cmd(stem_letter, *args):
    args = list(args)
    for i, arg in enumerate(args):
        if not isinstance(arg, dict):
            type_name = {str: 'string', int: 'number', float: 'number'}[type(arg)]
            arg = {
                "type": type_name,
                "value": arg
            }
        arg['name'] = f'arg_{i}' if arg.get('name') is None else arg['name']
        args[i] = arg
    return {
        "args": args,
        "stem": "FAKE_CMD_" + stem_letter,
        "time": {
            "tag": "00:00:01",
            "type": "COMMAND_RELATIVE"
        },
        "type": "command"
    }

def sep(time_tag="01:00:00"):
    return {
        "args": [],
        "stem": "CMD_NO_OP",
        "time": {
            "tag": time_tag,
            "type": "COMMAND_RELATIVE"
        },
        "type": "command"
    }

def symbol(value):
    return {
        "type": "symbol",
        "value": value
    }

@dataclass
class STEP_NUMBER:
    """
    Placeholder used to insert CMD_NO_OPs such that the following command is at the given step.

    That makes tests a little easier to modify down the road.
    """
    num: int

def expand_steps(steps):
    expanded_steps = []
    for step in steps:
        if isinstance(step, STEP_NUMBER):
            desired_step_number = step.num
            steps_to_add = desired_step_number - len(expanded_steps) - 1
            assert steps_to_add >= 0
            expanded_steps += [sep("00:00:01")] * steps_to_add
        elif isinstance(step, list):
            expanded_steps += expand_steps(step)
        else:
            expanded_steps.append(step)
    return expanded_steps

if __name__ == '__main__':
    main()

