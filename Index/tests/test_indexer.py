import unittest
from src.utils import tokenize, extract_product_info
from src.indexer import index_reviews, index_features

class TestIndexer(unittest.TestCase):

    def test_tokenize(self):
        text = "The Box of Chocolate!"
        expected = ["box", "chocolate"]
        self.assertEqual(tokenize(text), expected)

    def test_url_extraction(self):
        url = "https://web-scraping.dev/product/10?variant=red-5"
        info = extract_product_info(url)
        self.assertEqual(info['id'], "10")
        self.assertEqual(info['variant'], "red-5")

    def test_reviews_logic(self):
        docs = [{
            "url": "https://tests.com",
            "product_reviews": [
                {"rating": 5, "date": "2023-01-01"},
                {"rating": 3, "date": "2023-02-01"}
            ]
        }]
        idx = index_reviews(docs)
        stats = idx["https://tests.com"]
        self.assertEqual(stats['total_reviews'], 2)
        self.assertEqual(stats['mean_mark'], 4.0)
        self.assertEqual(stats['last_rating'], 3)

    def test_feature_index(self):
        docs = [
            {"url": "u1", "product_features": {"brand": "Nike"}},
            {"url": "u2", "product_features": {"brand": "Nike"}}
        ]
        idx = index_features(docs, "brand")
        self.assertIn("u1", idx["nike"])
        self.assertIn("u2", idx["nike"])

if __name__ == '__main__':
    unittest.main()