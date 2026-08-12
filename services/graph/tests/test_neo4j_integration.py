import os
import unittest

from aegis_graph_service.neo4j_store import Neo4jGraphStore


@unittest.skipUnless(os.getenv("AEGIS_NEO4J_INTEGRATION") == "1", "set AEGIS_NEO4J_INTEGRATION=1 to run against Neo4j")
class Neo4jIntegrationTest(unittest.TestCase):
    def test_projection_and_impact_query(self):
        from types import SimpleNamespace

        store = Neo4jGraphStore(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "aegis_dev_password"),
        )
        incident = SimpleNamespace(incident_id="integration-incident", event_ids=["integration-event"], district="Sindhupalchok")
        event = {"event_id": "integration-event", "event_type": "FLOOD", "occurred_at": "2026-08-12T10:00:00Z", "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}]}
        try:
            store.project_incident(incident, [event])
            nodes = store.impact("integration-incident", depth=3)
            self.assertTrue(any(node["id"] == "integration-event" for node in nodes))
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
