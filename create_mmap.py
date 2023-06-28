from misc.jp2_converter import Accessor, create_mmap
import sys
import os
from datetime import datetime

if __name__=="__main__":
    jp2path = sys.argv[1]
    mmapdir = sys.argv[2]
    use_glymur = False

    use_kdu = True

    if use_glymur:
        accessor = Accessor(jp2path.strip())
        loadtime,flushtime = create_mmap(accessor,mmapdir.strip(),concurrent=True)    

    elif use_kdu:
        start = datetime.now()
        os.system(f'LD_LIBRARY_PATH=$PWD/lib ./kdu_expand -num_threads 64 -i {jp2path.strip()} -o /cache/tmp.tif')
        loadend = datetime.now()
        accessor = Accessor('/cache/tmp.tif')
        create_mmap(accessor,mmapdir.strip(),concurrent=False)
        flushend = datetime.now()
        loadtime = loadend - start
        flushtime = flushend - loadend
    
    print('load time', loadtime)
    print('flush time', flushtime)

    if use_kdu:
        os.unlink('/cache/tmp.tif')
