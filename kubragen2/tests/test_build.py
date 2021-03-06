import unittest

from kubragen2.build import BuildData
from kubragen2.data import DataIsNone, DisabledData, ValueData, DataGetValue
from kubragen2.exception import InvalidParamError


class TestData(unittest.TestCase):
    def test_data_is_None(self):
        self.assertTrue(DataIsNone(None))
        self.assertFalse(DataIsNone('xxx'))
        self.assertTrue(DataIsNone(DisabledData()))
        self.assertFalse(DataIsNone(ValueData('xxx', enabled=True)))
        self.assertTrue(DataIsNone(ValueData(None, enabled=True)))
        self.assertTrue(DataIsNone(ValueData(DisabledData(), enabled=True)))
        self.assertFalse(DataIsNone(ValueData(ValueData('xxx', enabled=True), enabled=True)))

    def test_data_get_value(self):
        self.assertEqual(DataGetValue(None), None)
        self.assertEqual(DataGetValue('xxx'), 'xxx')
        self.assertEqual(DataGetValue(DisabledData()), None)
        with self.assertRaises(InvalidParamError):
            DataGetValue(DisabledData(), raise_if_disabled=True)
        self.assertEqual(DataGetValue(ValueData('xxx', enabled=True)), 'xxx')
        self.assertEqual(DataGetValue(ValueData(None, enabled=True)), None)
        self.assertEqual(DataGetValue(ValueData(DisabledData(), enabled=True)), None)
        self.assertEqual(DataGetValue(ValueData(ValueData('xxx', enabled=True), enabled=True)), 'xxx')

    def test_build_data(self):
        data = {
            'x': 1,
            'y': ValueData(2, enabled=True),
            'z': {
                'a': ValueData(3, enabled=True),
                'b': ValueData(4, enabled=False),
                'h': [
                    13, 14, ValueData(15, enabled=True), ValueData(16, enabled=False),
                ]
            },
        }
        BuildData(data)
        self.assertEqual(data, {
            'x': 1,
            'y': 2,
            'z': {
                'a': 3,
                'h': [
                    13, 14, 15,
                ]
            },
        })

    def test_build_data_inplace(self):
        data = {
            'x': 1,
            'y': ValueData(2, enabled=True),
        }

        ndata = BuildData(data, in_place=False)
        self.assertEqual(ndata, {'x': 1, 'y': 2})
        self.assertIsInstance(data['y'], ValueData)

        BuildData(data, in_place=True)
        self.assertNotIsInstance(data['y'], ValueData)
