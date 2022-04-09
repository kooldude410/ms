from sqlalchemy import Column, Integer, String, DateTime 
from base import Base 

class stats(Base): 
    """ Processing Statistics """ 
 
    __tablename__ = "stats" 
 
    id = Column(Integer, primary_key=True) 
    item_total = Column(Integer, nullable=False) 
    item_max_gain = Column(Integer, nullable=False) 
    xp_total = Column(Integer, nullable=False) 
    xp_max_gain = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)

 
    def __init__(self, item_total,item_max_gain,xp_total,xp_max_gain,last_updated): 
        """ Initializes a processing statistics objet """ 
        self.item_total = item_total 
        self.item_max_gain = item_max_gain 
        self.xp_total = xp_total 
        self.xp_max_gain = xp_max_gain
        self.last_updated = last_updated
 
    def to_dict(self): 
        """ Dictionary Representation of a statistics """ 
        dict = {} 
        dict['item_total'] = self.item_total 
        dict['item_max_gain'] = self.item_max_gain 
        dict['xp_total'] = self.xp_total 
        dict['xp_max_gain'] = self.xp_max_gain
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%d %H:%M:%S.%f")
 
        return dict