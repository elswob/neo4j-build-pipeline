import pytest
import pandas as pd
from loguru import logger

from workflow.scripts.utils.general import neo4j_connect
from tests.utils import group_props_by_type, schema_type_mapping
from tests.utils.load_schema import meta_rel_names, meta_rel_dict, meta_node_names


META_REL_QUERY_TEMPLATE = """
    MATCH (source)-[rel:{meta_rel}]->(target)
    RETURN
        properties(rel) AS rel
    LIMIT 1000;
"""
SOURCE_TARGET_QUERY_TEMPLATE = """
    MATCH (source)-[rel:{meta_rel}]->(target)
    RETURN DISTINCT
        labels(source) AS source,
        labels(target) AS target
"""
META_REL_META_PROPS = {"_source"}


@pytest.fixture(scope="class", params=meta_rel_names)
def meta_rel(request):
    return request.param


@pytest.fixture(scope="class")
def meta_rel_df(meta_rel):
    query = META_REL_QUERY_TEMPLATE.format(meta_rel=meta_rel)
    driver = neo4j_connect()
    session = driver.session()
    data = session.run(query).data()
    df = pd.json_normalize(data)
    return df


@pytest.fixture(scope="class")
def source_target_dict(meta_rel):
    query = SOURCE_TARGET_QUERY_TEMPLATE.format(meta_rel=meta_rel)
    driver = neo4j_connect()
    session = driver.session()
    data = session.run(query).data()
    source = [_["source"] for _ in data]
    target = [_["target"] for _ in data]
    res = {
        "source": [_ for sub_list in source for _ in sub_list],
        "target": [_ for sub_list in target for _ in sub_list],
    }
    return res


@pytest.fixture(scope="class")
def sample_keys(meta_rel_df):
    return set(meta_rel_df.columns)


@pytest.fixture(scope="class")
def schema_defn(meta_rel):
    schema_defn = meta_rel_dict[meta_rel]
    return schema_defn


@pytest.fixture(scope="class")
def scalar_props(schema_defn, sample_keys):
    defined_scalar_props, defined_array_props = group_props_by_type(
        schema_defn, column_prefix="rel."
    )
    scalar_props = {
        k: v for k, v in defined_scalar_props.items() if {k}.issubset(sample_keys)
    }
    return scalar_props


@pytest.fixture(scope="class")
def array_props(schema_defn, sample_keys):
    defined_scalar_props, defined_array_props = group_props_by_type(
        schema_defn, column_prefix="rel."
    )
    array_props = {
        k: v for k, v in defined_array_props.items() if {k}.issubset(sample_keys)
    }
    return array_props


class TestMetaRelItem:
    def test_source_target_unique(self, source_target_dict):
        logger.info(f"source_target_dict: {source_target_dict}")
        assert len(source_target_dict["source"]) == 1
        assert len(source_target_dict["target"]) == 1

    def test_source_target_exist(self, source_target_dict):
        logger.info(f"source_target_dict: {source_target_dict}")
        assert set(source_target_dict["source"]).issubset(set(meta_node_names))
        assert set(source_target_dict["target"]).issubset(set(meta_node_names))

    def test_meta_props_exist(self, sample_keys):
        logger.info(sample_keys)
        meta_props = set([f"rel.{_}" for _ in META_REL_META_PROPS])
        assert meta_props.issubset(sample_keys)

    def test_required_props_exist(self, schema_defn, sample_keys):
        required_props = set(
            [
                f"rel.{_}"
                for _ in schema_defn["required"]
                if _ not in ["source", "target"]
            ]
        )
        logger.info(f"required_props: {required_props}")
        logger.info(f"sample_keys: {sample_keys}")
        assert required_props.issubset(sample_keys)

    def test_scalar_props_conform(self, scalar_props, meta_rel_df):
        for k, v in scalar_props.items():
            expected_type = schema_type_mapping[v["type"]]
            logger.info(f"{k}: {expected_type}")
            series = meta_rel_df[k].dropna()
            logger.info(series)
            # special handling of nullable integer
            if v["type"] == "integer":
                series = series.astype(pd.Int64Dtype())
            type_not_conform = series.apply(
                lambda _: not isinstance(_, expected_type)
            ).pipe(lambda s: sum(s))
            assert not bool(type_not_conform)

    def test_array_props_conform(self, array_props, meta_rel_df):
        for k, v in array_props.items():
            expected_type = schema_type_mapping[v["items"]["type"]]
            logger.info(f"{k}: {expected_type}")
            parent_is_not_list = (
                meta_rel_df[k]
                .dropna()
                .apply(lambda _: not isinstance(_, list))
                .pipe(lambda s: sum(s))
            )
            assert not bool(parent_is_not_list)
            series = pd.series(
                [_ for sub_list in meta_rel_df[k].dropna().tolist() for _ in sub_list]
            )
            logger.info(series)
            # special handling of nullable integer
            if v["type"] == "integer":
                series = series.astype(pd.int64dtype())
            type_not_conform = series.apply(
                lambda _: not isinstance(_, expected_type)
            ).pipe(lambda s: sum(s))
            assert not bool(type_not_conform)
