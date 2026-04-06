"""
Neo4j Schema — Cypher queries for index creation and schema management.

Called by Neo4jStorage.create_graph() to set up vector + fulltext indexes.
Vector dimensions are read from Config.EMBEDDING_DIMENSIONS (default 1536).
"""

from ..config import Config

# Constraints
CREATE_GRAPH_UUID_CONSTRAINT = """
CREATE CONSTRAINT graph_uuid IF NOT EXISTS
FOR (g:Graph) REQUIRE g.graph_id IS UNIQUE
"""

CREATE_ENTITY_UUID_CONSTRAINT = """
CREATE CONSTRAINT entity_uuid IF NOT EXISTS
FOR (n:Entity) REQUIRE n.uuid IS UNIQUE
"""

CREATE_EPISODE_UUID_CONSTRAINT = """
CREATE CONSTRAINT episode_uuid IF NOT EXISTS
FOR (ep:Episode) REQUIRE ep.uuid IS UNIQUE
"""

# Fulltext indexes (for BM25 keyword search)
CREATE_ENTITY_FULLTEXT_INDEX = """
CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
FOR (n:Entity) ON EACH [n.name, n.summary]
"""

CREATE_FACT_FULLTEXT_INDEX = """
CREATE FULLTEXT INDEX fact_fulltext IF NOT EXISTS
FOR ()-[r:RELATION]-() ON EACH [r.fact, r.name]
"""


def get_entity_vector_index_query(dimensions: int) -> str:
    """Vector index for Entity nodes. Dimensions must match embedding model."""
    return f"""
CREATE VECTOR INDEX entity_embedding IF NOT EXISTS
FOR (n:Entity) ON (n.embedding)
OPTIONS {{indexConfig: {{
    `vector.dimensions`: {dimensions},
    `vector.similarity_function`: 'cosine'
}}}}
"""


def get_relation_vector_index_query(dimensions: int) -> str:
    """Vector index for RELATION edges. Dimensions must match embedding model."""
    return f"""
CREATE VECTOR INDEX fact_embedding IF NOT EXISTS
FOR ()-[r:RELATION]-() ON (r.fact_embedding)
OPTIONS {{indexConfig: {{
    `vector.dimensions`: {dimensions},
    `vector.similarity_function`: 'cosine'
}}}}
"""


def get_all_schema_queries(dimensions: int = None) -> list:
    """
    Returns all schema queries to run on startup.

    Args:
        dimensions: Vector index size. Defaults to Config.EMBEDDING_DIMENSIONS.
    """
    if dimensions is None:
        dimensions = Config.EMBEDDING_DIMENSIONS

    return [
        CREATE_GRAPH_UUID_CONSTRAINT,
        CREATE_ENTITY_UUID_CONSTRAINT,
        CREATE_EPISODE_UUID_CONSTRAINT,
        get_entity_vector_index_query(dimensions),
        get_relation_vector_index_query(dimensions),
        CREATE_ENTITY_FULLTEXT_INDEX,
        CREATE_FACT_FULLTEXT_INDEX,
    ]


# Backward-compatible alias — used by existing callers of ALL_SCHEMA_QUERIES
# Note: evaluates at import time using current Config value
ALL_SCHEMA_QUERIES = get_all_schema_queries()
