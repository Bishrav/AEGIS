import unittest

from aegis_rag.retrieval import HttpEmbeddingProvider


class EmbeddingProviderTest(unittest.TestCase):
    def test_provider_configuration_is_dimension_aware(self):
        provider = HttpEmbeddingProvider("https://embed.example.test/v1", "secret", "embedding-model", dimensions=3)
        self.assertEqual(provider.dimensions, 3)
        self.assertEqual(provider.endpoint, "https://embed.example.test/v1")


if __name__ == "__main__":
    unittest.main()
