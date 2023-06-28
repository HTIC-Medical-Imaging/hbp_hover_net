import glymur
glymur.set_option('lib.num_threads',48)
glymur.set_option('print.codestream',False)
glymur.set_option('print.xml',False)
import pickle
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from datetime import datetime
import numpy as np
from collections import namedtuple
from multiprocessing import cpu_count
import os
from tqdm import tqdm

MultiprocPlan = namedtuple('MultiprocPlan','worksize,nworkers,perworker,rounds,minwork')

def get_multiproc_plan(worksize,minwork=50):
    
    assert minwork>0 
    minwork = min(minwork, worksize)
    
    maxcnt = cpu_count()
    
    for factor in (1/2, 2/3, 3/4, 4/5, 5/6, 6/7, 7/8):

        nworkers = int(maxcnt*factor)
    
        perworker = worksize//nworkers

        rounds = perworker//minwork
        
        while rounds < 1 and nworkers > 1:
            nworkers=nworkers//2
            perworker = worksize//nworkers

            rounds = perworker//minwork
        
        if rounds < 1:
            rounds = 1
            break
            
        if rounds > 5: # need more workers
            continue
        else:
            break
    return MultiprocPlan(worksize,nworkers,perworker,rounds,minwork)

Point = namedtuple('Point','x,y')
Extent = namedtuple('Extent','point1,point2')

def to_slice(ext,step=1):
    """can directly index as arr[to_slice(ext)] - equiv to 
        arr[ext.point1.y:ext.point2.y,ext.point1.x:ext.point2.x,:]"""
    rsl = slice(int(ext.point1.y),int(ext.point2.y),step)
    csl = slice(int(ext.point1.x),int(ext.point2.x),step)
    return rsl,csl 

def workerfunc(obj,tilenum):
     arr, rgn, url = obj[tilenum] # for __getitem__
     return arr,rgn, url, tilenum, os.getpid()

