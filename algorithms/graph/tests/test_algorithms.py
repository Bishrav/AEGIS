import unittest

from aegis_graph.algorithms import Graph, bfs_impact, shortest_path


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.graph.add_edge("Flood", "Road", 1)
        self.graph.add_edge("Road", "Hospital", 2)
        self.graph.add_edge("Flood", "Substation", 3)

    def test_bfs_returns_impact_blast_radius(self):
        self.assertEqual(bfs_impact(self.graph, "Flood"), ["Flood", "Road", "Substation", "Hospital"])

    def test_shortest_path_returns_weight_and_path(self):
        self.assertEqual(shortest_path(self.graph, "Flood", "Hospital"), (3, ["Flood", "Road", "Hospital"]))

