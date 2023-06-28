from misc.jp2_converter import GlymurAccessor, create_mmap
import sys

if __name__=="__main__":
    jp2path = sys.argv[1]
    mmapdir = sys.argv[2]

    accessor = GlymurAccessor(jp2path.strip())
    loadtime,flushtime = create_mmap(accessor,mmapdir.strip())
    print('load time', loadtime)
    print('flush time', flushtime)
