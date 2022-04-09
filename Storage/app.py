from xml.dom.minidom import CharacterData
import logging.config
import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from base import Base
from levelup import levelup
from pickupitem import pickupitem

import yaml
import datetime
import time
import json
 
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


with open(r'app_conf.yml') as file:
    APPCONF = yaml.load(file, Loader=yaml.FullLoader)
    
    
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')     

USER = APPCONF['datastore']['user']
PASSWORD = APPCONF['datastore']['password']
HOSTNAME = APPCONF['datastore']['hostname']
PORT = APPCONF['datastore']['port']
DB = APPCONF['datastore']['db']

DB_ENGINE = create_engine(f'mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DB}')
   
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

MAX_EVENTS = 10
EVENT_FILE = "events.json"

def addXP(body):
    """ Receives a xp gain event """

    session = DB_SESSION()
    dblog() 
    lvlup = levelup(body['characterId'],
                       body['userId'],
                        body['xpAmount'],
                       body['timestamp'],
                       body['traceid'])

    session.add(lvlup)

    session.commit()
    session.close()
    
    recievelog = f"Stored event addXP request with a trace id of {body['traceid']}"
    logging.debug(recievelog)
    
    #return NoContent, 201

    
def addItem(body):
    """ Receives a item pickup event """

    session = DB_SESSION()
    dblog() 
    pitem = pickupitem(body['characterId'],
                   body['itemID'],
                   body['itemQuantity'],
                   body['timestamp'],
                   body['traceid'])

    session.add(pitem)

    session.commit()
    session.close()

    recievelog = f"Stored event addItem request with a trace id of {body['traceid']}"
    logging.debug(recievelog)

    #return NoContent, 201

def getlastitem(timestamp, end_timestamp): 
    """ Gets new blood pressure readings after the timestamp """ 
 
    session = DB_SESSION()
    dblog() 
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") 
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    
    readings = session.query(pickupitem).filter(
        and_(pickupitem.timestamp >= timestamp_datetime,
             pickupitem.timestamp < end_timestamp_datetime)) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for litem gains after %s returns %d results" %  
                (timestamp, len(results_list))) 
    

 
    return results_list, 200 

def getlastxp(timestamp, end_timestamp): 
    """ Gets new blood pressure readings after the timestamp """ 
 
    session = DB_SESSION()
    dblog() 
 
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f") 
 
    readings = session.query(levelup).filter(
        and_(levelup.timestamp >= timestamp_datetime,
             levelup.timestamp < end_timestamp_datetime)) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for xp gains after %s returns %d results" %  
                (timestamp, len(results_list))) 
    
    return results_list, 200 


def dblog():
    logger.info("Connecting to DB. Hostname: %s, Port: %d" % (HOSTNAME,PORT))
    
    #return NoContent, 200

 
def process_messages(): 
    """ Process event messages """ 
    hostname = "%s:%d" % (APPCONF["events"]["hostname"],   
                          APPCONF["events"]["port"])
    max_retry = APPCONF["events"]["retry"]
    
    while retry < max_retry:
        logger.info(f"Try to connect Kafka Server, this is number {retry} try")
        try: 
            client = KafkaClient(hosts=hostname) 
            topic = client.topics[str.encode(APPCONF["events"]["topic"])]
            logger.info("Successfully connect to Kafka") 
            consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                                reset_offset_on_start=False, 
                                                auto_offset_reset=OffsetType.LATEST)
            break
        except:
            logger.error(f"Failed to connect to Kafka, this is number {retry} try")
            time.sleep(APPCONF["events"]["sleep"])
            retry += 1
            logger.info("retry in 10 second") 
    # Create a consume on a consumer group, that only reads new messages  
    # (uncommitted messages) when the service re-starts (i.e., it doesn't  
    # read all the old messages from the history in the message queue). 

 
    # This is blocking - it will wait for a new message 
    for msg in consumer: 
        msg_str = msg.value.decode('utf-8') 
        msg = json.loads(msg_str) 
        logger.info("Message: %s" % msg) 
 
        payload = msg["payload"]
        print("this is payload: ", payload)
 
        if msg["type"] == "levelup": 
            addXP(payload)

        elif msg["type"] == "pickupitem":
            addItem(payload)
        # Commit the new message as being read 
        consumer.commit_offsets()


 
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages) 
    t1.setDaemon(True) 
    t1.start()
    app.run(port=8090)
    

