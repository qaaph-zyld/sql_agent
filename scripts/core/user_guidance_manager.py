#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User Guidance Manager Module

This module provides a system for managing and displaying user guidance, tips, and help messages.
It follows the mandatory changelog protocol.
"""

import logging
import os
import json # Added for loading guidance from JSON
from typing import Any, Dict, List, Optional

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/user_guidance_manager.log'
)
logger = logging.getLogger(__name__)

GUIDANCE_CONFIG_FILE = os.path.join("config", "guidance_messages.json")

class UserGuidanceManager:
    """
    Manages the storage and retrieval of user guidance messages.
    """
    def __init__(self, changelog_engine: ChangelogEngine):
        self.changelog_engine = changelog_engine
        self._guidance_messages: Dict[str, str] = {}
        
        loaded_from_file_count = self._load_guidance_from_file(GUIDANCE_CONFIG_FILE)
        
        initialization_summary = "UserGuidanceManager initialized."
        current_state_details = []
        changes_made_details = ["Initialized internal guidance message dictionary."]
        files_affected_details = [
            {"file_path": "scripts/core/user_guidance_manager.py", "change_type": "MODIFIED", "impact_level": "MEDIUM"}
        ]
        technical_decisions_details = ["Using an in-memory dictionary, potentially pre-populated from a config file."]

        if loaded_from_file_count > 0:
            initialization_summary += f" Loaded {loaded_from_file_count} messages from {GUIDANCE_CONFIG_FILE}."
            current_state_details.append(f"Loaded {loaded_from_file_count} messages from {GUIDANCE_CONFIG_FILE}.")
            changes_made_details.append(f"Successfully loaded guidance from {GUIDANCE_CONFIG_FILE}.")
            files_affected_details.append({"file_path": GUIDANCE_CONFIG_FILE, "change_type": "READ", "impact_level": "LOW"})
        else:
            current_state_details.append(f"{GUIDANCE_CONFIG_FILE} not found or empty/invalid. Using only programmatically registered guidance.")
            technical_decisions_details.append(f"Configuration file {GUIDANCE_CONFIG_FILE} was not loaded (not found, empty, or invalid format).")

        logger.info(initialization_summary)
        self._update_changelog(
            action_summary=initialization_summary,
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state=f"System ready. {' '.join(current_state_details)}",
            changes_made=changes_made_details,
            files_affected=files_affected_details,
            technical_decisions=technical_decisions_details
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

    def _load_guidance_from_file(self, filepath: str) -> int:
        """
        Loads guidance messages from a JSON file into the internal store.
        Messages from the file will be merged with, and potentially overridden by, programmatically registered messages.

        Args:
            filepath (str): The path to the JSON file.

        Returns:
            int: The number of guidance messages successfully loaded from the file.
        """
        try:
            if not os.path.exists(filepath):
                logger.info(f"Guidance configuration file not found: {filepath}")
                return 0
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                logger.error(f"Invalid format in guidance file {filepath}. Expected a JSON object.")
                return 0
            
            loaded_count = 0
            for key, value in data.items():
                if isinstance(value, str):
                    self._guidance_messages[key] = value
                    loaded_count += 1
                else:
                    logger.warning(f"Skipping non-string value for key '{key}' in {filepath}.")
            
            if loaded_count > 0:
                logger.info(f"Successfully loaded {loaded_count} guidance messages from {filepath}.")
            else:
                logger.info(f"No valid guidance messages found or loaded from {filepath}.")
            return loaded_count
        except FileNotFoundError:
            logger.info(f"Guidance configuration file not found: {filepath}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from guidance file {filepath}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading guidance from {filepath}: {e}")
        return 0

    def register_guidance(self, context_key: str, message: str) -> None:
        """
        Registers or updates a guidance message for a given context key.

        Args:
            context_key (str): A unique key representing the context (e.g., 'error_sql_syntax', 'feature_x_tip').
            message (str): The guidance message to display.
        """
        previous_message = self._guidance_messages.get(context_key)
        self._guidance_messages[context_key] = message
        logger.info(f"Guidance registered/updated for key '{context_key}': '{message}'")
        self._update_changelog(
            action_summary=f"Guidance for '{context_key}' registered/updated",
            action_type="Guidance Management",
            previous_state=f"Guidance for '{context_key}': {previous_message if previous_message else 'None'}",
            current_state=f"Guidance for '{context_key}': {message}",
            changes_made=[f"Stored new guidance message for '{context_key}'."],
            files_affected=[], # In-memory change, no direct file affected by this specific action
            technical_decisions=["Updated in-memory guidance store."]
        )

    def get_guidance(self, context_key: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Retrieves a guidance message for a given context key.

        Args:
            context_key (str): The key for which to retrieve guidance.

        Returns:
            Optional[str]: The guidance message, or None if not found.
        """
        message = self._guidance_messages.get(context_key)
        if message:
            if params:
                try:
                    formatted_message = message.format(**params)
                    logger.info(f"Guidance retrieved and formatted for key '{context_key}': '{formatted_message}'")
                    return formatted_message
                except KeyError as e:
                    logger.warning(f"Missing parameter '{e}' for guidance key '{context_key}'. Returning unformatted message. Original message: '{message}'")
                    return message # Return unformatted message if a key is missing
                except Exception as e:
                    logger.error(f"Error formatting message for key '{context_key}' with params {params}: {e}. Returning unformatted message. Original message: '{message}'")
                    return message # Return unformatted message on other formatting errors
            else:
                logger.info(f"Guidance retrieved for key '{context_key}' (no params provided): '{message}'")
                return message
        else:
            logger.warning(f"No guidance found for key '{context_key}'.")
            return None

    def remove_guidance(self, context_key: str) -> bool:
        """
        Removes a guidance message for a given context key.

        Args:
            context_key (str): The key for the guidance to remove.

        Returns:
            bool: True if guidance was removed, False if key not found.
        """
        if context_key in self._guidance_messages:
            removed_message = self._guidance_messages.pop(context_key)
            logger.info(f"Guidance removed for key '{context_key}'. Message was: '{removed_message}'")
            self._update_changelog(
                action_summary=f"Guidance for '{context_key}' removed",
                action_type="Guidance Management",
                previous_state=f"Guidance for '{context_key}' existed.",
                current_state=f"Guidance for '{context_key}' removed.",
                changes_made=[f"Removed guidance message for '{context_key}'."],
                files_affected=[],
                technical_decisions=["Removed entry from in-memory guidance store."]
            )
            return True
        logger.warning(f"Attempted to remove non-existent guidance for key '{context_key}'.")
        return False

