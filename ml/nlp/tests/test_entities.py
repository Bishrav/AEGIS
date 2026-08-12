import unittest

from aegis_nlp.entities import HybridEntityExtractor


class EntityTests(unittest.TestCase):
    def test_gazetteer_and_date_rules_extract_domain_entities(self):
        entities = HybridEntityExtractor().extract("Flood near Melamchi in Sindhupalchok on 2026-08-11")
        pairs = {(entity.type, entity.value) for entity in entities}
        self.assertIn(("RIVER", "Melamchi"), pairs)
        self.assertIn(("DISTRICT", "Sindhupalchok"), pairs)
        self.assertIn(("DATE", "2026-08-11"), pairs)

