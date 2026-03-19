from tts_fresh.mission import MISSION
#from tts_fresh.fresh_io.seqjson_io import seqjson_to_seqdict
from tts_seq.core.seqjson_dict import seqjson_to_seqdict
import pathlib


# fresh/mission_base.py
from abc import ABC, abstractmethod
from typing import Any
import pathlib

class MissionConfigBase(ABC):
    """
    The blueprint for mission-specific logic.
    External repos will subclass this to provide custom validation parameters.
    It defines the required interface for discovery, I/O, and criticality parsing.

    Each mission used to have variables set here, and a file called mission.py
    determined which variables to honor. But in order to remove mission-specific
    code from the core repo, we used this as a bridge. Now each project can define
    its own extenison of MissionConfigBase and configure it to be used globally
    for each run using set_active_mission() below.

    It's not the most elegant, but it was a serviceable low-touch way to get
    it all disentangled.
    """

    @property
    @abstractmethod
    def mission_name(self) -> str:
        """
        Retrieves the name of the mission associated with the configuration.
        This property is used for identification and logging purposes across the tool.
        
        :return: The mission name (e.g., 'EURC').
        :rtype: str
        """
        pass

    @abstractmethod
    def get_flight_rules_package(self):
        """
        Returns the Python package module containing mission-specific flight rules.
        This allows the validation engine to dynamically discover and import rules for a specific mission.

        :return: The module reference for the mission's flight rules package.
        :rtype: module
        """
        pass

    @abstractmethod
    def get_io_method(self):
        """
        Returns the specific function used to parse sequence files into the internal SeqDict format.
        Different missions may use different sequence file formats, requiring unique parsing logic.

        :return: A callable function that takes a file path and returns a SeqDict.
        :rtype: callable
        """
        pass

    @abstractmethod
    def get_default_config_file_path(self) -> str:
        """
        Returns the file system path for the default JSON configuration associated with the mission.
        This configuration typically contains thresholds and constants required by the flight rules.

        :return: The full path to the default config file.
        :rtype: str
        """
        pass

    @abstractmethod
    def get_fr_criticality_from_id(self, fr_id: str) -> str:
        """
        Parses the criticality level (e.g., CAT_A) from a flight rule ID string.
        Each mission may have a different naming convention for their flight rule identifiers.

        :param fr_id: The unique identifier string for a flight rule.
        :type fr_id: str
        :return: The parsed criticality level as a string.
        :rtype: str
        """
        pass

    @abstractmethod
    def get_seq_file_extension(self) -> str:
        """
        Returns the expected file extension or glob pattern for sequence files.
        This is used by the CLI to filter files when processing directories.

        :return: The file extension string (e.g., '*.seq' or '*.seq.json').
        :rtype: str
        """
        pass
    
    @abstractmethod
    def get_testing_cmd_dict_path(self):
        """
        Returns the path to the command dictionary used during validation or unit testing.
        This dictionary defines the valid commands and arguments for the sequence.

        :return: The path to the testing command dictionary file.
        :rtype: pathlib.Path
        """
        pass

class CoreTestingMissionConfig(MissionConfigBase):
    """
    A concrete implementation of MissionConfigBase used for internal core testing.
    It defaults to SEQ JSON parsing and uses the EURC testing dictionaries for validation
    because it was originally written for EURC, and that hertigage still remains.
    """
    @property
    def mission_name(self) -> str:
        """
        Retrieves the name for the testing configuration.
        This identifies that the tool is running in a core test environment.

        :return: The string 'CORE_TESTS'.
        :rtype: str
        """
        return 'CORE_TESTS'

    def get_flight_rules_package(self):
        """
        Returns the package containing core flight rules for testing.
        In this implementation, it is currently left empty as testing often targets core rules directly.

        :return: None or the module reference.
        """
        pass

    def get_io_method(self):
        """
        Provides the standard JSON-to-SeqDict conversion method.
        This is the default I/O method used when no mission-specific override is set.

        :return: The seqjson_to_seqdict function.
        :rtype: callable
        """
        return seqjson_to_seqdict

    def get_default_config_file_path(self):
        """
        Provides the path to the default EURC configuration file for testing.
        This ensures tests have a consistent environment to run against.

        :return: The path object to the default config.
        :rtype: pathlib.Path
        """
        return pathlib.Path(__file__).parent.joinpath('config/eurc_default_config.json')

    def get_fr_criticality_from_id(self, fr_id):
        """
        Extracts criticality from a standard hyphenated flight rule ID.
        It expects a format like 'MISSION-CRIT-NUMBER' and raises an error if the format is invalid.

        :param fr_id: The flight rule ID string to parse.
        :type fr_id: str
        :return: The middle criticality segment of the ID.
        :rtype: str
        :raises ValueError: If the ID does not contain the expected number of segments.
        """
        try:
            _, crit, _ = fr_id.split('-')
            return crit
        except ValueError:
            raise ValueError(f'Invalid EURC FR ID: {fr_id}')

    def get_seq_file_extension(self):
        """
        Specifies that the test environment uses JSON-formatted sequence files.
        This helps the test runners locate the appropriate sample files.

        :return: The extension pattern '*.seq.json'.
        :rtype: str
        """
        return '*.seq.json'

    def get_testing_cmd_dict_path(self):
        """
        Returns the path to the XML command dictionary used for EURC testing.
        This file is located within the project's internal test directory structure.

        :return: The path to the command.xml file.
        :rtype: pathlib.Path
        """
        return pathlib.Path(__file__).parent.joinpath('test/dictionaries/command.xml')

    def get_control_flow_directives(self):
        return {
            'SEQ_IF',
            'SEQ_IF_AND',
            'SEQ_IF_OR',
            'SEQ_ELSE',
            'SEQ_END_IF',
            'SEQ_WAIT_UNTIL',
            'SEQ_WAIT_UNTIL_AND',
            'SEQ_WAIT_UNTIL_OR',
            'SEQ_WAIT_UNTIL_TIMEOUT',
            'SEQ_END_WAIT_UNTIL',
            'SEQ_WHILE_LOOP',
            'SEQ_WHILE_LOOP_AND',
            'SEQ_WHILE_LOOP_BREAK',
            'SEQ_WHILE_LOOP_CONTINUE',
            'SEQ_WHILE_LOOP_OR',
            'SEQ_END_WHILE_LOOP',
        }        

