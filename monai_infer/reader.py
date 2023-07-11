from monai.data import ImageReader
import os
from monai.utils import ensure_tuple, MetaKeys
import pickle
import numpy as np

from monai.data.image_reader import (
    _stack_images, _copy_compatible_dict
)

# written like https://docs.monai.io/en/latest/_modules/monai/data/image_reader.html#PILReader

class MmapReader(ImageReader):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        # for k,v in kwargs.items():
        #     self.__setattr__(k,v)
    
    def verify_suffix(self,filename):
        return filename[-4:]=='.dat' and os.path.exists(filename.replace('.dat','_info.pkl'))

    def read(self,data,**kwargs):
        # data: file name or list of filenames
        img_ = []
        filenames = ensure_tuple(data)
        kwargs_ = self.kwargs.copy()
        kwargs_.update(kwargs)

        for name in filenames:
            info = pickle.load(open(name.replace('.dat','_info.pkl'),'rb'))
            arr = np.memmap(name,shape=info['shape'],dtype='uint8',mode='r')
            img_.append(arr)
        
        return img_ if len(filenames)>1 else img_[0]
    
        
    def get_data(self,imgarrays):
        img_array = []
        compatible_meta = {}

        if isinstance(imgarrays,np.ndarray):
            imgarrays = (imgarrays,)

        for iarr in ensure_tuple(imgarrays):
            header = {}
            header[MetaKeys.SPATIAL_SHAPE]=np.asarray(iarr.shape)
            img_array.append(iarr)
            _copy_compatible_dict(header,compatible_meta)
        
        return _stack_images(img_array,compatible_meta),compatible_meta



