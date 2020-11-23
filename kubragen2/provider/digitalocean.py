from typing import Any, Optional

from ..kdata import KData_PersistentVolume_CSI
from ..merger import merger


class KData_PersistentVolume_CSI_DOBS(KData_PersistentVolume_CSI):
    noformat: Optional[bool]
    nodriver: bool

    def __init__(self, name: str, csi: Any, storageclass: Optional[str] = None, noformat: Optional[bool] = True,
                 nodriver: bool = False,
                 merge_config: Optional[Any] = None):
        super().__init__(name=name, csi=csi, storageclass=storageclass, merge_config=merge_config)
        self.noformat = noformat
        self.nodriver = nodriver

    def build(self) -> Any:
        ret = super().build()
        if not self.nodriver:
            ret['spec']['csi']['driver'] = 'dobs.csi.digitalocean.com'
        if self.noformat is not None:
            ret = merger.merge(ret, {
                'spec': {
                    'csi': {
                        'volumeAttributes': {
                            'com.digitalocean.csi/noformat': 'false' if self.noformat is False else 'true',
                        }
                    }
                }
            })
        if 'volumeHandle' in ret['spec']['csi'] and ret['spec']['csi']['volumeHandle'] is not None:
            # https://github.com/digitalocean/csi-digitalocean/blob/master/examples/kubernetes/pod-single-existing-volume/README.md
            merger.merge(ret, {
                'metadata': {
                    'annotations': {
                        'pv.kubernetes.io/provisioned-by': 'dobs.csi.digitalocean.com',
                    }
                }
            })
        if 'storageClassName' not in ret['spec']:
            ret['spec']['storageClassName'] = 'do-block-storage'
        return ret

