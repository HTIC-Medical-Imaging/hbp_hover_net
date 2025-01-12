import tensorrt as trt
import numpy as np
import monai_infer.trt_common as common
import datetime
import sys
import os
from tqdm import tqdm
from cuda import cuda, cudart
from misc.jp2_converter import Accessor
from functools import partial

from concurrent.futures import ThreadPoolExecutor,wait
# https://github.com/NVIDIA/TensorRT/blob/main/samples/python/yolov3_onnx/onnx_to_tensorrt.py

TRT_LOGGER = trt.Logger(trt.Logger.VERBOSE)

def get_engine(engine_file_path):
    with open(engine_file_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
        return runtime.deserialize_cuda_engine(f.read())

engine_path = '/code/hbp_hover_net/weights/monai_zoo/pathology_nuclei_segmentation_classification/models/engine_best.trt'
output_names = ['nucleus_prediction', 'horizontal_vertical', 'type_prediction']
output_shapes = [(2,164,164),(2,164,164),(5,164,164)]
outputspec = {nm:output_shapes[ii] for ii,nm in enumerate(output_names)}

def parallel_infer(nucleus_map,batch,device):

    cudart.cudaSetDevice(device)

    with get_engine(engine_path) as engine, engine.create_execution_context() as context:
        print('num_bindings:',engine.num_bindings)
        print('num_optimization_profiles:',engine.num_optimization_profiles)
        common.engine_info(engine)
        inputs, outputs, bindings, stream, allocbatchsiz = common.allocate_buffers(engine,batch_size,0,outputspec)
        
        # https://github.com/NVIDIA/TensorRT/blob/a167852705d74bcc619d8fad0af4b9e4d84472fc/demo/BERT/inference.py#L154
        context.set_input_shape('input',(allocbatchsiz,3,256,256))
        # for jj,nm in enumerate(output_names):
        #     context.set_binding_shape(engine.get_binding_index(nm),[allocbatchsiz]+list(output_shapes[jj]))

        # assert context.all_binding_shapes_specified

        images = np.zeros((batch_size,3,256,256),dtype=np.float32)
        
        for batchslice in tqdm(batch):
            nimgs = batchslice[1]-batchslice[0]
            images[:]=0
            rgns = []
            for ii,tilenum in enumerate(range(*batchslice)):
                img,_,_ = accessor[tilenum]
                images[ii,...]=np.transpose(img,[2,0,1]).astype(np.float32)/255
                rgns.append(accessor.get_tile_extent(tilenum))
    
            # Do inference
            # print("Running inference on image {}...".format(input_image_path))
            # Set host input to the image. The common.do_inference function will copy the input to the GPU before executing.
            inputs[0].host = images[:nimgs,...]
            tic = datetime.datetime.now()
            trt_outputs = common.do_inference_v2(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
            toc = datetime.datetime.now()
            # batchtimes.append(toc-tic)
    
            # Before doing post-processing, we need to reshape the outputs as the common.do_inference will give us flat arrays.
            trt_outputs = [output.reshape([allocbatchsiz]+list(shape)) for output, shape in zip(trt_outputs, output_shapes)]

            # print([x.shape for x in trt_outputs])

            # post the outputs back in wsi size canvas
            for ii,rgn in enumerate(rgns):
                c1,r1=rgn.point1.x,rgn.point1.y
                c2,r2=rgn.point2.x,rgn.point2.y
                nucleus_map[:,r1:r2,c1:c2]=trt_outputs[0][ii][:,:r2-r1,:c2-c1]
    
    common.free_buffers(inputs, outputs, stream)
    del context
    return os.getpid()



    
if __name__=="__main__": 
    
    imgdatfile = sys.argv[1]
    batch_size = int(sys.argv[2])

    # get batches of tiles using Accessor
    tileshp = (164,164)
    padding = (256-164)//2
    accessor = Accessor(imgdatfile,tileshp,padding)
    print('ntiles:',accessor.ntiles)
    batches = []
    
    
    num_gpus = [7,7]
    chunks=[]
    
    for batchstart in range(0,accessor.ntiles,batch_size):
        batchend = min(batchstart+batch_size,accessor.ntiles)
        batches.append((batchstart,batchend))
    
    chunk_size = len(batches)//len(num_gpus)
    for i in range(1,len(num_gpus)+1):
        chunks.append(batches[(i-1)*chunk_size:i*chunk_size])
    # images = np.random.randn(batch_size,3,256,256).astype(np.float32) 
    

    bn = os.path.basename(imgdatfile)
    mmapname = '/data/eval2/nucleus_parallel'+bn
    if os.path.exists(mmapname):
        os.unlink(mmapname)
    nucleus_map = np.memmap(mmapname, dtype=np.float32, shape=(2,accessor.imageshape[0],accessor.imageshape[1]),mode='w+' )
    # nucleus_map[:]=0

    job = partial(parallel_infer,nucleus_map)
    with ThreadPoolExecutor(max_workers=len(num_gpus)) as executor:
        futures = executor.map(job,chunks,num_gpus)
        # wait(futures)
