import torch
import sys
import torch.onnx
import os
import pathlib
from  importlib import import_module

# https://docs.nvidia.com/deeplearning/tensorrt/quick-start-guide/index.html#export-from-pytorch

if __name__=="__main__":
    mdlpath = sys.argv[1]
    batch_size = int(sys.argv[2])

    shp = [3,256,256]
    dummy_batch = torch.randn(batch_size,*shp)
    dummy_batch_u8 = torch.zeros([batch_size]+shp, dtype=torch.uint8)

    outdir=os.path.dirname(mdlpath)
    basename = os.path.basename(mdlpath)
    prefix=pathlib.Path(basename).stem

    modulename = 'monai.networks.nets'
    clsname = 'HoVerNet'

    mdlargs = {
        'mode':'fast',
        'in_channels':3,
        'out_classes':5,
    }
    
    mod = import_module(modulename)
    cls = getattr(mod,clsname)
    obj = cls(**mdlargs)
    
    torch.onnx.export(obj,dummy_batch,outdir+'/'+prefix+'_fp32.onnx',verbose=False)
    torch.onnx.export(obj,dummy_batch_u8,outdir+'/'+prefix+'_u8.onnx',verbose=False)

