import pandas as pd
import psycopg2
import sys
import os
from tqdm import tqdm

if __name__=="__main__":
    bsid = sys.argv[1]
    secno = sys.argv[2]
    csvdir = sys.argv[3]
    csvprefix = sys.argv[4]
    dt = sys.argv[5]

    csvpath = csvdir+'/json/'+csvprefix[:-4]+'_objects.csv'
    namepart = csvpath.split('_')[-3]

    assert secno in namepart, 'check secno argument (%s) expecting %s' % (secno, namepart)

    records = pd.read_csv(csvpath)
    N = records.shape[0]

    dbuser=os.getenv('POSTGRES_USERNAME','postgres')
    dbpass=os.getenv('POSTGRES_PASSWORD','admin123')
    dbhost=os.getenv('POSTGRES_HOST','172.17.0.7')
    dbport=os.getenv('POSTGRES_PORT','5432')

    conn=psycopg2.connect(dbname=bsid.lower(),user=dbuser,password=dbpass,host=dbhost,port=int(dbport))

    with conn.cursor() as cursor:

        for ii,rec in tqdm(records.iterrows(),total=N):
            bbox_tl = rec.bbox_cmin,rec.bbox_rmin
            bbox_br = rec.bbox_cmax,rec.bbox_rmax
            cx = rec.cen_c+bbox_tl[0]
            cy = rec.cen_r+bbox_tl[1]
            cursor.execute(f'insert into nissl_detections_{dt} (section, centroid, tl, br, celltypeid, celltypeprob) values ({secno}, ST_MakePoint({cx},{cy})::point, ST_MakePoint({bbox_tl[0]},{bbox_tl[1]})::point, ST_MakePoint({bbox_br[0]},{bbox_br[1]})::point, {rec.type}, {rec.type_prob})')
            if ii%100==0:
                conn.commit()

    conn.commit()
    conn.close()
