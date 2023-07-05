import psycopg2
from collections import namedtuple
import numpy as np
import json

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

def get_points_within(biosampleid,algo,ext,conn,date='latest'):
    
    boxprop = as_bbox(ext)

    gj_output = {}

    with conn.cursor() as curs:
        ls = pg_linestring(ext)

        if date=='latest':
            curs.execute("select name from summary order by name desc limit 1")
            tablename = curs.fetchone()[0]
        else:
            tablename = algo+'_'+date

        curs.execute(f"select section,centroid from {tablename} where (section between 1700 and 1710) and ST_Within(centroid::geometry,ST_Envelope('{ls}'))")

        section_points = {}
        for res in curs:
            sec = res[0]
            cen = [float(v) for v in res[1][1:-1].split(',')]
            if sec not in section_points:
                section_points[sec]=[]
            section_points[sec].append(cen)
            
        # print(curs.fetchone())
        # print(curs.query)
        
        for sec,points in section_points.items():
            gj_output[sec] = gj_multipoint(points,section=sec,bbox=boxprop,count=len(points))

    return gj_output


if __name__=="__main__":

    biosampleid = 'b37'
    algo = 'nissl_detections'

    p1 = Point(14000,23000) # c,r
    p2 = Point(18000,25000)
    ext = Extent(p1,p2)

    conn = psycopg2.connect(dbname=biosampleid,user='postgres',password='admin123',host='127.0.0.1',port=5432)

    gj_output = get_points_within(biosampleid,algo,ext,conn,date='test')

    json.dump(gj_output,open('tmp.json','wt'))

    conn.close()

