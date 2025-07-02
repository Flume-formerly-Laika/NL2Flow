import copy
from typing import Any, Dict, List, Union

def diff_schemas(old: Any, new: Any, path: str = "") -> List[Dict[str, Any]]:
    """
    Recursively diff two schemas (dicts/lists/primitives).
    Returns a list of changes: additions, deletions, and modifications.
    Each change is a dict with keys: 'op' (add, remove, change), 'path', 'old', 'new'.
    """
    diffs = []
    if type(old) != type(new):
        diffs.append({
            "op": "change",
            "path": path,
            "old": old,
            "new": new
        })
        return diffs

    if isinstance(old, dict):
        old_keys = set(old.keys())
        new_keys = set(new.keys())
        for key in old_keys - new_keys:
            diffs.append({
                "op": "remove",
                "path": f"{path}/{key}" if path else key,
                "old": old[key],
                "new": None
            })
        for key in new_keys - old_keys:
            diffs.append({
                "op": "add",
                "path": f"{path}/{key}" if path else key,
                "old": None,
                "new": new[key]
            })
        for key in old_keys & new_keys:
            diffs.extend(diff_schemas(old[key], new[key], f"{path}/{key}" if path else key))
    elif isinstance(old, list):
        # For lists, do a simple index-wise diff (could be improved for order-insensitive cases)
        min_len = min(len(old), len(new))
        for i in range(min_len):
            diffs.extend(diff_schemas(old[i], new[i], f"{path}[{i}]"))
        for i in range(min_len, len(old)):
            diffs.append({
                "op": "remove",
                "path": f"{path}[{i}]",
                "old": old[i],
                "new": None
            })
        for i in range(min_len, len(new)):
            diffs.append({
                "op": "add",
                "path": f"{path}[{i}]",
                "old": None,
                "new": new[i]
            })
    else:
        if old != new:
            diffs.append({
                "op": "change",
                "path": path,
                "old": old,
                "new": new
            })
    return diffs

def diff_schema_versions(schema1: Dict[str, Any], schema2: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Public API: Diff two top-level schemas (dicts).
    Returns a list of structured changes.
    """
    return diff_schemas(schema1, schema2) 