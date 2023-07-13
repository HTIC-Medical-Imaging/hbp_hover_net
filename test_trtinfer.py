import tensorrt as trt
import numpy as np
import monai_infer.trt_common as common

# https://github.com/NVIDIA/TensorRT/blob/main/samples/python/yolov3_onnx/onnx_to_tensorrt.py

TRT_LOGGER = trt.Logger()

def get_engine(engine_file_path):
    with open(engine_file_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
        return runtime.deserialize_cuda_engine(f.read())


if __name__=="__main__": 
    
    engine_path = '/code/hbp_hover_net/weights/monai_zoo/pathology_nuclei_segmentation_classification/models/engine.trt'

    batch_size = 32
    
    # FIXME: get a batch of tiles using Accessor
    images = np.random.randn((batch_size,3,256,256),dtype=np.float32) 

    output_names = ['nucleus_prediction', 'horizontal_vertical', 'type_prediction']
    output_shapes = [(2,164,164),(2,164,164),(5,164,164)]
    outputspec = {nm:output_shapes[ii] for ii,nm in enumerate(output_names)}

    with get_engine(engine_path) as engine, engine.create_execution_context() as context:
        inputs, outputs, bindings, stream, allocbatchsiz = common.allocate_buffers(engine,batch_size,0,outputspec)
        # Do inference
        # print("Running inference on image {}...".format(input_image_path))
        # Set host input to the image. The common.do_inference function will copy the input to the GPU before executing.
        inputs[0].host = images
        trt_outputs = common.do_inference_v2(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)

    
    # Before doing post-processing, we need to reshape the outputs as the common.do_inference will give us flat arrays.
    trt_outputs = [output.reshape([allocbatchsiz]+list(shape)) for output, shape in zip(trt_outputs, output_shapes)]

    print([x.shape for x in trt_outputs])
    # FIXME: post the outputs back in wsi size canvas

    common.free_buffers(inputs, outputs, stream)
    