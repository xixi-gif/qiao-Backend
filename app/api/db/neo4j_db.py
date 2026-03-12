# app/db/neo4j_db.py
from neo4j import GraphDatabase
from app.api.core.config import settings

class Neo4jConnection:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self._driver.close()

    def execute_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# 创建一个单例供全局使用
neo4j_conn = Neo4jConnection()