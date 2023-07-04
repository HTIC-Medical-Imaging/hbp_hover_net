
import psycopg2 
import sys
import os

if __name__=="__main__":
    
    ssid = 'ss37'
    if len(sys.argv)>1:
        ssid = sys.argv[1]

    dbuser=os.getenv('POSTGRES_USERNAME','postgres')
    dbpass=os.getenv('POSTGRES_PASSWORD','admin123')
    dbhost=os.getenv('POSTGRES_HOST','127.0.0.1')
    dbport=os.getenv('POSTGRES_PORT','5432')
    
    conn=psycopg2.connect(database='postgres',user=dbuser,password=dbpass,host=dbhost,port=int(dbport))
    
    conn.autocommit=True
    
    dbname = ssid
    
    with conn.cursor() as cursor:
        try:
            cursor.execute('create database '+dbname)
        except:
            print('db not created')

    conn.close()
    
    conn=psycopg2.connect(database=dbname,user=dbuser,password=dbpass,host=dbhost,port=int(dbport))
    
    with conn.cursor() as cursor:

        cursor.execute('CREATE EXTENSION IF NOT EXISTS plpgsql')
        cursor.execute('CREATE EXTENSION postgis')

        cursor.execute('create table nissl_detections (section int, centroid POINT, tl POINT, br POINT, celltypeid int, celltypeprob float)')
        
        # cursor.execute('insert into nissl_detections (section,centroid, tl, br, celltypeid, celltypeprob)values(1078, ST_MakePoint(100,-80)::point, ST_MakePoint(90,-90)::point, ST_MakePoint(110,-70)::point, 3, 0.718)')

    conn.commit()
    conn.close()
