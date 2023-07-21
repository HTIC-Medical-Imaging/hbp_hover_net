import cucim
import glob

if __name__=="__main__":

    imgname = glob.glob('/data/JP2/*.jp2')[0]

    img = cucim.clara.CuImage(imgname)
    resolutions = img.resolutions
    level_dimensions = resolutions["level_dimensions"]
    level_count = resolutions["level_count"]
    thumb = img.read_region(location=[0,0], size=level_dimensions[level_count - 1], level=level_count - 1)
    

    