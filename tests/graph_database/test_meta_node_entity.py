import pytest
import pandas as pd
from loguru import logger

from workflow.scripts.utils.general import neo4j_connect
from tests.utils import group_props_by_type, schema_type_mapping
from tests.utils.load_schema import meta_node_names, meta_node_dict

META_NODE_QUERY_TEMPLATE = """
    MATCH (n:{meta_node})
    RETURN n LIMIT 500;
"""
META_NODE_META_PROPS = {"_id", "_name", "_source"}


@pytest.fixture(scope="class", params=meta_node_names)
def meta_node(request):
    return request.param


@pytest.fixture(scope="class")
def meta_node_df(meta_node):
    query = META_NODE_QUERY_TEMPLATE.format(meta_node=meta_node)
    driver = neo4j_connect()
    session = driver.session()
    data = session.run(query).data()
    df = pd.json_normalize(data)
    return df


@pytest.fixture(scope="class")
def sample_keys(meta_node_df):
    return set(meta_node_df.columns)


@pytest.fixture(scope="class")
def schema_defn(meta_node):
    schema_defn = meta_node_dict[meta_node]
    return schema_defn


@pytest.fixture(scope="class")
def scalar_props(schema_defn, sample_keys):
    defined_scalar_props, defined_array_props = group_props_by_type(
        schema_defn, column_prefix="n."
    )
    scalar_props = {
        k: v for k, v in defined_scalar_props.items() if {k}.issubset(sample_keys)
    }
    return scalar_props


@pytest.fixture(scope="class")
def array_props(schema_defn, sample_keys):
    defined_scalar_props, defined_array_props = group_props_by_type(
        schema_defn, column_prefix="n."
    )
    array_props = {
        k: v for k, v in defined_array_props.items() if {k}.issubset(sample_keys)
    }
    return array_props


class TestMetaNodeItem:
    def test_meta_props_exist(self, sample_keys):
        logger.info(sample_keys)
        meta_props = set([f"n.{_}" for _ in META_NODE_META_PROPS])
        assert meta_props.issubset(sample_keys)

    def test_required_props_exist(self, schema_defn, sample_keys):
        required_props = set([f"n.{_}" for _ in schema_defn["required"]])
        logger.info(f"required_props: {required_props}")
        logger.info(f"sample_keys: {sample_keys}")
        assert required_props.issubset(sample_keys)

    def test_scalar_props_conform(self, scalar_props, meta_node_df):
        for k, v in scalar_props.items():
            expected_type = schema_type_mapping[v["type"]]
            logger.info(f"{k}: {expected_type}")
            series = meta_node_df[k].dropna()
            logger.info(series)
            # special handling of nullable integer
            if v["type"] == "integer":
                series = series.astype(pd.Int64Dtype())
            type_not_conform = series.apply(
                lambda _: not isinstance(_, expected_type)
            ).pipe(lambda s: sum(s))
            assert not bool(type_not_conform)

    def test_array_props_conform(self, array_props, meta_node_df):
        for k, v in array_props.items():
            expected_type = schema_type_mapping[v["items"]["type"]]
            logger.info(f"{k}: {expected_type}")
            parent_is_not_list = (
                meta_node_df[k]
                .dropna()
                .apply(lambda _: not isinstance(_, list))
                .pipe(lambda s: sum(s))
            )
            assert not bool(parent_is_not_list)
            series = pd.Series(
                [_ for sub_list in meta_node_df[k].dropna().tolist() for _ in sub_list]
            )
            logger.info(series)
            # special handling of nullable integer
            if v["type"] == "integer":
                series = series.astype(pd.int64dtype())
            type_not_conform = series.apply(
                lambda _: not isinstance(_, expected_type)
            ).pipe(lambda s: sum(s))
            assert not bool(type_not_conform)
