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
from pykafka.common import OffsetType

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    
KAFURL = app_config['events']['hostname']
KAFPORT = app_config['events']['port']
KAFTOPIC = app_config['events']['topic']

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger') 

def get_addItem(index): 
    """ Get BP Reading in History """ 
    hostname = "%s:%d" % (KAFURL, KAFPORT) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(KAFTOPIC)]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving item at index %d" % index) 
    
    try: 
        for msg in consumer:
            print(msg['type'])
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str)
            print(msg) 
            if msg['type'] == 'pickupitem' and index == count:
                return msg['payload'], 200
            count += 1
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find BP at index %d" % index) 
    return { "message": "Not Found"}, 404

def get_addXP(index): 
    """ Get BP Reading in History """ 
    hostname = "%s:%d" % (KAFURL, KAFPORT)
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(KAFTOPIC)] 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving item at index %d" % index)
    list = []
    count = 0
    try: 
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            if msg['type'] == 'levelup' and index == count:
                return msg['payload'], 200
            count += 1
               
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find BP at index %d" % index) 
    return { "message": "Not Found"}, 404




app = connexion.FlaskApp(__name__, specification_dir='') 
app.add_api("openapi.yml") 
 
if __name__ == "__main__": 
    app.run(port=8083)