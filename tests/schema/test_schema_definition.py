import pytest

from tests.utils.models import MetaNode, MetaRel

from tests.utils.load_schema import (
    meta_node_dict,
    meta_rel_dict,
    meta_node_names,
    meta_rel_names,
)


@pytest.mark.parametrize("meta_node_name", meta_node_names)
def test_meta_node_definition(meta_node_name):
    raw = meta_node_dict[meta_node_name]
    parsed = MetaNode(**raw)
    return parsed


@pytest.mark.parametrize("meta_rel_name", meta_rel_names)
def test_meta_rel_definition(meta_rel_name):
    raw = meta_rel_dict[meta_rel_name]
    parsed = MetaRel(**raw)
    return parsed
