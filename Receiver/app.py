from xml.dom.minidom import CharacterData
import connexion
import logging.config
import json 
from connexion import NoContent 
import logging
import requests
import yaml
import uuid
import datetime
from pykafka import KafkaClient

DBURL1 = "http://localhost:8090/characters/pickupitem"
DBURL2 = "http://localhost:8090/characters/levelup"
# MAX_EVENTS = 10
# EVENT_FILE = "events.json"

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    
KAFURL = app_config['events']['hostname']
KAFPORT = app_config['events']['port']
KAFTOPIC = app_config['events']['topic']
    
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger') 

 
def addItem(body):
    """ Receives a gain item event """
    currentId = str(uuid.uuid4())

    recievelog = f"Received event addItem request with a trace id of {currentId}"
    logging.info(recievelog)
    writelog(recievelog)
    
    body['traceid'] = currentId
    body['timestamp'] = str(datetime.datetime.now())

    # response = requests.post(DBURL1, json = body)
    client = KafkaClient(hosts=f'{KAFURL}:{KAFPORT}') 
    topic = client.topics[str.encode(KAFTOPIC)] 
    producer = topic.get_sync_producer() 
 
    msg = { "type": "pickupitem",  
            "datetime" :    
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),  
            "payload": body } 
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    returnlog = f"Returned event addItem response (Id: {currentId}) with status 201"
    logging.info(returnlog)
    writelog(returnlog)
    return 201
# response.status_code


def addXP(body):
    """ Receives a add xp event """
    currentId = str(uuid.uuid4())
    recievelog = f"Received event addXP request with a trace id of {currentId}"
    logging.info(recievelog)
    writelog(recievelog)
    body['traceid'] = currentId
    body['timestamp'] = str(datetime.datetime.now())

    client = KafkaClient(hosts=f'{KAFURL}:{KAFPORT}') 
    topic = client.topics[str.encode(KAFTOPIC)] 
    producer = topic.get_sync_producer()
    

    msg = { "type": "levelup",  
            "datetime" :    
            datetime.datetime.now().strftime( 
            "%Y-%m-%dT%H:%M:%S"),  
            "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))    

    # response = requests.post(DBURL2, json = body)
    print(body)
    returnlog = f"Returned event addXP response (Id: {currentId}) with status 201"
    logging.info(returnlog)
    writelog(returnlog)
    return 201
# response.status_code

def writelog(logstring):
    file_object = open('app.log', 'a')
    file_object.write(logstring)
    file_object.close()
 


app = connexion.FlaskApp(__name__, specification_dir='') 
app.add_api("openapi.yml") 
 
if __name__ == "__main__": 
    app.run(port=8080)
    