# fresh/mission_config.py
#from tts_fresh.mission_base import MissionConfigBase

# 1. The Global Variable (The "Registry")
_ACTIVE_MISSION: MissionConfigBase = None

def set_active_mission(config_instance: MissionConfigBase):
    """
    Sets the global mission configuration instance for the current execution.
    This should be called once at initialization to register mission-specific behavior.

    :param config_instance: An instance of a MissionConfigBase subclass.
    :type config_instance: MissionConfigBase
    :return: None
    """
    global _ACTIVE_MISSION
    _ACTIVE_MISSION = config_instance

def _get_active():
    """
    Retrieves the currently registered mission configuration.
    If no mission has been set, it defaults to the testing configuration and prints a warning.

    :return: The active mission configuration instance.
    :rtype: MissionConfigBase
    """
    if _ACTIVE_MISSION is None:
        return CoreTestingMissionConfig()
    return _ACTIVE_MISSION


# ---------------------------------------------------------
# 2. The Bridge Functions 
# (These match the signatures your existing code expects)
#
# This is the part that used to be defined per mission
# in this file.
# ---------------------------------------------------------

def import_mission_fr_folder():
    """
    Bridge function to retrieve the mission-specific flight rules package.
    It queries the active mission configuration to find where the rules are located.

    :return: The package module for the mission's flight rules.
    :rtype: module
    """
    return _get_active().get_flight_rules_package()

def get_folder_name():
    """
    Bridge function to retrieve the current mission name.
    This is used to maintain compatibility with legacy code that expects a mission identifier.

    :return: The name of the active mission.
    :rtype: str
    """
    # Helper to keep existing logic working if needed
    return _get_active().mission_name

def get_io_method():
    """
    Bridge function to retrieve the appropriate sequence parsing method.
    It ensures the correct I/O logic is used based on the active mission.

    :return: The I/O callable for reading sequence files.
    :rtype: callable
    """
    return _get_active().get_io_method()

def get_default_config_file_path():
    """
    Bridge function to retrieve the path for the default configuration file.
    The path is sourced from the active mission configuration.

    :return: The file path to the mission's default config.
    :rtype: str
    """
    return _get_active().get_default_config_file_path()

def get_fr_criticality_from_id(fr_id):
    """
    Bridge function to parse criticality from a rule ID using mission-specific logic.
    It delegates the string parsing to the active mission configuration instance.

    :param fr_id: The flight rule identifier string.
    :type fr_id: str
    :return: The parsed criticality string.
    :rtype: str
    """
    return _get_active().get_fr_criticality_from_id(fr_id)

def get_seq_file_extension():
    """
    Bridge function to retrieve the expected sequence file extension.
    This helps the tool identify valid input files for the current mission.

    :return: The extension or glob pattern.
    :rtype: str
    """
    return _get_active().get_seq_file_extension()

def get_testing_cmd_dict_path():
    """
    Bridge function to retrieve the command dictionary path for the current mission.
    This dictionary is critical for validating command stems and arguments.

    :return: The path to the command dictionary.
    :rtype: pathlib.Path
    """
    return _get_active().get_testing_cmd_dict_path()

def get_control_flow_directives():
    return _get_active().get_control_flow_directives()