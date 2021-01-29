from typing import Dict, Tuple, Optional

schema_type_mapping = {
    "string": str,
    "float": float,
    "integer": int,
}


def is_prop_array(prop: Dict) -> bool:
    return prop["type"] == "array"


def group_props_by_type(entity: Dict, column_prefix: Optional[str], is_rel: bool = False) -> Tuple:
    """
    Group props by scalar and array props.
    If `is_rel`, remove source and target from props
    """
    properties = entity["properties"]
    scalar_props = {k: v for k, v in properties.items() if not is_prop_array(v)}
    array_props = {k: v for k, v in properties.items() if is_prop_array(v)}
    if column_prefix is not None:
        scalar_props = {f"{column_prefix}{k}": v for k, v in scalar_props.items()}
        array_props = {f"{column_prefix}{k}": v for k, v in array_props.items()}
    if is_rel:
        scalar_props = {
            k: v for k, v in scalar_props.items() if k not in ["source", "target"]
        }
    res = (scalar_props, array_props)
    return res


def meta_rel_get_source(rel: Dict) -> str:
    return rel["properties"]["source"]["type"]


def meta_rel_get_target(rel: Dict) -> str:
    return rel["properties"]["target"]["type"]
