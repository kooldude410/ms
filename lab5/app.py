from xml.dom.minidom import CharacterData
import logging.config
import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import swagger_ui_bundle
import requests
from flask_cors import CORS, cross_origin

from base import Base
from stats import stats

import yaml

import datetime
import json 
# import os.path

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')     

DBURL1 = "http://kafka.westus.cloudapp.azure.com:8090/characters/pickupitem"
DBURL2 = "http://kafka.westus.cloudapp.azure.com:8090/characters/levelup"

DB_ENGINE = create_engine("sqlite:///characters.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

scheduler = BackgroundScheduler()

def get_stats():
    '''get request for most recent event'''
    session = DB_SESSION()
    recentstats = (session.query(stats).order_by(stats.id.desc()).first()).to_dict()
    logger.debug(f'Recent stats called: total item gain {recentstats["item_total"]}, max item gain {recentstats["item_max_gain"]}, total xp gained {recentstats["xp_total"]}, max xp gained {recentstats["xp_max_gain"]}')
    session.close()
    logger.info('/event/stats get processing complete.')
    return recentstats, 200 
    
def populate_stats():
    """gets some events from storage service, then stores them"""
    
    session = DB_SESSION()
    #query the most recent entry
    laststats = session.query(stats).order_by(stats.last_updated.desc()).first().to_dict()
    
    #sets current time
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    # deltatime = datetime.datetime.strptime
    # sampletime = {'timestamp' : (last_updated - datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S.%f")}
    # deltatime = datetime.datetime.strptime(sampletime, "%Y-%m-%d %H:%M:%S.%f")
    # logger.debug(f"sampletime is {sampletime}")
    
    #start from timestamp of latest entry
    start_timestamp = laststats['last_updated']
    
    # itemurl = app_config["eventstore"]["url"] + "/characters/levelup?start_timestamp=" + start_timestamp + "&end_timestamp=" + current_timestamp
    # logger.debug(f"itemurl is {itemurl}")
    
    itemcall = requests.get(url = DBURL1, params = {"start_timestamp": start_timestamp, "end_timestamp": current_timestamp})
    logger.debug(f'itemcall is type {type(itemcall)}')
    
    iteminfo = itemcall.json()
    logger.debug(f'iteminfo is {iteminfo}')
    
    if itemcall.status_code == 200:
        logger.info(f"Recieved {len(iteminfo)} item events.")
    else:
        logger.error(f"Recieved {itemcall.status_code} status code.")


    # xpurl = app_config["eventstore"]["url"] + "/characters/levelup?start_timestamp=" + start_timestamp + "&end_timestamp=" + current_timestamp
    # logger.debug(f"xpurl is {xpurl}")
    
    xpcall = requests.get(url = DBURL2, params = {"start_timestamp": start_timestamp, "end_timestamp": current_timestamp})
    logger.debug(f'xpcall is type {type(xpcall)}')
    
    xpinfo = xpcall.json()
    logger.debug(f'iteminfo is {xpinfo}')
    
    if xpcall.status_code == 200:
        logger.info(f"Recieved {len(xpinfo)} item events.")
    else:
        logger.error(f"Recieved {xpcall.status_code} status code.")
    
    
    
    item_total = 0
    item_max_gain = 0
    xp_total = 0
    xp_max_gain = 0
    
    
    for items in iteminfo:
        logger.debug('Processed item event ' + items["traceid"])
        item_total += items['itemQuantity']
        if item_max_gain < items['itemQuantity']:
            item_max_gain = items['itemQuantity']
            
    for items in xpinfo:
        logger.debug("Processed xp event " + items['traceid'])
        xp_total += items['xpAmount']
        if xp_max_gain < items['xpAmount']:
            xp_max_gain = items['xpAmount']
    
    parsedstats = stats(item_total,
                       item_max_gain,
                       xp_total,
                       xp_max_gain,
                       current_timestamp)

    if (item_max_gain != 0) and (xp_max_gain != 0):
        session.add(parsedstats)

    session.commit()
    logger.info(f'Stats added: Total item gain {item_total}, max item gain {item_max_gain}, total xp gained {xp_total}, max xp gained {xp_max_gain}')
    session.close()
    logger.info("Perodic process interval completed")
    return logger.info('Start Periodic Processing') , 201

def init_scheduler(): 
    sched = BackgroundScheduler(daemon=True) 
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec']) 
    sched.start()
 
app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
    

