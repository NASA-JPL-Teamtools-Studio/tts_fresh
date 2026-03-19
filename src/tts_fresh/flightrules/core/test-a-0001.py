from tts_fresh.flightrules.fr_base import FRBase, FRCheckInfo, FRCriticality, FRResult, FRState
from tts_fresh.seqdict import SeqDict


# Leading underscore disables this test, but keeping the code as a simple example.
class _FR_TESTA0001_checker(FRBase):
    """
    A sample flight rule implementation used primarily for testing and demonstration purposes.
    It follows the standard pattern of inheriting from FRBase but is prefixed with an underscore 
    to prevent the core engine from executing it during normal runs.
    The class serves as a reference for how to structure rule logic and manage result aggregation.
    """

    def check_fr(sequence: SeqDict, config: dict) -> "list[FRCheckInfo]":
        """
        Executes a simulated flight rule check that is designed to consistently report a violation.
        It demonstrates the initialization of an FRCheckInfo object and the subsequent use of the addition operator to integrate a failure result.
        This method provides a clear example of how rule metadata and command-specific results are managed within the system.

        :param sequence: The command sequence to be validated, though it is not actively inspected in this testing implementation.
        :type sequence: SeqDict
        :param config: A dictionary containing configuration parameters, which this specific test rule ignores.
        :type config: dict
        :return: A list containing a single check info object that reflects the pre-defined rule violation.
        :rtype: list[FRCheckInfo]
        """
        result_info = FRCheckInfo(
            flight_rule_id="TEST-A-0001", 
            flight_rule_version="0",
            flight_rule_description="a testing flight rule", 
            criticality=FRCriticality.CAT_A, 
            # The state should always start with PASSED, 0 violations, no results.
            state=FRState.PASSED,
            num_violations=0,
            results=[])

        # Imagine we did some checking and found this violation...
        # Using += to add a result will also update the bookkeeping variables: state, num_violations, results.
        result_info += FRResult(
                    state=FRState.VIOLATED,
                    step_number=-1,
                    command_stem="SEQUENCE",
                    command_args=[],
                    flight_rule_id="TEST-A-0001",
                    message="this rule will always fail"
                )
        return [result_info]