#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Transaction Rollback Manager Module

This module provides a manager to handle a sequence of operations as a transaction,
allowing for rollback if an error occurs.
It follows the mandatory changelog protocol.
"""

import logging
from typing import List, Callable, Tuple, Dict, Any, Optional

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/transaction_rollback_manager.log'
)
logger = logging.getLogger(__name__)

class TransactionRollbackManager:
    """
    Manages a list of operations that can be rolled back in case of an error.
    """
    def __init__(self, changelog_engine: ChangelogEngine):
        self.changelog_engine = changelog_engine
        self._rollback_stack: List[Tuple[Callable, Tuple, Dict]] = []
        self._transaction_active = False
        logger.info("TransactionRollbackManager initialized.")
        self._update_changelog(
            action_summary="TransactionRollbackManager initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Manager ready to handle transactions.",
            changes_made=["Initialized internal state for rollback stack."],
            files_affected=[{"file_path": "scripts/core/transaction_rollback_manager.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Established a basic structure for transaction management. Placed in core due to directory creation issues."]
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

    def begin_transaction(self) -> None:
        """Starts a new transaction block."""
        if self._transaction_active:
            logger.warning("Attempted to begin a new transaction while one is already active. Clearing existing stack.")
            self._rollback_stack.clear()
        self._transaction_active = True
        self._rollback_stack.clear() # Ensure stack is clean for the new transaction
        logger.info("Transaction begun.")
        self._update_changelog(
            action_summary="Transaction begun", action_type="Transaction Management",
            previous_state="No active transaction or previous transaction ended", current_state="Transaction active, rollback stack cleared",
            changes_made=["Set transaction active flag, cleared rollback stack."],
            files_affected=[], technical_decisions=["Ensures a clean state for new transactions."]
        )

    def register_rollback_action(self, rollback_action: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Registers a rollback action to be executed if rollback is called.
        The action should undo a previously performed operation.

        Args:
            rollback_action (Callable): The function/method to call for rollback.
            *args: Positional arguments for the rollback_action.
            **kwargs: Keyword arguments for the rollback_action.
        """
        if not self._transaction_active:
            logger.error("Cannot register rollback action: No active transaction.")
            # Optionally raise an error here
            return
        
        self._rollback_stack.append((rollback_action, args, kwargs))
        action_name = getattr(rollback_action, '__name__', 'Unnamed rollback action')
        logger.info(f"Rollback action '{action_name}' registered.")
        # Changelog for every registered action might be too verbose. Consider summarizing on commit/rollback.

    def commit(self) -> None:
        """Commits the current transaction, clearing the rollback stack."""
        if not self._transaction_active:
            logger.warning("Commit called but no active transaction.")
            return
        
        self._rollback_stack.clear()
        self._transaction_active = False
        logger.info("Transaction committed.")
        self._update_changelog(
            action_summary="Transaction committed", action_type="Transaction Management",
            previous_state="Transaction active with registered rollback actions", current_state="Transaction ended, rollback stack cleared",
            changes_made=["Cleared rollback stack, set transaction inactive."],
            files_affected=[], technical_decisions=["Finalizes the transaction successfully."]
        )

    def rollback(self) -> None:
        """Rolls back the current transaction by executing registered actions in reverse order."""
        if not self._transaction_active:
            logger.warning("Rollback called but no active transaction.")
            return

        logger.info(f"Rolling back transaction. {len(self._rollback_stack)} actions to perform.")
        num_actions = len(self._rollback_stack)
        rolled_back_actions_summary = []

        while self._rollback_stack:
            action, args, kwargs = self._rollback_stack.pop()
            action_name = getattr(action, '__name__', 'Unnamed rollback action')
            try:
                logger.info(f"Executing rollback action: {action_name}")
                action(*args, **kwargs)
                rolled_back_actions_summary.append(f"Successfully rolled back: {action_name}")
            except Exception as e:
                logger.error(f"Error during rollback of action {action_name}: {e}", exc_info=True)
                rolled_back_actions_summary.append(f"Failed to roll back: {action_name} (Error: {e})")
                # Decide if we should continue rolling back other actions or stop.
                # For now, continue to attempt other rollbacks.
        
        self._transaction_active = False
        logger.info("Transaction rollback completed.")
        self._update_changelog(
            action_summary="Transaction rolled back", action_type="Transaction Management",
            previous_state="Transaction active, error occurred or rollback requested", current_state="Transaction ended, rollback actions attempted",
            changes_made=[
                f"{num_actions} rollback actions attempted.",
                "Rollback stack cleared, transaction set inactive."
            ] + rolled_back_actions_summary,
            files_affected=[{"file_path": "logs/transaction_rollback_manager.log", "change_type": "APPENDED", "impact_level": "HIGH"}],
            technical_decisions=["Attempts to undo operations in reverse order. Logs errors during rollback."]
        )

