import psycopg2
from collections import namedtuple
import numpy as np
import json
import csv

Point = namedtuple('Point','x,y')
# Span = namedtuple('Span','w,h')
# Box = namedtuple('Box','point,span')
Extent = namedtuple('Extent','point1,point2')

def as_bbox(ext):
    return {'data':[[ext.point1.x, ext.point1.y],[ext.point2.x, ext.point2.y]]}

def pg_linestring(ext):
    return f'LINESTRING({ext.point1.x} {ext.point1.y},{ext.point2.x} {ext.point2.y})'

def gj_multipoint(points,**kwargs):
    return {
        'feature':{
                'type':'Feature',
                'properties':kwargs,
                'geometry': {
                    'type':'MultiPoint',
                    'coordinates':[points]
                }
            }
        }

def as_homogeneous(points):
    npts = points.shape[0]
    return np.hstack((points,np.ones((npts,1),points.dtype)))

def pixel_to_mm3d(points,spacing, org):
    # points: nx3
    # spacing: tuple (sx,sy,sz) in mm per pix
    # org: tuple (cx,cy,cz) in pix

    spc_mtx = np.eye(4)
    spc_mtx[0,0]=spacing[0]
    spc_mtx[1,1]=spacing[1]
    spc_mtx[2,2]=spacing[2]
    spc_mtx[0,-1]=-org[0]*spacing[0]
    spc_mtx[1,-1]=-org[1]*spacing[1]
    spc_mtx[2,-1]=-org[2]*spacing[2]
    return np.dot(as_homogeneous(np.array(points)),spc_mtx.T)[:,:-1]

def get_points_within(algo,ext,slc,conn,date='latest'):
    

    with conn.cursor() as curs:
        ls = pg_linestring(ext)

        if date=='latest':
            curs.execute("select name from summary order by name desc limit 1")
            tablename = curs.fetchone()[0]
        else:
            tablename = algo+'_'+date

        curs.execute(f"select section,centroid from {tablename} where (section between {slc.start} and {slc.stop}) and ST_Within(centroid::geometry,ST_Envelope('{ls}'))")

        section_points = {}
        cloud_points = []

        for res in curs:
            sec = res[0]
            cen = [float(v) for v in res[1][1:-1].split(',')]
            if sec not in section_points:
                section_points[sec]=[]
            section_points[sec].append([cen[0],-cen[1]])
            cloud_points.append([cen[0],cen[1],float(sec)])
            
        # print(curs.fetchone())
        # print(curs.query)

    return section_points, cloud_points


if __name__=="__main__":

    biosampleid = 'b37'
    algo = 'nissl_detections'

    p1 = Point(14000,23000) # c,r
    p2 = Point(18000,25000)
    ext = Extent(p1,p2)

    conn = psycopg2.connect(dbname=biosampleid,user='postgres',password='admin123',host='127.0.0.1',port=5432)

    section_points,cloud_points = get_points_within(algo,ext,slice(1700,1710),conn,date='test')

    boxprop = as_bbox(ext)

    gj_output = {}
    for sec,points in section_points.items():
        gj_output[sec] = gj_multipoint(points,section=sec,bbox=boxprop,count=len(points))

    
    json.dump(gj_output,open('tmp.json','wt'))

    with open('tmp.csv','wt',newline="") as fp:
        writer = csv.writer(fp)
        writer.writerows(pixel_to_mm3d(cloud_points,(1/2000,1/2000,1/50),(40000,40000,1303)))
        

    conn.close()

