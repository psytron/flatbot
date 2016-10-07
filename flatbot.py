

# DOCUMENTATION:
# THIS FILE IS A DOCKER PROCESS WHICH TRANSLATES INCOMING FLAT-FILES ( CSV, XLS ) INTO JSON POST-REQUESTS
# A SINGLE PARAMETER IN THE UPSTART JOB (DOMAIN) SIMULTANEOUSLY POINTS THE APP AT DIRECTORY
# AND PROPAGATES DOMAIN ACROSS ANY SIGNALS FOUND IN CLIENTS UPLOAD DIRECTORY
import csv; import os; import sys; import json; import xlrd; import mimetypes; import time; import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sys import platform
import json; import requests
from datetime import datetime



# CONFIG PARAMETERS CLIENT USER / DIR
# PROPAGATE TO INCOMING DISCOVERIES AND DIRS
arg1 = sys.argv[1:][0]
domain_id = arg1 if len(arg1)>1 else 'hurley'
if( platform == 'darwin' ):
    inbox_dir = '../exports/sftp/INBOX/'
    error_dir = '../exports/sftp/ERROR/'
    archive_dir = '../exports/sftp/ARCHIVE/'
    receive_url = 'http://localhost:8000/sftp/'
else:
    inbox_dir = '/home/'+domain_id+'/sftp/INBOX/'
    error_dir = '/home/'+domain_id+'/sftp/ERROR/'
    archive_dir = '/home/'+domain_id+'/sftp/ARCHIVE/'
    receive_url = 'https://octopus.wellopp.com/sftp/'

print('STARTING FLATBOT with PARAM: ',domain_id )


# BREAKDOWN CSV FILE INTO JSON CHUNKS
def process_csv( path_in , filename ):
    print('  process_csv( ',path_in,' )')
    entries=[]
    try:
        with open( path_in, newline='' ) as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read() , delimiters='|,')
            csvfile.seek(0)
            reader = csv.reader( csvfile, delimiter=dialect.delimiter, quotechar='"' )
            # convert rows to obj
            er = enumerate(reader)
            # er = enumerate(reader,start=1) # remove the IF later
            for i, row in er:
                if( i == 0 ):
                    legend=row
                    print('Header in parse: ',row)
                else:
                    obj = {}
                    for ndx,vl in enumerate( row ):
                        obj[ legend[ndx] ] = row[ndx]
                    obj_out = dict( (k.lower(), v) for k,v in obj.items())
                    obj_out['domain']=domain_id
                    post_json( obj_out )
            return True
    except Exception as e:
        print("Exception in ParseCSV ", e)
        return False



def process_csv_lx( path_in , filename ):
    entries=[]
    try:
        with open( path_in, newline='' ) as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read() , delimiters='|,')
            csvfile.seek(0)
            reader = csv.reader( csvfile, delimiter=dialect.delimiter, quotechar='"' )
            # convert rows to obj
            er = enumerate(reader)
            # er = enumerate(reader,start=1) # remove the IF later
            print('first_name'+','+'last_name'+','+'birth_date'+','+'address'+','+'city'+','+'state'+','+'zip'+','+'gender')
            for i, row in er:
                if( i == 0 ):
                    legend=row
                else:
                    obj = {}
                    for ndx,vl in enumerate( row ):
                        obj[ legend[ndx] ] = row[ndx]
                    obj_out = dict( (k.lower(), v) for k,v in obj.items())
                    obj_out['domain']=domain_id
                    stripped_date = datetime.strptime( obj_out['birth_date'] , '%m/%d/%Y' )
                    obj_out['birth_date']='{:%Y-%m-%d}'.format( stripped_date )

                    print( obj_out['pat_first_name']+','+ obj_out['pat_last_name']+','+ obj_out['birth_date'] +','+ obj_out['address_line_1']+','+ obj_out['city']+','+ obj_out['state']+','+obj_out['zip']+','+'F')
            return True
    except Exception as e:
        print("Exception in ParseCSV ", e)
        return False





# BREAKDOWN XLS FILE INTO JSON CHUNKS
def process_xls( path_in , filename ):
    entries = []
    workbook = xlrd.open_workbook( path_in )
    sheet = workbook.sheet_by_index(0)
    legend = sheet.row_values(0)
    for rownum in range( sheet.nrows ):
        cols = sheet.row_values( rownum )
        obj={}
        # convert rows to obj :
        if( rownum > 0 ):
            for vl,vx in enumerate( cols ):
                obj[ legend[vl] ]=cols[vl]
            obj_out = dict( (k.lower(), v) for k,v in obj.items())
            obj_out['domain']= domain_id
            post_json( obj_out )
    return True



# SEND SINGLE TO SERVER
def post_json( json_cluster ):
    print('Attempting to POST_JSON to: ', receive_url , ' Payload:', json_cluster  )
    r = requests.post( receive_url, json=json_cluster , verify=False )
    print('Response Code: ',r.status_code)


def process_json( path_in , filename ):
    string_rep = json.loads( open(path_in).read())
    post_json( string_rep )
    return True



# MAIN LOOP FOR RUNNING THROUGH UPDATED FILES
def scan_dir(self):
    for root, dirs, files in os.walk( inbox_dir, topdown=False):
        for filename in files:
            # INSPECT FILE ONE BY ONE :
            z_extension = os.path.splitext(filename)[1][1:]
            z_path = os.path.join( root, filename )
            z_mime = mimetypes.guess_type( z_path )
            if z_extension == 'csv':
                res = process_csv( z_path , filename )
            elif z_extension == 'xlsx':
                res = process_xls( z_path , filename )
            elif z_extension == 'txt':
                res = process_csv( z_path , filename )
            elif z_extension == 'json':
                res = process_json( z_path , filename )
            else:
                res = False
            # MOVE FILE BASED ON STATUS
            if( res == True ):
                shutil.move( z_path , archive_dir + filename )
                print( " MOVILE FILE: "+z_path)
            else:
                shutil.move( z_path , error_dir + filename )
                print( " MOVILE FILE: "+z_path)
            # here would be cool to make    c.extract()   returns True if success False if fail
            # it also updates its descendant cluters





# FILE CHANGE DETECTION
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        scan_dir( self )

if __name__ == "__main__":
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=inbox_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()