class MmapCreator:
    def __init__(self,jp2path,mmapdir='/data/special/mmapcache',shp=(4096,4096),padding=0):
        # print(jp2path)
        # print(os.listdir(os.path.dirname(jp2path)))
        
        self.jp2path = jp2path

        if not os.path.exists(self.jp2path):
            raise RuntimeError('file not exists')
        
        self._jp2handle = glymur.Jp2k(self.jp2path)
        if self._jp2handle is None :
            raise RuntimeError('glymur handle is invalid')
        # else:
            # print(self._jp2handle._readonly)
            # self._jp2handle.parse()
            # self._jp2handle._initialize_shape()
        self.imageshape = self._jp2handle.shape
        print(self.imageshape)
        self.ntiles_c = round(self.imageshape[1]/shp[1]) # FIXME: was ceil, changing to round for compat with ui
        self.ntiles_r = round(self.imageshape[0]/shp[0]) # not actually used anywhere - only print
        self.ntiles = self.ntiles_r * self.ntiles_c
        print(self.ntiles)
        self.padding=padding
        self.tileshape = (shp[0],shp[1],3)
        loc,bn = os.path.split(jp2path)
        namepart = ".".join(bn.split('.')[:-1])
        self.dec_factor = 1
        self.mmapfilename = mmapdir+'/'+namepart+'.dat'

        self.infoname = self.mmapfilename.replace('.dat','_info.pkl')

    def get_tile_extent(self,tilenum):
        # assert tilenum<self.ntiles
        tile_r = tilenum//self.ntiles_c
        tile_c = tilenum % self.ntiles_c
        tl = Point(self.tileshape[1]*tile_c,self.tileshape[0]*tile_r)
        br = Point(min(tl.x+self.tileshape[1],self.imageshape[1]),min(tl.y+self.tileshape[0],self.imageshape[0]))
        
        return Extent(tl,br)

    def get_padded_extent(self,ext):
        padding = self.padding
        nc = self.imageshape[1]
        nr = self.imageshape[0]

        r1 = ext.point1.y
        r2 = ext.point2.y
        c1 = ext.point1.x
        c2 = ext.point2.x

        mirror_top = 0
        if r1 - padding < 0:
            mirror_top = -(r1 - padding)
        else:
            r1 = r1-padding

        mirror_left = 0
        if c1 - padding < 0:
            mirror_left = -(c1 - padding)
        else:
            c1 = c1-padding

        mirror_bot = 0
        if r2 + padding >= nr:
            mirror_bot = (r2 + padding) - nr
        else:
            r2 = r2+padding

        mirror_right = 0
        if c2 + padding >= nc:
            mirror_right = (c2 + padding) - nc
        else:
            c2 = c2+padding
            
        df = int(self.dec_factor)    
        ext2 = Extent(Point(c1*df,r1*df),Point(c2*df,r2*df))
        region = Extent(Point(c1-mirror_left,r1-mirror_top), Point(c2+mirror_right,r2+mirror_bot))
        return ext2, region, (mirror_top, mirror_left, mirror_bot, mirror_right)

    def __getitem__(self,tilenum):
        if tilenum < self.ntiles:
            # print('access %d' % tilenum)
            print('.',end="",flush=True)
            ext = self.get_tile_extent(tilenum)

            ext2, region, mirrorvals = self.get_padded_extent(ext)
            
            imgurl = None

            df = int(self.dec_factor)
            
            arr = self._jp2handle[to_slice(ext2,df)]
                
            (mirror_top, mirror_left, mirror_bot, mirror_right) = mirrorvals
            if mirror_top > 0:
                arr = np.pad(arr,[(mirror_top,0),(0,0),(0,0)],mode='reflect')
            if mirror_left > 0:
                arr = np.pad(arr,[(0,0),(mirror_left,0),(0,0)],mode='reflect')
            if mirror_bot> 0:
                arr = np.pad(arr,[(0,mirror_bot),(0,0),(0,0)],mode='reflect')
            if mirror_right > 0:
                arr = np.pad(arr,[(0,0),(0,mirror_right),(0,0)],mode='reflect')
            
            return arr, region, imgurl
        else:
            print('#',end="",flush=True)
            return np.zeros((0,0,3)), None, None

    def create(self):
        assert not os.path.exists(self.infoname)

        info = {'dtype':'uint8', 'shape':self.imageshape,'mmname':self.mmapfilename,'fname':self.jp2path}
        
        pickle.dump(info,open(self.infoname,'wb'))
        self.handle = np.memmap(self.mmapfilename,dtype='uint8',mode='w+',shape=self.imageshape )
        
        
        plan = get_multiproc_plan(self.ntiles,minwork=10)
        print(plan)
        
        # workerfunc2 = partial(workerfunc,self)
        data,ext,url,tilenum,pid=workerfunc(self,self.ntiles-1)
        start=datetime.now()
        print('load started...',end="")
        # if True:
        pid_tiles = {}
        with ProcessPoolExecutor(max_workers=plan.nworkers) as executor:
            for data,extent,url,tilenum,pid in executor.map(workerfunc,self,range(plan.worksize),chunksize=plan.rounds):
            # for ii in tqdm(range(plan.worksize)):
                # data,extent,_ = workerfunc2(ii)
                if extent is not None:
                    rsl,csl = to_slice(extent)
                    self.handle[rsl,csl,:]=data
                if pid not in pid_tiles:
                    pid_tiles[pid]=[]
                pid_tiles[pid].append(tilenum)

        print('loaded. syncing...',end="")
        loadend = datetime.now()
        self.handle.flush()
        flushend = datetime.now()
        print('done')
        for pid,tiles in pid_tiles.items():
            print(pid,len(tiles))
        return loadend-start,flushend-loadend # loadtime, flushtime

def workerfortest(tilenum):
    print('.',end="",flush=True)
    return tilenum, os.getpid()

def test_plan():
    print('testing procplan')
    plan = get_multiproc_plan(400,minwork=10)
    print(plan)
    pid_tiles = {}
    print('starting map')
    with ProcessPoolExecutor(max_workers=plan.nworkers) as executor:
        for tilenum,pid in executor.map(workerfortest,range(plan.worksize),chunksize=plan.rounds):
        
            if pid not in pid_tiles:
                pid_tiles[pid]=[]
            pid_tiles[pid].append(tilenum)    

    print('map done')    
    for pid,tiles in pid_tiles.items():
        print(pid,len(tiles))

if __name__=="__main__":
    test_plan()
