import copy
import unittest

from kubragen2.options import Options, OptionValue, OptionsBuildData


class TestUtil(unittest.TestCase):
    def test_option_merge(self):
        options = Options({
            'x': {
                'y': OptionValue('x.z'),
                'z': 14,
            }
        }, {
            'x': {
                'y': 99,
            },
        })
        self.assertEqual(options.option_get('x.y'), 99)

    def test_option_value(self):
        options = Options({
            'x': {
                'y': OptionValue('x.z'),
                'z': 14,
            }
        })
        data = OptionsBuildData(options, copy.deepcopy(options.options))
        self.assertEqual(data, {'x': {'y': 14, 'z': 14}})
