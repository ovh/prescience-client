import unittest

from prescience_client.utils.monad import Option, List


class TestMonadUtils(unittest.TestCase):

    def test_list_is_empty_true(self):
        self.assertEqual(True, List([]).is_empty())

    def test_list_is_empty_false(self):
        self.assertEqual(False, List(['toto']).is_empty())

    def test_list_map_int(self):
        self.assertEqual(List([1, 2, 3]), List([0, 1, 2]).map(lambda x: x+1))

    def test_list_map_string(self):
        self.assertEqual(List(['toto dupond', 'john dupond']), List(['toto', 'john']).map(lambda x: x+' dupond'))

    def test_list_size(self):
        self.assertEqual(3, List([1, 2, 3]).size())

    def test_list_head(self):
        self.assertEqual(1, List([1, 2, 3]).head())

    def test_list_head_option(self):
        self.assertEqual(Option(1), List([1, 2, 3]).head_option())

    def test_list_tail(self):
        self.assertEqual(3, List([1, 2, 3]).tail())

    def test_list_tail_option(self):
        self.assertEqual(Option(3), List([1, 2, 3]).tail_option())

    def test_list_to_dict_empty(self):
        self.assertEqual({}, List([]).to_dict())

    def test_list_to_dict_tuple(self):
        self.assertEqual({'key': 'value'}, List([('key', 'value')]).to_dict())

    def test_list_to_dict_index(self):
        self.assertEqual({0: 'toto'}, List(['toto']).to_dict())

    def test_list_filter(self):
        self.assertEqual(List([2, 2]), List([0, 0, 0, 2, 2]).filter(lambda x: x > 1))

    def test_list_count(self):
        self.assertEqual(2, List([0, 0, 0, 2, 2]).count(lambda x: x > 1))

    def test_get_or_else_on_valued_option(self):
        self.assertEqual('toto', Option('toto').get_or_else('other'))

    def test_get_or_else_on_none_option(self):
        self.assertEqual('other', Option(None).get_or_else('other'))

    def test_is_empty_on_none_option(self):
        self.assertEqual(True, Option(None).is_empty())

    def test_is_empty_on_valued_option(self):
        self.assertEqual(False, Option('toto').is_empty())

    def test_map_on_valued_option(self):
        self.assertEqual(Option('toto dupond'), Option('toto').map(lambda x: x + ' dupond'))

    def test_map_on_none_option(self):
        self.assertEqual(Option(None), Option(None).map(lambda x: x + ' dupond'))