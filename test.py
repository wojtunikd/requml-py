import unittest

from Analysis.preprocessing import removePunctuation
from Analysis.use_cases import removeDuplicates, getAllActors


class PreprocessingTests(unittest.TestCase):
    def test_removePunctuation(self):
        data = "This, is a 'punctuation' removal test."
        self.assertEqual(removePunctuation(data), "This is a punctuation removal test")


class UseCasesTests(unittest.TestCase):
    def test_removeDuplicateActors(self):
        data = ["actor_1", "actor_3", "actor_5", "actor_1", "actor_2", "actor_1"]
        self.assertEqual(removeDuplicates(data), ["actor_1", "actor_3", "actor_5", "actor_2"])

    def test_getAllActorsFromUserStories(self):
        data = [{"actor": "actor_1", "attr": "test_1"}, {"actor": "actor_1", "attr": "test_2"}, {"actor": "actor_2", "attr": "test_3"}]
        self.assertEqual(getAllActors(data), ["actor_1", "actor_2"])


if __name__ == "__main__":
    unittest.main()
