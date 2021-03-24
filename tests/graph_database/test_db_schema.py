import pytest

from loguru import logger

from workflow.scripts.utils.general import neo4j_connect

from tests.utils.load_schema import meta_node_names, meta_rel_names, meta_node_dict


def test_connect():
    query = """
        MATCH (n)
        RETURN n LIMIT 2;
    """
    driver = neo4j_connect()
    session = driver.session()
    data = session.run(query).data()
    logger.info(data)
    assert len(data) == 2


def test_meta_node_exist():
    query = """
        CALL db.labels() YIELD label RETURN label
    """
    driver = neo4j_connect()
    with driver.session() as session:
        data = session.run(query).data()
    db_meta_node_names = set([_["label"] for _ in data])
    if {"Meta"}.issubset(db_meta_node_names):
        db_meta_node_names.remove({"Meta"})
    logger.info(f"meta_node_names: {meta_node_names}")
    logger.info(f"db_meta_node_names: {db_meta_node_names}")
    assert set(meta_node_names) == db_meta_node_names


def test_meta_rel_exist():
    query = """
        CALL db.relationshipTypes()
        YIELD relationshipType
        RETURN relationshipType AS label
    """
    driver = neo4j_connect()
    with driver.session() as session:
        data = session.run(query).data()
    db_meta_rel_names = set([_["label"] for _ in data])
    logger.info(f"meta_rel_names: {meta_rel_names}")
    logger.info(f"db_meta_rel_names: {db_meta_rel_names}")
    assert set(meta_rel_names) == db_meta_rel_names


def test_meta_node_index():
    query = "CALL db.indexes()"
    driver = neo4j_connect()
    with driver.session() as session:
        data = session.run(query).data()
    actual_node_indexes = {(_["labelsOrTypes"][0], _["properties"][0]) for _ in data}
    expected_node_indexes = {
        (key, value["index"]) for key, value in meta_node_dict.items()
    }
    # We would expect expected_indexes to be a subset of current_indexes
    assert len(expected_node_indexes.difference(actual_node_indexes)) == 0
