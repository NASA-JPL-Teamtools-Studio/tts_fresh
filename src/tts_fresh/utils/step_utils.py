from dataclasses import dataclass
from tts_fresh.flightrules.fr_base import FRCriticality
from tts_fresh.seqdict import SeqDict, SeqStep, SeqArgType
from tts_fresh.mission_config import get_fr_criticality_from_id

_RECOGNIZED_CRITICALITIES = {
        'A': FRCriticality.CAT_A,
        'B': FRCriticality.CAT_B,
        'C': FRCriticality.CAT_C,
}


@dataclass
class HexRange:
    """
    Represents a range of memory addresses defined by a start and end point.
    This class provides utility methods to check for address space conflicts or overlaps during memory validation.
    """
    start: int
    end: int

    def disjoint_with(self, other: "HexRange") -> bool:
        """
        Determines if the current address range has no intersection with another range.
        It checks if one range completely precedes or follows the other in the address space to ensure separation.

        :param other: The other hex range to compare against.
        :type other: HexRange
        :return: True if the ranges are completely separate, False otherwise.
        :rtype: bool
        """
        return self.end < other.start or self.start > other.end

    def overlaps(self, other: "HexRange") -> bool:
        """
        Checks if any portion of the current address range intersects with another range.
        This provides a direct way to identify memory access conflicts between two defined blocks.

        :param other: The other hex range to check for intersection.
        :type other: HexRange
        :return: True if the ranges share any common address space, False otherwise.
        :rtype: bool
        """
        return not self.disjoint_with(other)

    def __str__(self):
        """
        Returns a formatted string representation of the address range in hexadecimal.
        The format consistently uses lowercase '0x' prefixes and padded values for clear logging and reporting.

        :return: A human-readable string describing the range.
        :rtype: str
        """
        return f'{self.start:#010X} to {self.end:#010X}'.replace('X', 'x')


def get_criticality(flight_rule_id: str) -> FRCriticality:
    """
    Maps a mission-specific flight rule identifier to a standardized criticality enum.
    It utilizes the active mission configuration to parse the identifier and validates the result against a set of recognized categories.

    :param flight_rule_id: The unique identifier string for the flight rule.
    :type flight_rule_id: str
    :return: The corresponding standardized criticality level for the rule.
    :rtype: FRCriticality
    :raises ValueError: If the parsed criticality indicator is not recognized by the system.
    """
    crit = None
    crit = get_fr_criticality_from_id(flight_rule_id)
    try:
        return _RECOGNIZED_CRITICALITIES[crit]
    except KeyError:
        raise ValueError(f"Criticality indication {crit} is not recognized! Only {', '.join(_RECOGNIZED_CRITICALITIES)} are recognized.")

def get_steps(seq_json: SeqDict) -> "list[SeqStep]":
    """
    Extracts the list of command steps from a parsed sequence dictionary object.
    This provides a unified interface for flight rules to access the primary execution path of a sequence.

    :param seq_json: The sequence dictionary containing the loaded sequence data and metadata.
    :type seq_json: SeqDict
    :return: A list of individual steps or commands extracted from the sequence.
    :rtype: list[SeqStep]
    """
    return seq_json.steps
#    return seq_json.get('steps', []) + seq_json.get('hardware_commands', [])


def read_address_arg(step: SeqStep, arg_number) -> int:
        """
        Parses a specific command argument and converts it into an integer memory address.
        It handles various argument types, including standard numeric values and hexadecimal strings, while ensuring the data is in a usable format for memory checks.

        :param step: The sequence step containing the arguments to be inspected.
        :type step: SeqStep
        :param arg_number: The index of the argument within the step's argument list.
        :type arg_number: int
        :return: The parsed integer value representing the memory address.
        :rtype: int
        :raises NotImplementedError: If the argument is a symbolic variable that cannot be resolved statically.
        :raises ValueError: If the argument type is not recognized as a valid numeric or hex format.
        """
        arg = step.args[arg_number]
        arg_type = arg.argtype
        arg_value = arg.value
        if arg_type == SeqArgType.NUMBER:
            return arg_value
        elif arg_type == SeqArgType.HEX:
            return int(arg_value, 16)
        elif arg_type == SeqArgType.SYMBOL:
            raise NotImplementedError(f'Command uses variable {arg_value} in specifying what addresses it reads from.')
        else:
            raise ValueError(f'Argument type {arg_type} is not recognized. It should be number or hex.')