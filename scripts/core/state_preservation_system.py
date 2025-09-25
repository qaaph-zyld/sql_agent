#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
State Preservation System Module

This module provides a system for saving and loading application/component state.
It follows the mandatory changelog protocol.
"""

import logging
import json
import os
import pickle # Using pickle for simplicity, consider security implications for real applications
from typing import Any, Dict, List, Optional

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/state_preservation_system.log'
)
logger = logging.getLogger(__name__)

DEFAULT_STATES_DIR = "states"

class StatePreservationSystem:
    """
    Manages saving and loading of application or component states.
    """
    def __init__(self, changelog_engine: ChangelogEngine, states_directory: str = DEFAULT_STATES_DIR):
        self.changelog_engine = changelog_engine
        self.states_directory = states_directory
        if not os.path.exists(self.states_directory):
            try:
                os.makedirs(self.states_directory)
                logger.info(f"Created states directory: {self.states_directory}")
            except OSError as e:
                logger.error(f"Error creating states directory {self.states_directory}: {e}")
                # Fallback or raise error if directory creation is critical
                raise

        logger.info(f"StatePreservationSystem initialized. States will be stored in: {self.states_directory}")
        self._update_changelog(
            action_summary="StatePreservationSystem initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state=f"System ready, states directory: {self.states_directory}",
            changes_made=["Initialized state directory check/creation."],
            files_affected=[
                {"file_path": "scripts/core/state_preservation_system.py", "change_type": "CREATED", "impact_level": "MEDIUM"},
                {"file_path": self.states_directory, "change_type": "ENSURED_EXISTS", "impact_level": "LOW"}
            ],
            technical_decisions=["Established basic structure for state saving/loading. Using pickle for initial simplicity."]
        )

    def _update_changelog(self, action_summary: str, action_type: str, previous_state: str, current_state: str, changes_made: List[str], files_affected: List[Dict[str, str]], technical_decisions: List[str]) -> None:
        self.changelog_engine.update_changelog(
            action_summary=action_summary,
            action_type=action_type,
            previous_state=previous_state,
            current_state=current_state,
            changes_made=changes_made,
            files_affected=files_affected,
            technical_decisions=technical_decisions
        )

    def _get_state_filepath(self, state_identifier: str, serialization_format: str = 'pickle') -> str:
        """Generates the full filepath for a given state identifier and format."""
        safe_identifier = "".join(c for c in state_identifier if c.isalnum() or c in ('_', '-'))
        extension = '.pkl' if serialization_format == 'pickle' else '.json'
        return os.path.join(self.states_directory, f"{safe_identifier}{extension}")

    def save_state(self, state_identifier: str, state_data: Any, serialization_format: str = 'pickle') -> bool:
        """
        Saves the given state_data under the state_identifier.
        Uses specified serialization format (pickle or json).

        Args:
            state_identifier (str): A unique name for the state.
            state_data (Any): The Python object to save.
            serialization_format (str): 'pickle' or 'json'. Defaults to 'pickle'.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        filepath = self._get_state_filepath(state_identifier, serialization_format)
        mode = 'wb' if serialization_format == 'pickle' else 'w'
        try:
            with open(filepath, mode) as f:
                if serialization_format == 'pickle':
                    pickle.dump(state_data, f)
                elif serialization_format == 'json':
                    json.dump(state_data, f, indent=4) # Added indent for readability
                else:
                    logger.error(f"Unsupported serialization format: {serialization_format}")
                    return False
            logger.info(f"State '{state_identifier}' ({serialization_format}) saved successfully to {filepath}.")
            self._update_changelog(
                action_summary=f"State '{state_identifier}' ({serialization_format}) saved", action_type="State Management",
                previous_state="State not saved or outdated", current_state=f"State saved to {filepath}",
                changes_made=[f"Serialized ({serialization_format}) and wrote state data for '{state_identifier}'."],
                files_affected=[{"file_path": filepath, "change_type": "CREATED_OR_MODIFIED", "impact_level": "HIGH"}],
                technical_decisions=[f"Used {serialization_format} for state serialization."]
            )
            return True
        except (pickle.PicklingError, TypeError, OSError) as e: # Added TypeError for json.dump
            logger.error(f"Error saving state '{state_identifier}' ({serialization_format}) to {filepath}: {e}", exc_info=True)
            self._update_changelog(
                action_summary=f"Failed to save state '{state_identifier}' ({serialization_format})", action_type="State Management Error",
                previous_state="Attempting to save state", current_state=f"Error during save: {e}",
                changes_made=[f"Failed to serialize/write state for '{state_identifier}' ({serialization_format})."],
                files_affected=[{"file_path": filepath, "change_type": "WRITE_ATTEMPT_FAILED", "impact_level": "HIGH"}],
                technical_decisions=[f"State save failed due to serialization ({serialization_format}) or I/O error."]
            )
            return False

    def load_state(self, state_identifier: str, serialization_format: str = 'pickle') -> Optional[Any]:
        """
        Loads the state identified by state_identifier using the specified format.

        Args:
            state_identifier (str): The unique name of the state to load.
            serialization_format (str): 'pickle' or 'json'. Defaults to 'pickle'.

        Returns:
            Optional[Any]: The loaded state data, or None if not found or error occurs.
        """
        filepath = self._get_state_filepath(state_identifier, serialization_format)
        mode = 'rb' if serialization_format == 'pickle' else 'r'
        if not os.path.exists(filepath):
            logger.warning(f"State file for '{state_identifier}' ({serialization_format}) not found at {filepath}.")
            return None
        
        try:
            with open(filepath, mode) as f:
                if serialization_format == 'pickle':
                    state_data = pickle.load(f)
                elif serialization_format == 'json':
                    state_data = json.load(f)
                else:
                    logger.error(f"Unsupported serialization format: {serialization_format}")
                    return None
            logger.info(f"State '{state_identifier}' ({serialization_format}) loaded successfully from {filepath}.")
            return state_data
        except (pickle.UnpicklingError, json.JSONDecodeError, OSError, EOFError) as e: # Added json.JSONDecodeError
            logger.error(f"Error loading state '{state_identifier}' ({serialization_format}) from {filepath}: {e}", exc_info=True)
            return None

    def delete_state(self, state_identifier: str, serialization_format: str = 'pickle') -> bool:
        """
        Deletes the state file associated with state_identifier and format.

        Args:
            state_identifier (str): The unique name of the state to delete.
            serialization_format (str): 'pickle' or 'json'. Defaults to 'pickle'.

        Returns:
            bool: True if deletion was successful or file didn't exist, False on error.
        """
        filepath = self._get_state_filepath(state_identifier, serialization_format)
        if not os.path.exists(filepath):
            logger.info(f"State file for '{state_identifier}' ({serialization_format}) not found at {filepath}. Nothing to delete.")
            return True
        
        try:
            os.remove(filepath)
            logger.info(f"State '{state_identifier}' ({serialization_format}) deleted successfully from {filepath}.")
            self._update_changelog(
                action_summary=f"State '{state_identifier}' ({serialization_format}) deleted", action_type="State Management",
                previous_state=f"State existed at {filepath}", current_state="State file removed",
                changes_made=[f"Deleted state file for '{state_identifier}' ({serialization_format})."],
                files_affected=[{"file_path": filepath, "change_type": "DELETED", "impact_level": "HIGH"}],
                technical_decisions=["Removed persistent state file."])
            return True
        except OSError as e:
            logger.error(f"Error deleting state '{state_identifier}' ({serialization_format}) from {filepath}: {e}", exc_info=True)
            self._update_changelog(
                action_summary=f"Failed to delete state '{state_identifier}' ({serialization_format})", action_type="State Management Error",
                previous_state="Attempting to delete state file", current_state=f"Error during delete: {e}",
                changes_made=[f"Failed to delete state file for '{state_identifier}' ({serialization_format})."],
                files_affected=[{"file_path": filepath, "change_type": "DELETE_ATTEMPT_FAILED", "impact_level": "HIGH"}],
                technical_decisions=["State delete failed due to I/O error."])
            return False

