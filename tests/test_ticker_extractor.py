import unittest

from config import COMMON_FALSE_TICKERS
from processors.ticker_extractor import extract_tickers


class TickerExtractorTests(unittest.TestCase):
    def setUp(self):
        self.symbol_universe = [
            {"ticker": "RKLB", "company": "Rocket Lab USA"},
            {"ticker": "IONQ", "company": "IonQ"},
            {"ticker": "XYZ", "company": "Example Quantum Systems"},
        ]

    def test_extracts_symbols_not_present_in_config(self):
        text = "Rocket Lab USA wins a defense launch contract while $IONQ spikes."

        self.assertNotIn("RKLB", COMMON_FALSE_TICKERS)
        self.assertNotIn("IONQ", COMMON_FALSE_TICKERS)
        self.assertEqual(
            extract_tickers(text, symbol_universe=self.symbol_universe),
            ["IONQ", "RKLB"],
        )

    def test_extracts_unknown_uppercase_symbol_when_in_universe(self):
        text = "XYZ reports unusual volume after a partnership headline."

        self.assertNotIn("XYZ", COMMON_FALSE_TICKERS)
        self.assertEqual(
            extract_tickers(text, symbol_universe=self.symbol_universe),
            ["XYZ"],
        )

    def test_avoids_generic_false_positives(self):
        text = "Stocks rise as the market awaits the Fed decision and new CPI data."

        self.assertEqual(extract_tickers(text, symbol_universe=self.symbol_universe), [])


if __name__ == "__main__":
    unittest.main()
