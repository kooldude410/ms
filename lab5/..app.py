from xml.dom.minidom import CharacterData
import logging.config
import connexion
from connexion import NoContent


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler

import swagger_ui_bundle
import requests

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

DBURL1 = "http://localhost:8090/characters/pickupitem"
DBURL2 = "http://localhost:8090/characters/levelup"

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
    starttime = datetime.datetime.now()
    sampletime = {'timestamp' : starttime - datetime.timedelta(minutes=2)}
    
    itemcall = requests.get(url = DBURL1, params = sampletime)
    iteminfo = itemcall.json()
    if itemcall.status_code == 200:
        logger.info(f"Recieved {len(iteminfo)} item events.")
    else:
        logger.error(f"Recieved {itemcall.status_code} status code.")

    xpcall = requests.get(url = DBURL2, params = sampletime)
    xpinfo = xpcall.json()
    if xpcall.status_code == 200:
        logger.info(f"Recieved {len(xpinfo)} item events.")
    else:
        logger.error(f"Recieved {xpcall.status_code} status code.")
    
    item_total = 0
    item_max_gain = 0
    xp_total = 0
    xp_max_gain = 0
    
    for items in iteminfo:
        logger.debug(f"Processed item event {items['traceid']}")
        item_total += items['itemQuantity']
        if item_max_gain < items['itemQuantity']:
            item_max_gain = items['itemQuantity']
            
    for items in xpinfo:
        logger.debug(f"Processed xp event {items['traceid']}")
        xp_total += items['xpAmount']
        if xp_max_gain < items['xpAmount']:
            xp_max_gain = items['xpAmount']
    
    parsedstats = stats(item_total,
                       item_max_gain,
                       xp_total,
                       xp_max_gain,
                       starttime)

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
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
    

