from typing import Any, Dict


def set_attrs_from_dict(src_dict: Dict[str, Any], dist_obj: Any, /):
    for key, value in src_dict.items():
        if hasattr(dist_obj, key):
            setattr(dist_obj, key, value)
