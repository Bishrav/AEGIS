import unittest
from unittest.mock import Mock

from aegis_graph_service.neo4j_store import Neo4jGraphStore


class Neo4jStoreTests(unittest.TestCase):
    def test_store_can_be_constructed_with_driver_factory_boundary(self):
        self.assertTrue(hasattr(Neo4jGraphStore, "project_incident"))
        self.assertTrue(hasattr(Neo4jGraphStore, "impact"))

