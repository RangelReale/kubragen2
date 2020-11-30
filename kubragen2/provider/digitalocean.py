from typing import Any, Optional, Mapping

from ..kdata import KData_PersistentVolume_CSI, KData_PersistentVolume_Request, KData_PersistentVolumeClaim, \
    KData_PersistentVolumeClaim_Request
from ..merger import merger


class KData_PersistentVolume_CSI_DOBS(KData_PersistentVolume_CSI):
    """
    A CSI DOBS PersistentVolume.
    """
    noformat: Optional[bool]
    nodriver: bool

    def __init__(self, noformat: Optional[bool] = True,
                 nodriver: bool = False):
        super().__init__(clear_storageclass_if_volumehandle=False)
        self.noformat = noformat
        self.nodriver = nodriver

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret = dict(super().internal_build(req))
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

    def build_claim(self, pvc: KData_PersistentVolumeClaim, req: KData_PersistentVolumeClaim_Request) -> Mapping[Any, Any]:
        ret = dict(super().build_claim(pvc, req))
        if 'storageClassName' not in ret['spec']:
            ret['spec']['storageClassName'] = 'do-block-storage'
        return ret
