#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data Visualization Simplifier Module

This module provides utilities to simplify complex data structures for easier visualization.
It follows the mandatory changelog protocol.
"""

import logging
from typing import Dict, Any, List, Union, Optional

# Import changelog engine for mandatory protocol compliance
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/data_visualization_simplifier.log'
)
logger = logging.getLogger(__name__)

class DataFlattener:
    """
    Flattens nested dictionary or list structures.
    """
    def __init__(self):
        logger.info("DataFlattener initialized.")

    def flatten_dict(self, nested_dict: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        Flattens a nested dictionary.

        Args:
            nested_dict (Dict[str, Any]): The dictionary to flatten.
            parent_key (str): The prefix for the keys in the flattened dictionary (used in recursion).
            sep (str): Separator for joining parent and child keys.

        Returns:
            Dict[str, Any]: A flattened dictionary.
        """
        items = []
        for k, v in nested_dict.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Option 1: Store list as is
                # items.append((new_key, v))
                # Option 2: Flatten list items if they are dicts (more complex)
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self.flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}{sep}{i}", item))
            else:
                items.append((new_key, v))
        return dict(items)

    def flatten_list_of_dicts(self, list_of_dicts: List[Dict[str, Any]], parent_key_prefix: str = 'item', sep: str = '_') -> List[Dict[str, Any]]:
        """
        Flattens each dictionary in a list of dictionaries.
        Optionally, can be extended to handle lists of non-dicts or mixed types.

        Args:
            list_of_dicts (List[Dict[str, Any]]): A list where each element is a dictionary.
            parent_key_prefix (str): A prefix for keys if the list itself is part of a larger structure (conceptual).
            sep (str): Separator used by flatten_dict.

        Returns:
            List[Dict[str, Any]]: A list of flattened dictionaries.
        """
        return [self.flatten_dict(d, parent_key='', sep=sep) for d in list_of_dicts if isinstance(d, dict)]

class KeyFeatureSelector:
    """
    (Placeholder) Selects key features from a dataset for simplified visualization.
    """
    def __init__(self):
        logger.info("KeyFeatureSelector initialized (Placeholder).")

    def extract_key_features(self, data: Union[Dict[str, Any], List[Any]], top_n_keys: int = 5, criteria: Optional[str] = None) -> Any:
        """
        (Placeholder) Extracts the most important features/keys from data.

        Args:
            data (Union[Dict[str, Any], List[Any]]): The data to process.
            top_n_keys (int): Number of key features to attempt to extract (e.g., from a dict).
            criteria (Optional[str]): Placeholder for criteria (e.g., 'highest_variance', 'most_frequent').

        Returns:
            Any: A simplified representation focusing on key features.
        """
        logger.info(f"Extracting key features (top_n: {top_n_keys}, criteria: {criteria}) - Placeholder.")
        if isinstance(data, dict):
            # Example: return first N keys, or keys with highest variance if numerical, etc.
            return {k: data[k] for i, k in enumerate(data) if i < top_n_keys}
        elif isinstance(data, list):
            # Example: return a sample or summary of the list
            return data[:min(len(data), top_n_keys)]
        return data # Fallback

class DataVisualizationSimplifier:
    """
    Main class for data visualization simplification utilities.
    Implements the mandatory changelog protocol.
    """
    def __init__(self):
        self.changelog_engine = ChangelogEngine()
        self.flattener = DataFlattener()
        self.key_feature_selector = KeyFeatureSelector() # Placeholder
        self._update_changelog(
            action_summary="DataVisualizationSimplifier initialized",
            action_type="Component Initialization",
            previous_state="Not initialized",
            current_state="Simplifier ready, provides DataFlattener and KeyFeatureSelector (placeholder)",
            changes_made=["Initialized internal state, defined DataFlattener and placeholder KeyFeatureSelector"],
            files_affected=[{"file_path": "scripts/ui/data_visualization_simplifier.py", "change_type": "CREATED", "impact_level": "MEDIUM"}],
            technical_decisions=["Focused on data flattening for initial version. Key feature selection is a placeholder."]
        )
        logger.info("DataVisualizationSimplifier initialized.")

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
    simplifier = DataVisualizationSimplifier()

    # DataFlattener Example
    nested_example = {
        'user': {
            'id': 123,
            'name': 'John Doe',
            'address': {
                'street': '123 Main St',
                'city': 'Anytown'
            }
        },
        'orders': [
            {'order_id': 'A001', 'items': [{'item_id': 'X1', 'qty': 2}, {'item_id': 'Y2', 'qty': 1}]},
            {'order_id': 'A002', 'items': [{'item_id': 'Z3', 'qty': 5}]}
        ],
        'status': 'active'
    }
    print(f"Original nested dict: {nested_example}")
    flattened_dict = simplifier.flattener.flatten_dict(nested_example)
    print(f"Flattened dict: {flattened_dict}")

    list_of_nested_dicts = [
        {'a': 1, 'b': {'c': 2, 'd': 3}},
        {'a': 10, 'b': {'c': 20, 'd': {'e': 30}} }
    ]
    print(f"\nOriginal list of nested dicts: {list_of_nested_dicts}")
    flattened_list = simplifier.flattener.flatten_list_of_dicts(list_of_nested_dicts)
    print(f"Flattened list of dicts: {flattened_list}")

    # KeyFeatureSelector placeholder call
    complex_data_for_selection = {
        'feature1': 100, 'feature2': [1,2,3,4,5,6,7,8,9,10], 'feature3': 'very long string data',
        'feature4': {'sub1': 1, 'sub2': 2}, 'feature5': 0.5, 'feature6': True
    }
    key_features = simplifier.key_feature_selector.extract_key_features(complex_data_for_selection, top_n_keys=3)
    print(f"\nKey features (placeholder): {key_features}")

    simplifier._update_changelog(
        action_summary="Demonstrated data flattening and key feature selection (placeholder)",
        action_type="Demo Execution",
        previous_state="Simplifier initialized",
        current_state="Demo completed",
        changes_made=["Called flatten_dict, flatten_list_of_dicts, extract_key_features (placeholder)"],
        files_affected=[{"file_path": "logs/data_visualization_simplifier.log", "change_type": "APPENDED", "impact_level": "LOW"}],
        technical_decisions=["Showcased functionality. Actual impact depends on how simplified data is used in visualizations."]
    )

