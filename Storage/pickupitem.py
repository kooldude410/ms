from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class pickupitem(Base):
    """adds an item event"""

    __tablename__ = "pickupitem"

    id = Column(Integer, primary_key=True)
    characterId = Column(Integer, nullable=False)
    itemID = Column(String(250), nullable=False)
    itemQuantity = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    traceid = Column(String(250), nullable=False)

    def __init__(self, characterId, itemID,itemQuantity, timestamp, traceid):
        """ adds item to db, yeah in hindsight, the object-oreientedness is terrible """
        self.characterId = characterId
        self.itemID = itemID
        self.itemQuantity = itemQuantity
        self.timestamp = timestamp
        self.traceid = traceid
        
    def to_dict(self):
        """ Dictionary Representation of a item gain event """
        dict = {}
        dict['id'] = self.id
        dict['characterId'] = self.characterId
        dict['itemID'] = self.itemID
        dict['itemQuantity'] = self.itemQuantity
        dict['timestamp'] = self.timestamp
        dict['traceid'] = self.traceid

        return dict
