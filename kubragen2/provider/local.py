from typing import Optional, Any, Dict

from ..kdata import KData_PersistentVolumeClaim


class KData_PersistentVolumeClaim_NoSelector(KData_PersistentVolumeClaim):
    volumename: str

    def __init__(self, name: str, volumeName: str, storageclass: Optional[str] = None,
                 namespace: Optional[str] = None, merge_config: Optional[Any] = None):
        super().__init__(name=name, storageclass=storageclass, namespace=namespace, merge_config=merge_config)
        self.volumename = volumeName

    def get_value(self) -> Any:
        ret: Dict[Any, Any] = super().get_value()
        if 'selector' in ret['spec']:
            del ret['spec']['selector']
            ret['spec']['storageClassName'] = ''
            ret['spec']['volumeName'] = self.volumename
        return ret
