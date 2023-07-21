from misc.jp2_converter import Accessor, create_mmap, get_mmap_name
import sys
import os
from datetime import datetime


def main(jp2path, mmapdir, use_glymur=False,use_kdu=True):

    mmapfilename, infoname = get_mmap_name(jp2path)
    if not os.path.exists(mmapdir+'/'+infoname):
        if use_glymur:
            accessor = Accessor(jp2path)
            loadtime,flushtime = create_mmap(accessor,mmapdir,concurrent=True)    

        elif use_kdu:
            start = datetime.now()
            basenm = os.path.basename(jp2path)
            tmpoutname = mmapdir+'/'+basenm[:-4]+'.tif'
            print(f'starting kdu_expand {basenm}')
            os.system(f'LD_LIBRARY_PATH=$PWD/lib bin/kdu_expand -num_threads 64 -i {jp2path} -o {tmpoutname}')
            loadend = datetime.now()

            loadtime = loadend - start
            print('load time', loadtime)

            accessor = Accessor(tmpoutname)
            accessor.imgpath = jp2path # to set nameprefix of _info.pkl
            create_mmap(accessor, mmapdir, concurrent=False)
            
            flushend = datetime.now()
            flushtime = flushend - loadend
            os.unlink(tmpoutname)
        
            print('flush time', flushtime)


if __name__=="__main__":

    jp2path = sys.argv[1].strip()
    mmapdir = sys.argv[2].strip()
    main(jp2path,mmapdir)
    
