from __future__ import annotations

from typing import Any


class Neo4jGraphStore:
    def __init__(self, uri: str, user: str, password: str) -> None:
        from neo4j import GraphDatabase

        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def project_incident(self, incident: Any, events: list[dict[str, Any]]) -> None:
        with self.driver.session() as session:
            session.execute_write(_write_projection, incident, events)

    def impact(self, incident_id: str, depth: int = 3) -> list[dict[str, Any]]:
        # Cypher requires literal variable-length bounds in this deployment path.
        # Clamp the caller-provided value before inserting the integer into the query.
        safe_depth = min(max(int(depth), 1), 5)
        with self.driver.session() as session:
            result = session.run(
                f"MATCH (i:Incident {{id: $incident_id}})-[*1..{safe_depth}]->(n) "
                "RETURN DISTINCT n.id AS id, labels(n) AS labels",
                incident_id=incident_id,
            )
            return [record.data() for record in result]


def _write_projection(tx, incident, events) -> None:
    tx.run("MERGE (i:Incident {id: $id}) SET i.district = $district", id=incident.incident_id, district=incident.district)
    for event in events:
        if str(event["event_id"]) not in incident.event_ids:
            continue
        tx.run(
            "MERGE (e:Event {id: $id}) SET e.type = $type, e.occurred_at = $occurred_at "
            "WITH e MATCH (i:Incident {id: $incident_id}) MERGE (i)-[:CONTAINS]->(e)",
            id=str(event["event_id"]),
            type=event["event_type"],
            occurred_at=str(event["occurred_at"]),
            incident_id=incident.incident_id,
        )
        for entity in event.get("entities", []):
            tx.run(
                "MERGE (n:Entity {type: $type, value: $value}) "
                "WITH n MATCH (e:Event {id: $event_id}) MERGE (e)-[:MENTIONS]->(n)",
                type=entity["type"],
                value=entity["value"],
                event_id=str(event["event_id"]),
            )
