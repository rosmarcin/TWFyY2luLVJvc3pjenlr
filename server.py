from flask import Flask, request, abort
from flask import jsonify

from time import sleep, time
from datetime import datetime
import threading, signal
import atexit
import urllib.request
import json
from urllib.error import HTTPError, URLError

from socket import timeout

class Worker(object):
    # zwraca serializowane 
    # implementacja metody na potrzeby przykładu, zamiast pobrania z bazy

    urls={}
    fetch_history={}
    current_index=0 

    def saveUrl(self, url):
        self.current_index+=1
        self.urls[self.current_index]=url       
        return self.current_index
        
    def deleteUrl(self, id):
        if id:
            if id>0 and id<=self.current_index:
                del self.urls[id]
                print('Active threads: ', threading.active_count())
                return str({'id':id})
            else:
                return "ID not in database"
        else:
            return "ERROR missing ID"

    def getUrls(self):
        temp_list=[]
        for key, data in self.urls.items():
            temp_list.append({'id':key, 'url':data['url'], 'interval':data['interval']})
        return str(temp_list)

    def getUrl(self, id):
        if isinstance(id, (int)):
            if id>=0 and id<=len(self.urls):
                return str(self.urls[id])
            else:
                return "NOT FOUND!"
        else:
            #raise exception
            return 'error'

    def fetchUrl(self, url):
        print('Fetching : ', url)
        start_time = time()
        duration=0
        try:
            response = urllib.request.urlopen(url).read()
            duration= time() - start_time
        except (HTTPError, URLError) as err:
            response = None
        except timeout:
            response = None

        return {'response': response, 
        'duration': duration, 
        'created_at': str(int(round(time() * 1000))) }
    
    def saveContent(self, url_id, content):
        current_list=[]
        if url_id in self.fetch_history:
            current_list = list(self.fetch_history[url_id]) # gets list for current ID
            current_list.append(content)
        else:
            current_list.append(content)
        
        self.fetch_history[url_id]=current_list

    def run_job(self, id, periodic): 
        while True:
            run=list(self.urls.keys())
            if id in run:
                url = self.urls[id]['url']
                content = self.fetchUrl(url)
                self.saveContent(id,content)    
                sleep(int(self.urls[id]['interval']))
                
            else:
                print('Closing Thread : ', threading.currentThread().getName())
                break

def close_thread():
    print('Thread closed!')

def validate_json(json_obj):
    try:
        if json_obj['url'] and isinstance(json_obj['interval'], int):
            return True 
        else:
            return False
    except (KeyError, ValueError) as err:
        return False

worker = Worker()
app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(error):
    return "Not Found", 404


@app.errorhandler(400)
def bad_request(error):
    return "Bad Request", 400


@app.route('/')
def index():
    return 'Server works!'
    

@app.route('/api/fetcher', methods=['GET', 'POST', 'DELETE'])
def fetcher():
    if request.method=='POST':
        if request.json:
            if validate_json(request.json):
                id=worker.saveUrl(request.json)
                thread = threading.Thread(target=worker.run_job, args=(id,'periodic') )
                thread.daemon = True
                thread.start()  
                print('active threads: ', threading.active_count())
                return  jsonify({'id':id})
            else:
                abort(400)   
        # elif request.args.get('id'):
        #     return worker.updateUrl(request.json)
        else:
            abort(400)
    elif request.method=='GET':
        if request.args.get('id'):
            if int(request.args.get('id')) in worker.urls.keys():
                return str(worker.getUrl(int(request.args.get('id'))))
            else:
                abort(404)
        else:
            print('Active threads: ', threading.active_count())
            return str(worker.getUrls())
    elif request.method=='DELETE':
        if request.args.get('id'):
            return worker.deleteUrl(int(request.args.get('id')))

@app.route('/api/fetcher/<int:id>/history')
def getUrlHistory(id):
    if id and int(id) in worker.fetch_history.keys():
        return str(worker.fetch_history[int(id)])
    else:
        abort(404)
         
@app.route('/api/fetcher/history')
def getHistory():
    return str(worker.fetch_history)

atexit.register(close_thread)
app.run()