# Example Usage:
if __name__ == "__main__":
    class DummyChangelogEngine:
        def update_changelog(self, **kwargs):
            print(f"CHANGELOG_UPDATE (TransactionRollbackManager): {kwargs.get('action_summary')}")

    changelog_engine_instance = DummyChangelogEngine()
    manager = TransactionRollbackManager(changelog_engine_instance)

    # --- Example 1: Successful Transaction ---
    print("\n--- Example 1: Successful Transaction ---")
    state = {'value': 0, 'files_created': []}

    def operation1(val_to_add):
        state['value'] += val_to_add
        print(f"Operation 1: Added {val_to_add}. State value: {state['value']}")
    def rollback_op1(val_to_add):
        state['value'] -= val_to_add
        print(f"Rollback Op 1: Subtracted {val_to_add}. State value: {state['value']}")

    def operation2_create_file(filename):
        state['files_created'].append(filename)
        print(f"Operation 2: Simulated creating file '{filename}'. Files: {state['files_created']}")
    def rollback_op2_delete_file(filename):
        if filename in state['files_created']:
            state['files_created'].remove(filename)
        print(f"Rollback Op 2: Simulated deleting file '{filename}'. Files: {state['files_created']}")

    manager.begin_transaction()
    operation1(10)
    manager.register_rollback_action(rollback_op1, 10)
    operation2_create_file("temp_file.txt")
    manager.register_rollback_action(rollback_op2_delete_file, "temp_file.txt")
    manager.commit()
    print(f"Final state after commit: {state}")

    # --- Example 2: Transaction with Rollback ---
    print("\n--- Example 2: Transaction with Rollback ---")
    state = {'value': 0, 'files_created': []} # Reset state

    manager.begin_transaction()
    operation1(5)
    manager.register_rollback_action(rollback_op1, 5)
    operation2_create_file("another_temp.txt")
    manager.register_rollback_action(rollback_op2_delete_file, "another_temp.txt")
    print("Simulating an error before commit...")
    manager.rollback()
    print(f"Final state after rollback: {state}")

    # --- Example 3: Rollback with error in rollback action ---
    print("\n--- Example 3: Rollback with error in rollback action ---")
    state = {'value': 0, 'files_created': []} # Reset state
    def faulty_rollback(msg):
        print(f"Attempting faulty rollback: {msg}")
        raise ValueError("This rollback action itself failed!")

    manager.begin_transaction()
    operation1(20)
    manager.register_rollback_action(rollback_op1, 20)
    operation2_create_file("faulty_file.txt")
    manager.register_rollback_action(faulty_rollback, "Trying to undo file creation") # This will fail
    operation1(3)
    manager.register_rollback_action(rollback_op1, 3)
    print("Simulating an error, triggering rollback with a faulty rollback action in stack...")
    manager.rollback()
    print(f"Final state after faulty rollback attempt: {state}")

    # --- Example 4: Simulated Data Processing Workflow ---
    print("\n--- Example 4: Simulated Data Processing Workflow ---")
    # This example simulates a workflow where a file is processed, and results are stored.
    # If storing results fails, the initial processing (e.g., creating a temp status file) should be undone.

    app_state = {'status_file': None, 'database_record_id': None}

    def create_status_file(transaction_id):
        app_state['status_file'] = f"processing_{transaction_id}_status.tmp"
        print(f"WORKFLOW: Created status file: {app_state['status_file']}")
        # In a real scenario, this would actually create a file.
        return True

    def delete_status_file(transaction_id):
        status_file_to_delete = f"processing_{transaction_id}_status.tmp"
        if app_state['status_file'] == status_file_to_delete:
            print(f"WORKFLOW_ROLLBACK: Deleted status file: {app_state['status_file']}")
            app_state['status_file'] = None
            # In a real scenario, this would delete the file.
        else:
            print(f"WORKFLOW_ROLLBACK: Status file {status_file_to_delete} not found or already deleted.")

    def store_results_in_db(data):
        # Simulate success or failure
        if "error" in data:
            print(f"WORKFLOW: Failed to store results in DB for data: {data}")
            raise ConnectionError("Simulated database connection error")
        app_state['database_record_id'] = hash(data) # Simulate getting a record ID
        print(f"WORKFLOW: Successfully stored results in DB. Record ID: {app_state['database_record_id']} for data: {data}")
        return app_state['database_record_id']

    def remove_results_from_db(record_id):
        if app_state['database_record_id'] == record_id:
            print(f"WORKFLOW_ROLLBACK: Removed results from DB. Record ID: {app_state['database_record_id']}")
            app_state['database_record_id'] = None
        else:
            print(f"WORKFLOW_ROLLBACK: DB Record ID {record_id} not found or already removed.")

    current_transaction_id = "tx123"
    data_to_process_success = "important_data_package_1"
    data_to_process_fail = "error_trigger_package_2"

    print("\nScenario 4.1: Successful processing workflow")
    manager.begin_transaction()
    try:
        create_status_file(current_transaction_id)
        manager.register_rollback_action(delete_status_file, current_transaction_id)

        record_id = store_results_in_db(data_to_process_success)
        # If store_results_in_db had its own complex rollback, it might use its own transaction
        # or register its rollback parts here if simple enough.
        # For this example, we assume a simple rollback action can be registered.
        manager.register_rollback_action(remove_results_from_db, record_id)

        manager.commit()
        print(f"WORKFLOW_END (Success): Final app_state: {app_state}")
    except Exception as e:
        print(f"WORKFLOW_ERROR: An error occurred - {e}. Initiating rollback.")
        manager.rollback()
        print(f"WORKFLOW_END (Rolled Back): Final app_state: {app_state}")

    # Reset state for next scenario
    app_state = {'status_file': None, 'database_record_id': None}
    current_transaction_id = "tx456"

    print("\nScenario 4.2: Processing workflow with failure")
    manager.begin_transaction()
    try:
        create_status_file(current_transaction_id)
        manager.register_rollback_action(delete_status_file, current_transaction_id)

        # This call will fail
        record_id = store_results_in_db(data_to_process_fail) 
        manager.register_rollback_action(remove_results_from_db, record_id)

        manager.commit() # This line won't be reached
        print(f"WORKFLOW_END (Success - Unexpected): Final app_state: {app_state}")
    except Exception as e:
        print(f"WORKFLOW_ERROR: An error occurred - {e}. Initiating rollback.")
        manager.rollback()
        print(f"WORKFLOW_END (Rolled Back): Final app_state: {app_state}")


    print("\n--- Transaction Rollback Manager Demonstration Complete ---")
