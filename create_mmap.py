from misc.jp2_converter import MmapCreator
import sys

if __name__=="__main__":
    jp2path = sys.argv[1]
    mmapdir = sys.argv[2]

    obj = MmapCreator(jp2path.strip(),mmapdir.strip())
    loadtime,flushtime = obj.create()
    print('load time', loadtime)
    print('flush time', flushtime)
