import torch
import sys
import torch.onnx
import os
import pathlib
from  importlib import import_module
import onnx

# https://docs.nvidia.com/deeplearning/tensorrt/quick-start-guide/index.html#export-from-pytorch
# https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

if __name__=="__main__":
    mdlpath = sys.argv[1]
    batch_size = int(sys.argv[2])

    device = torch.device('cuda')
    shp = [3,256,256]
    dummy_batch = torch.randn(batch_size,*shp).to(device)
    dummy_batch_u8 = torch.zeros([batch_size]+shp, dtype=torch.uint8).to(device)

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

    
    obj = cls(**mdlargs).to(device)
    obj.eval()
    
    mdlweights = torch.load(mdlpath,map_location=device)
    obj.load_state_dict(mdlweights)

    out = obj(dummy_batch)

    dynaxes = {'input':{0:'batch_size'}}
    outkeys = []
    for k,v in out.items():
        print(k,v.shape,v.dtype)
        dynaxes[k]={0:'batch_size'}
        outkeys.append(k)

    torch.onnx.export(obj, dummy_batch, outdir+'/'+prefix+'_fp32.onnx',
                      verbose=False,
                      export_params=True,
                      input_names=['input'],
                      output_names=outkeys,
                      dynamic_axes = dynaxes,
                      )
    
    onnx.checker.check_model(onnx.load(outdir+'/'+prefix+'_fp32.onnx'))

    # torch.onnx.export(obj,dummy_batch_u8,outdir+'/'+prefix+'_u8.onnx',verbose=False)