# Example Usage:
if __name__ == "__main__":
    class DummyChangelogEngine:
        def update_changelog(self, **kwargs):
            print(f"CHANGELOG_UPDATE (StatePreservationSystem): {kwargs.get('action_summary')}")

    changelog_engine_instance = DummyChangelogEngine()
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists(DEFAULT_STATES_DIR):
        os.makedirs(DEFAULT_STATES_DIR)

    sps = StatePreservationSystem(changelog_engine_instance)

    # --- Pickle Example ---
    state_id_pickle = "user_session_pickle"
    state_data_pickle = {"user_id": 789, "session_data": {"items": [1,2,3], "active": True}, "timestamp": "2025-06-05T10:00:00Z"}

    print(f"\n--- Example (Pickle): Saving state for '{state_id_pickle}' ---")
    sps.save_state(state_id_pickle, state_data_pickle, serialization_format='pickle')

    print(f"\n--- Example (Pickle): Loading state for '{state_id_pickle}' ---")
    loaded_data_pickle = sps.load_state(state_id_pickle, serialization_format='pickle')
    if loaded_data_pickle:
        print(f"Loaded data (Pickle) for '{state_id_pickle}': {loaded_data_pickle}")
        assert loaded_data_pickle == state_data_pickle, "Pickle loaded data does not match original!"
    else:
        print(f"Failed to load state (Pickle) for '{state_id_pickle}'.")

    # --- JSON Example ---
    state_id_json = "app_settings_json"
    state_data_json = {"version": "1.2.0", "features": {"featureA": True, "featureB": False}, "api_keys": None} 

    print(f"\n--- Example (JSON): Saving state for '{state_id_json}' ---")
    sps.save_state(state_id_json, state_data_json, serialization_format='json')

    print(f"\n--- Example (JSON): Loading state for '{state_id_json}' ---")
    loaded_data_json = sps.load_state(state_id_json, serialization_format='json')
    if loaded_data_json:
        print(f"Loaded data (JSON) for '{state_id_json}': {loaded_data_json}")
        assert loaded_data_json == state_data_json, "JSON loaded data does not match original!"
    else:
        print(f"Failed to load state (JSON) for '{state_id_json}'.")

    print(f"\n--- Example (Pickle): Deleting state '{state_id_pickle}' ---")
    sps.delete_state(state_id_pickle, serialization_format='pickle')
    loaded_data_pickle_after_delete = sps.load_state(state_id_pickle, serialization_format='pickle')
    if loaded_data_pickle_after_delete is None:
        print(f"Correctly confirmed '{state_id_pickle}' (Pickle) is deleted.")
    else:
        print(f"Error: '{state_id_pickle}' (Pickle) was found after deletion!")

    print(f"\n--- Example (JSON): Deleting state '{state_id_json}' ---")
    sps.delete_state(state_id_json, serialization_format='json')
    loaded_data_json_after_delete = sps.load_state(state_id_json, serialization_format='json')
    if loaded_data_json_after_delete is None:
        print(f"Correctly confirmed '{state_id_json}' (JSON) is deleted.")
    else:
        print(f"Error: '{state_id_json}' (JSON) was found after deletion!")
        
    print(f"\n--- Example: Loading non-existent state (Pickle) ---")
    non_existent_pickle = sps.load_state("non_existent_state_id", serialization_format='pickle')
    assert non_existent_pickle is None, "Should be None for non-existent pickle state"
    print("Correctly returned None for non-existent pickle state.")

    print(f"\n--- Example: Loading non-existent state (JSON) ---")
    non_existent_json = sps.load_state("non_existent_state_id", serialization_format='json')
    assert non_existent_json is None, "Should be None for non-existent json state"
    print("Correctly returned None for non-existent json state.")

    print("\n--- State Preservation System Demonstration (Pickle & JSON) Complete ---")
