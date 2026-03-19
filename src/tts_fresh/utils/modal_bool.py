import enum


class ModalBool(enum.Enum):
    """
    Implements a three-valued logic system consisting of YES, NO, and MAYBE states.
    This enum provides standard boolean-like operations such as AND, OR, and NOT, allowing for more nuanced conditional logic where certainty is not always guaranteed.
    It is particularly useful for validation rules that may have indeterminate results based on the provided sequence data.
    """
    NO = 0
    MAYBE = 1
    YES = 2

    @staticmethod
    def of(b) -> "ModalBool":
        """
        Converts a standard boolean value or an existing ModalBool instance into a ModalBool type.
        This utility ensures type consistency by mapping True/False values to YES/NO while passing existing ModalBool states through unchanged.
        It serves as a constructor-like helper for normalizing inputs before performing logical operations.

        :param b: The value to be converted, which can be a boolean or a ModalBool instance.
        :type b: bool or ModalBool
        :return: The corresponding ModalBool representation of the input.
        :rtype: ModalBool
        """
        if isinstance(b, ModalBool):
            return b
        else:
            return ModalBool.YES if b else ModalBool.NO

    def __invert__(self) -> "ModalBool":
        """
        Performs a logical NOT operation on the current ModalBool state.
        It flips YES to NO and NO to YES, while the MAYBE state remains MAYBE as its inverse is still indeterminate.
        This allows for bitwise-style negation (~) in conditional expressions.

        :return: The inverted ModalBool state.
        :rtype: ModalBool
        """
        if self == ModalBool.NO:
            return ModalBool.YES
        elif self == ModalBool.YES:
            return ModalBool.NO
        else:
            return ModalBool.MAYBE

    def __and__(self, other) -> "ModalBool":
        """
        Executes a logical AND operation between the current state and another value.
        The result is YES only if both sides are YES, and NO if either side is NO; otherwise, the result is MAYBE.
        This method enables the use of the '&' operator for combining multiple logical conditions.

        :param other: The other value to compare against, which will be normalized via ModalBool.of().
        :type other: any
        :return: The result of the logical AND operation.
        :rtype: ModalBool
        """
        other = ModalBool.of(other)
        if self == ModalBool.YES and other == ModalBool.YES:
            return ModalBool.YES
        elif self == ModalBool.NO or other == ModalBool.NO:
            return ModalBool.NO
        else:
            return ModalBool.MAYBE

    def __rand__(self, other) -> "ModalBool":
        """
        Handles the reflected logical AND operation when the left-hand operand is not a ModalBool.
        It ensures that standard booleans can be combined with ModalBool instances using the '&' operator in any order.
        This effectively delegates the work back to the standard __and__ implementation.

        :param other: The operand on the left side of the '&' operator.
        :type other: any
        :return: The result of the logical AND operation.
        :rtype: ModalBool
        """
        return self & other

    def __or__(self, other) -> "ModalBool":
        """
        Executes a logical OR operation between the current state and another value.
        The result is YES if either side is YES, and NO only if both sides are NO; any other combination results in MAYBE.
        This method enables the use of the '|' operator for evaluating alternative conditions.

        :param other: The other value to compare against, which will be normalized via ModalBool.of().
        :type other: any
        :return: The result of the logical OR operation.
        :rtype: ModalBool
        """
        other = ModalBool.of(other)
        if self == ModalBool.YES or other == ModalBool.YES:
            return ModalBool.YES
        elif self == ModalBool.NO and other == ModalBool.NO:
            return ModalBool.NO
        else:
            return ModalBool.MAYBE

    def __ror__(self, other) -> "ModalBool":
        """
        Handles the reflected logical OR operation when the left-hand operand is not a ModalBool.
        This allows for flexible expressions where a standard boolean is on the left side of a '|' operator.
        It maintains consistency by redirecting the call to the standard __or__ method.

        :param other: The operand on the left side of the '|' operator.
        :type other: any
        :return: The result of the logical OR operation.
        :rtype: ModalBool
        """
        return self | other