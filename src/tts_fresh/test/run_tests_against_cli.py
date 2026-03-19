import os
import sys
import pytest

# cleanest way to do this was via an environment variable. we don't wish to subject people
# that want to run in this configuration to that, though. this provides a small utility
# that configures variables appropriately and opaquely.
def run_tests():
    # Set the environment variable in the current process
    os.environ["FRESH_TESTS_USE_CLI"] = "TRUE"
    
    # Use the pytest API to run tests directly
    # This avoids subprocess entirely, removing all Bandit warnings
    exit_code = pytest.main(["test/EURC"])
    sys.exit(exit_code)

if __name__ == "__main__":
    run_tests()