import argparse
import glob
import json
import math
import multiprocessing
import os
import re
import sys
from importlib import import_module
from multiprocessing import Lock, Pool
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.utils.data as data
import tqdm
import tensorrt as trt
from run_utils.utils import convert_pytorch_checkpoint

TRT_LOGGER = trt.Logger(min_severity =trt.ILogger.INTERNAL_ERROR)

from ctypes import cdll, c_char_p
libcudart = cdll.LoadLibrary('libcudart.so')
libcudart.cudaGetErrorString.restype = c_char_p

def cudaSetDevice(device_idx):
    ret = libcudart.cudaSetDevice(device_idx)
    if ret != 0:
        error_string = libcudart.cudaGetErrorString(ret)
        raise RuntimeError("cudaSetDevice: " + error_string)
####
class InferManager(object):
    def __init__(self, **kwargs):
        self.run_step = None
        for variable, value in kwargs.items():
            self.__setattr__(variable, value)
        self.__load_model()
        self.nr_types = self.method["model_args"]["nr_types"]
        # create type info name and colour

        # default
        self.type_info_dict = {
            None: ["no label", [0, 0, 0]],
        }

        if self.nr_types is not None and self.type_info_path is not None:
            self.type_info_dict = json.load(open(self.type_info_path, "r"))
            self.type_info_dict = {
                int(k): (v[0], tuple(v[1])) for k, v in self.type_info_dict.items()
            }
            # availability check
            for k in range(self.nr_types):
                if k not in self.type_info_dict:
                    assert False, "Not detect type_id=%d defined in json." % k

        if self.nr_types is not None and self.type_info_path is None:
            cmap = plt.get_cmap("hot")
            colour_list = np.arange(self.nr_types, dtype=np.int32)
            colour_list = (cmap(colour_list)[..., :3] * 255).astype(np.uint8)
            # should be compatible out of the box wrt qupath
            self.type_info_dict = {
                k: (str(k), tuple(v)) for k, v in enumerate(colour_list)
            }
        return

    def __load_model(self):
        """Create the model, load the checkpoint and define
        associated run steps to process each data batch.
        
        """
        
        module_lib = import_module("models.hovernet.run_desc")
        run_step = getattr(module_lib, "infer_step")
        run_step_trt = getattr(module_lib, "infer_trt_step")
        
        if "trt_model_path" in self.method:
            engines = []
            for gpu_id in range(len(self.method['gpu_list'])):
                torch.cuda.set_device(gpu_id)
                with open(self.method["trt_model_path"], "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
                    engines.append(runtime.deserialize_cuda_engine(f.read()))
                print(f"GPU {gpu_id} Loaded")
                
            self.run_step = lambda input_batch,device: run_step_trt(input_batch, device, engines[device])
            
        elif 'model_path' in self.method:
            model_desc = import_module("models.hovernet.net_desc")
            model_creator = getattr(model_desc, "create_model")

            net = model_creator(**self.method["model_args"])
            saved_state_dict = torch.load(self.method["model_path"])["desc"]
            saved_state_dict = convert_pytorch_checkpoint(saved_state_dict)

            net.load_state_dict(saved_state_dict, strict=True)
            net = torch.nn.DataParallel(net)
            net = net.to("cuda")
        
            self.run_step = lambda input_batch: run_step(input_batch, net)

        else:
            print('warning: self.run_step might be improper',self.run_step)
            print(self.method)

        module_lib = import_module("models.hovernet.post_proc")
        self.post_proc_func = getattr(module_lib, "process")
        return

    def __save_json(self, path, old_dict, mag=None):
        new_records = []
        new_dict2 = {}
        for inst_id, inst_info in old_dict.items():
            new_inst_info1 = {"id":int(inst_id)}            
            new_inst_info2 = {}
            for info_name, info_value in inst_info.items():
                # convert to jsonable
                if isinstance(info_value, np.ndarray):
                    info_value = np.round(info_value,2).tolist()
                if "contour" in info_name:
                    new_inst_info2[info_name] = info_value
                else:
                    if "prob" in info_name:
                        info_value = np.round(info_value,3)
                    new_inst_info1[info_name] = info_value
            
            new_records.append(new_inst_info1)
            new_dict2[int(inst_id)] = new_inst_info2
            

        # json_dict = {"mag": mag, "nuc": new_dict1}  # to sync the format protocol
        # with open(path+'_objects.json', "w") as handle:
        #     json.dump({"mag": mag, "nuc": new_dict1}, handle)
        pd.DataFrame(new_records).to_csv(path+'_objects.csv',index=False)
        with open(path+'_contours.json', "w") as handle:
            json.dump({"mag": mag, "nuc": new_dict2}, handle)    
        return new_records
