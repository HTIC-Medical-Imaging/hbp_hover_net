import psycopg2
from collections import namedtuple

Point = namedtuple('Point','x,y')
# Span = namedtuple('Span','w,h')
# Box = namedtuple('Box','point,span')
Extent = namedtuple('Extent','point1,point2')

def pg_linestring(ext):
    return f'LINESTRING({ext.point1.x} {ext.point1.y},{ext.point2.x} {ext.point2.y})'

if __name__=="__main__":
    conn = psycopg2.connect(dbname='b37',user='postgres',password='admin123',host='127.0.0.1',port=5432)

    p1 = Point(14000,23000)
    p2 = Point(18000,25000)
    ext = Extent(p1,p2)

    with conn.cursor() as curs:
        ls = pg_linestring(ext)
        curs.execute(f"select * from nissl_detections_test where ST_Within(centroid::geometry,ST_Envelope('{ls}'))")
        print(curs.fetchone())
        # print(curs.query)
    
    conn.close()
