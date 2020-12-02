import unittest

from kubragen2.data import Data
from kubragen2.kdata import KData_ConfigMap, KData_Manual, KData_Secret
from kubragen2.kdatahelper import KDataHelper_Env, KDataHelper_Volume


class TestKData(unittest.TestCase):
    def test_helper_env_value(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value='mypassword')
        self.assertEqual(kdata, {
            'name': 'APP_PASSWORD',
            'value': 'mypassword',
        })

    def test_helper_env_none(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value=None, disable_if_none=True)
        self.assertIsInstance(kdata, Data)
        self.assertFalse(kdata.is_enabled())

    def test_helper_env_configmap(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value=KData_ConfigMap(configmapName='mycm', configmapData='cmdata'))
        self.assertEqual(kdata, {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'configMapKeyRef': {
                    'name': 'mycm',
                    'key': 'cmdata'
                }
            },
        })

    def test_helper_volume_value(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value={
            'emptyDir': {},
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'emptyDir': {},
        })

    def test_helper_volume_none(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=None, disable_if_none=True)
        self.assertIsInstance(kdata, Data)
        self.assertFalse(kdata.is_enabled())

    def test_helper_volume_configmap(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=KData_ConfigMap(configmapName='mycm', configmapData='cmdata'))
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'configMap': {
                'name': 'mycm',
                'items': [{
                    'key': 'cmdata',
                    'path': 'cmdata',
                }],
            }
        })

    def test_helper_volume_configmap_manual(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=KData_Manual(merge_config={
            'configMap': {
                'name': 'mycm',
                'items': [{
                    'key': 'xcmdata',
                    'path': 'xcmdata',
                }],
            },
        }))

        self.assertEqual(kdata, {
            'name': 'data-volume',
            'configMap': {
                'name': 'mycm',
                'items': [{
                    'key': 'xcmdata',
                    'path': 'xcmdata',
                }],
            }
        })

    def test_helper_volume_secret(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=KData_Secret(secretName='mycm', secretData='cmdata'))
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'secret': {
                'secretName': 'mycm',
                'items': [{
                    'key': 'cmdata',
                    'path': 'cmdata',
                }],
            }
        })
