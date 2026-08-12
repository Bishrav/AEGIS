import unittest

from aegis_reasoning.providers import OpenAICompatibleProvider


class ProviderBoundaryTest(unittest.TestCase):
    def test_provider_is_configurable_without_calling_network(self):
        provider = OpenAICompatibleProvider("https://llm.example.test/v1", "secret", "demo-model")
        self.assertEqual(provider.endpoint, "https://llm.example.test/v1")
        self.assertEqual(provider.model, "demo-model")


if __name__ == "__main__":
    unittest.main()
