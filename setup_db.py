
import psycopg2 
import sys
import os
from datetime import datetime

if __name__=="__main__":
    
    bsid = sys.argv[1]  # e.g. ss37
    sec = sys.argv[2]
    algo = sys.argv[3] # e.g. hover_net
    ver = sys.argv[4]   # e.g. v1
    inputarg = sys.argv[5] # jp2path
    dt = sys.argv[6]

    dbuser=os.getenv('POSTGRES_USERNAME','postgres')
    dbpass=os.getenv('POSTGRES_PASSWORD','admin123')
    dbhost=os.getenv('POSTGRES_HOST','172.17.0.1')
    dbport=os.getenv('POSTGRES_PORT','5432')
    
    conn=psycopg2.connect(database='postgres',user=dbuser,password=dbpass,host=dbhost,port=int(dbport))
    
    conn.autocommit=True
    
    dbname = bsid
    
    with conn.cursor() as cursor:
        try:
            cursor.execute('create database '+dbname)
        except:
            print('db not created')

    conn.close()
    
    conn=psycopg2.connect(database=dbname,user=dbuser,password=dbpass,host=dbhost,port=int(dbport))
    
    # dt = datetime.now().strftime('%y%h%d_%H%M')
    
    with conn.cursor() as cursor:

        cursor.execute('CREATE EXTENSION IF NOT EXISTS plpgsql')
        cursor.execute('CREATE EXTENSION postgis')

        cursor.execute(f'create table nissl_detections_{dt} (section int, centroid POINT, tl POINT, br POINT, celltypeid int, celltypeprob float)')
        
        cursor.execute('create table if not exists summary (name varchar(20), algorithm varchar(50), version varchar(10), inputarg text)')
        cursor.execute(f"insert into summary (name, algorithm, version, inputarg) values ('nissl_detections_{dt}','{algo}','{ver}','{inputarg}')")
        

    conn.commit()
    conn.close()
