#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Common Action Shortcut System Module

This module provides a system for defining, managing, and executing common
user actions or sequences of actions as shortcuts.
It follows the mandatory changelog protocol.
"""

import logging
from typing import Callable, Dict, Any, List, Optional

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/common_action_shortcut_system.log'
)
logger = logging.getLogger(__name__)

class ShortcutRegistry:
    """
    Manages the registration of common action shortcuts.
    """
    def __init__(self):
        self._shortcuts: Dict[str, Dict[str, Any]] = {}
        logger.info("ShortcutRegistry initialized.")

    def register_shortcut(self, name: str, action: Callable[..., Any], description: str = "", default_args: Optional[Dict[str, Any]] = None) -> bool:
        """
        Registers a new shortcut.

        Args:
            name (str): The unique name for the shortcut.
            action (Callable[..., Any]): The function/method to call when the shortcut is executed.
            description (str): A brief description of what the shortcut does.
            default_args (Optional[Dict[str, Any]]): Default arguments for the action.

        Returns:
            bool: True if registration was successful, False if the name already exists.
        """
        if name in self._shortcuts:
            logger.warning(f"Shortcut '{name}' already registered. Registration failed.")
            return False
        self._shortcuts[name] = {
            'action': action,
            'description': description,
            'default_args': default_args or {}
        }
        logger.info(f"Shortcut '{name}' registered successfully.")
        return True

    def unregister_shortcut(self, name: str) -> bool:
        """
        Unregisters an existing shortcut.

        Args:
            name (str): The name of the shortcut to unregister.

        Returns:
            bool: True if unregistration was successful, False if the shortcut was not found.
        """
        if name not in self._shortcuts:
            logger.warning(f"Shortcut '{name}' not found. Unregistration failed.")
            return False
        del self._shortcuts[name]
        logger.info(f"Shortcut '{name}' unregistered successfully.")
        return True

    def get_shortcut_details(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves details for a specific shortcut.

        Args:
            name (str): The name of the shortcut.

        Returns:
            Optional[Dict[str, Any]]: Shortcut details if found, else None.
        """
        return self._shortcuts.get(name)

    def list_shortcuts(self) -> Dict[str, str]:
        """
        Lists all registered shortcuts with their descriptions.

        Returns:
            Dict[str, str]: A dictionary where keys are shortcut names and values are descriptions.
        """
        return {name: details['description'] for name, details in self._shortcuts.items()}

class ActionExecutor:
    """
    Executes registered shortcuts.
    """
    def __init__(self, registry: ShortcutRegistry):
        self.registry = registry
        logger.info("ActionExecutor initialized.")

    def execute(self, name: str, **kwargs: Any) -> Any:
        """
        Executes a registered shortcut by its name.

        Args:
            name (str): The name of the shortcut to execute.
            **kwargs: Arguments to pass to the shortcut's action, overriding defaults.

        Returns:
            Any: The result of the shortcut's action execution.

        Raises:
            ValueError: If the shortcut is not found.
            Exception: If the shortcut action raises an exception during execution.
        """
        shortcut_details = self.registry.get_shortcut_details(name)
        if not shortcut_details:
            logger.error(f"Shortcut '{name}' not found for execution.")
            raise ValueError(f"Shortcut '{name}' not found.")

        action = shortcut_details['action']
        final_args = {**shortcut_details['default_args'], **kwargs} # kwargs override defaults

        logger.info(f"Executing shortcut '{name}' with arguments: {final_args}")
        try:
            result = action(**final_args)
            logger.info(f"Shortcut '{name}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Error executing shortcut '{name}': {e}", exc_info=True)
            raise

class CommonActionShortcutSystem:
    """
    Main class for the common action shortcut system.
    Implements the mandatory changelog protocol.
    """
    def __init__(self):
        self.changelog_engine = ChangelogEngine()
        self.registry = ShortcutRegistry()
        self.executor = ActionExecutor(self.registry)
        self._update_changelog(
            action_summary="CommonActionShortcutSystem initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="System ready, provides ShortcutRegistry and ActionExecutor.",
            changes_made=["Initialized internal state, defined ShortcutRegistry and ActionExecutor classes."],
            files_affected=[{"file_path": "scripts/ui/common_action_shortcut_system.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Designed a registry for actions and an executor to run them, allowing for dynamic shortcut management."]
        )
        logger.info("CommonActionShortcutSystem initialized.")

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

# Example Usage:
if __name__ == "__main__":
    shortcut_system = CommonActionShortcutSystem()

    # Define some example actions
    def greet(name: str, greeting: str = "Hello"):
        message = f"{greeting}, {name}!"
        print(message)
        return message

    def show_system_status(service: str = "all"):
        status = f"System status for '{service}': OK"
        print(status)
        return status

    # Register shortcuts
    shortcut_system.registry.register_shortcut(
        name="greet_user", 
        action=greet, 
        description="Greets a user by name.",
        default_args={'name': 'Guest'}
    )
    shortcut_system.registry.register_shortcut(
        name="check_status", 
        action=show_system_status, 
        description="Shows the system status for a service."
    )

    print("\nAvailable shortcuts:", shortcut_system.registry.list_shortcuts())

    # Execute shortcuts
    print("\nExecuting 'greet_user' (default args):")
    shortcut_system.executor.execute("greet_user")

    print("\nExecuting 'greet_user' (custom args):")
    shortcut_system.executor.execute("greet_user", name="Alice", greeting="Hi")

    print("\nExecuting 'check_status' (default service):")
    shortcut_system.executor.execute("check_status")

    print("\nExecuting 'check_status' (specific service):")
    shortcut_system.executor.execute("check_status", service="database")

    # Example of trying to execute a non-existent shortcut
    try:
        print("\nTrying to execute non_existent_shortcut:")
        shortcut_system.executor.execute("non_existent_shortcut")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    shortcut_system._update_changelog(
        action_summary="Demonstrated shortcut registration and execution.",
        action_type="Demo Execution",
        previous_state="System initialized",
        current_state="Demo completed",
        changes_made=["Registered 'greet_user' and 'check_status' shortcuts, executed them with various arguments."],
        files_affected=[{"file_path": "logs/common_action_shortcut_system.log", "change_type": "APPENDED", "impact_level": "LOW"}],
        technical_decisions=["Showcased dynamic registration and execution of callables as shortcuts."]
    )