# Example Usage:
if __name__ == "__main__":
    class DummyChangelogEngine:
        def update_changelog(self, **kwargs):
            print(f"CHANGELOG_UPDATE (UserGuidanceManager): {kwargs.get('action_summary')}")

    changelog_engine_instance = DummyChangelogEngine()

    # Ensure 'logs' directory exists for the logger.
    # The 'config' directory and 'guidance_messages.json' are assumed to exist
    # as per previous setup steps (e.g., creation of config/guidance_messages.json).
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # No longer creating a dummy config/guidance_messages.json here.
    # The UserGuidanceManager will attempt to load the primary config/guidance_messages.json.
    
    ugm = UserGuidanceManager(changelog_engine_instance)

    print("\n--- Example: Retrieving Guidance (loaded from config/guidance_messages.json) ---")
    # Test with a key known to be in the main config/guidance_messages.json
    guidance_welcome = ugm.get_guidance("info_welcome")
    print(f"Guidance for 'info_welcome': {guidance_welcome}")
    assert guidance_welcome == "Welcome to the SQL Agent! Type 'help' to see available commands or 'examples' for common use cases.", \
        f"Assertion failed for 'info_welcome'. Expected specific message, got: {guidance_welcome}"

    guidance_sql_syntax_initial = ugm.get_guidance("error_sql_syntax")
    print(f"Initial guidance for 'error_sql_syntax': {guidance_sql_syntax_initial}")
    assert guidance_sql_syntax_initial is not None, "'error_sql_syntax' should be loaded from file."

    print("\n--- Example: Retrieving Parameterized Guidance ---")
    # Get parameterized message with all parameters
    conn_params = {"db_name": "sales_db", "host": "prod_server_01"}
    guidance_conn_failed_formatted = ugm.get_guidance("error_connection_failed", params=conn_params)
    expected_conn_failed_formatted = "Failed to connect to the database 'sales_db' on host 'prod_server_01'. Ensure the server is running and connection details (port, username, password) are correct."
    print(f"Formatted 'error_connection_failed': {guidance_conn_failed_formatted}")
    assert guidance_conn_failed_formatted == expected_conn_failed_formatted, "Parameterized message not formatted as expected."

    # Get parameterized message without parameters (should return raw message)
    guidance_conn_failed_raw = ugm.get_guidance("error_connection_failed")
    expected_conn_failed_raw = "Failed to connect to the database '{db_name}' on host '{host}'. Ensure the server is running and connection details (port, username, password) are correct."
    print(f"Raw 'error_connection_failed' (no params): {guidance_conn_failed_raw}")
    assert guidance_conn_failed_raw == expected_conn_failed_raw, "Raw parameterized message not returned as expected."

    # Get parameterized message with missing parameters (should return raw message and log warning)
    conn_params_missing = {"db_name": "inventory_db"} # Missing 'host'
    guidance_conn_failed_missing_param = ugm.get_guidance("error_connection_failed", params=conn_params_missing)
    print(f"'error_connection_failed' (missing param 'host'): {guidance_conn_failed_missing_param}")
    assert guidance_conn_failed_missing_param == expected_conn_failed_raw, "Parameterized message with missing param not handled as expected."

    print("\n--- Example: Registering New Guidance (programmatically) ---")
    new_guidance_key = "tip_custom_aggregation"
    new_guidance_message = "When performing aggregations, ensure your GROUP BY clause includes all non-aggregated columns from the SELECT list."
    ugm.register_guidance(new_guidance_key, new_guidance_message)
    retrieved_new_guidance = ugm.get_guidance(new_guidance_key)
    print(f"Guidance for '{new_guidance_key}': {retrieved_new_guidance}")
    assert retrieved_new_guidance == new_guidance_message, "Failed to retrieve programmatically registered guidance."

    print("\n--- Example: Updating Existing Guidance (one loaded from file) ---")
    updated_sql_syntax_message = "SQL Syntax Error: Please review your query for typos, missing commas, or incorrect keyword usage. Refer to SQL documentation if needed (updated programmatically)."
    ugm.register_guidance("error_sql_syntax", updated_sql_syntax_message)
    retrieved_updated_sql_syntax = ugm.get_guidance("error_sql_syntax")
    print(f"Updated guidance for 'error_sql_syntax': {retrieved_updated_sql_syntax}")
    assert retrieved_updated_sql_syntax == updated_sql_syntax_message, "Failed to update guidance message loaded from file."
    assert retrieved_updated_sql_syntax != guidance_sql_syntax_initial, "Updated message should differ from initial file-loaded message."

    print("\n--- Example: Retrieving Non-existent Guidance ---")
    guidance_non_existent = ugm.get_guidance("this_key_definitely_does_not_exist_12345")
    print(f"Guidance for 'this_key_definitely_does_not_exist_12345': {guidance_non_existent}")
    assert guidance_non_existent is None, "Retrieving a non-existent key should return None."

    print("\n--- Example: Removing Guidance ---")
    # Remove a message originally loaded from the file (e.g., 'tip_performance_select_star')
    key_to_remove_from_file = "tip_performance_select_star"
    print(f"Attempting to remove '{key_to_remove_from_file}' (expected to be loaded from file).")
    initial_value_before_remove = ugm.get_guidance(key_to_remove_from_file)
    assert initial_value_before_remove is not None, f"'{key_to_remove_from_file}' should exist before removal."
    ugm.remove_guidance(key_to_remove_from_file)
    guidance_after_removal_file = ugm.get_guidance(key_to_remove_from_file)
    print(f"Guidance for '{key_to_remove_from_file}' after removal: {guidance_after_removal_file}")
    assert guidance_after_removal_file is None, f"'{key_to_remove_from_file}' should be None after removal."

    # Remove a programmatically added message
    print(f"Attempting to remove '{new_guidance_key}' (programmatically added).")
    ugm.remove_guidance(new_guidance_key)
    guidance_after_removal_programmatic = ugm.get_guidance(new_guidance_key)
    print(f"Guidance for '{new_guidance_key}' after removal: {guidance_after_removal_programmatic}")
    assert guidance_after_removal_programmatic is None, f"'{new_guidance_key}' should be None after removal."

    print("\n--- User Guidance Manager Demonstration Complete ---")
