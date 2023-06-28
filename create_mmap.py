from misc.jp2_converter import Accessor, create_mmap
import sys
import os
from datetime import datetime

if __name__=="__main__":
    jp2path = sys.argv[1].strip()
    mmapdir = sys.argv[2].strip()
    use_glymur = False

    use_kdu = True

    if use_glymur:
        accessor = Accessor(jp2path)
        loadtime,flushtime = create_mmap(accessor,mmapdir,concurrent=True)    

    elif use_kdu:
        start = datetime.now()
        os.system(f'LD_LIBRARY_PATH=$PWD/lib ./kdu_expand -num_threads 64 -i {jp2path} -o /cache/tmp.tif')
        loadend = datetime.now()
        accessor = Accessor('/cache/tmp.tif')
        accessor.imgpath = jp2path # to set nameprefix of _info.pkl
        create_mmap(accessor, mmapdir, concurrent=False)
        flushend = datetime.now()
        loadtime = loadend - start
        flushtime = flushend - loadend
        os.unlink('/cache/tmp.tif')
    
    print('load time', loadtime)
    print('flush time', flushtime)

