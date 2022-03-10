from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class levelup(Base):
    """gaining level? yeah it doesnt make sense in hindsight"""

    __tablename__ = "levelup"

    id = Column(Integer, primary_key=True)
    characterId = Column(Integer, nullable=False)
    userId = Column(String(250), nullable=False)
    xpAmount = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    traceid = Column(String(250), nullable=False)

    def __init__(self, characterId, userId,xpAmount, timestamp, traceid):
        """ in function it adds XP """
        self.characterId = characterId
        self.userId = userId
        self.xpAmount = xpAmount
        self.timestamp = timestamp
        self.traceid = traceid

    def to_dict(self):
        """ Dictionary Representation of a xp gain event """
        dict = {}
        dict['id'] = self.id
        dict['characterId'] = self.characterId
        dict['userId'] = self.userId
        dict['xpAmount'] = self.xpAmount
        dict['timestamp'] = self.timestamp
        dict['traceid'] = self.traceid

        return dict
