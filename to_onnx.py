import torch
import sys
import torch.onnx
import os
import pathlib
from  importlib import import_module
import onnx
import onnxruntime
import numpy as np

# https://docs.nvidia.com/deeplearning/tensorrt/quick-start-guide/index.html#export-from-pytorch
# https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

# creating trt engine file:
# trtexec --onnx=model_fp32.onnx --buildOnly --best --precisionConstraints=prefer
# --minShapes=input:1x3x256x256
# --maxShapes=input:64x3x256x256
# --optShapes=input:32x3x256x256
# --saveEngine=engine.trt 

def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

if __name__=="__main__":
    mdlpath = sys.argv[1]
    batch_size = int(sys.argv[2])

    device = torch.device('cpu') #'cuda:0')
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

    out_torch = obj(dummy_batch)

    dynaxes = {'input':{0:'batch_size'}}
    outkeys = []
    out_vals = []
    for k,v in out_torch.items():
        print(k,v.shape,v.dtype)
        dynaxes[k]={0:'batch_size'}
        outkeys.append(k)
        out_vals.append(to_numpy(v))

    outname = outdir+'/'+prefix+'_fp32.onnx'
    torch.onnx.export(obj, dummy_batch, outname, 
                      verbose=False,
                      export_params=True,
                      input_names=['input'],
                      output_names=outkeys,
                      dynamic_axes = dynaxes,
                      )
    
    onnx.checker.check_model(onnx.load(outname))
    # https://onnxruntime.ai/docs/get-started/with-python.html
    
    #providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])
    ort_session = onnxruntime.InferenceSession(outname, providers=['CPUExecutionProvider']) 
    
    for inp in ort_session.get_inputs():
        print(inp)

    ort_inputs = {ort_session.get_inputs()[0].name:to_numpy(dummy_batch)}
    ort_outs = ort_session.run(None,ort_inputs)

    for ii,out_elt in enumerate(ort_outs):
        print(out_elt.shape)
        try:
            np.testing.assert_allclose(out_elt,out_vals[ii],rtol=1e-03, atol=1e-05)
        except Exception as ex:
            print(ex)

    # torch.onnx.export(obj,dummy_batch_u8,outdir+'/'+prefix+'_u8.onnx',verbose=False)

