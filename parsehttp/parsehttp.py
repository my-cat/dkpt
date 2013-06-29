#from  http import *
import sys
sys.path.append('/home/misery/mypkt')
from ipaddress import IPv4Address 
from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import *
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker
import pcap,dpkt
import ip
import ethernet,tcp,udp,http_pro
import datetime
import time
Base = declarative_base()
class User(Base):
    __tablename__='users'
    
    ip= Column(String, primary_key=True)
    name= Column(String)

    def __init__(self,ip,name):
        self.name= name
        self.ip=ip

    def __repr__(self):
        return "User ('%s','%s')"%(self.name,self.ip)
  
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.sqlite import DATETIME
class Website(Base):
    __tablename__='websites'
    id=Column(Integer,primary_key=True)
    websites =Column(String)
    mytime=Column(DATETIME)
    user_ip=Column(String,ForeignKey('users.ip'))
    user=relationship('User',backref=backref('websites',order_by=id))
        
    def __init__(self,ip,websites,time):
        self.user_ip=ip
        self.websites=websites
        self.mytime=time
    
    def __repr__(self):
        return "websites (%s)" %self.websites
    
    def parse(self,buf):
        pass

def make_table(dbname):
    engine=create_engine(dbname,echo=True)
    Base.metadata.create_all(engine)    
    return engine

def read_file(filename):
    f=open(filename, 'rb')
    file1 = pcap.Reader(f)
    return file1

def parse_requset(ts,buf):
    try:
        eth = ethernet.Ethernet(buf)
        if eth.type == 2048 :
            ip1=eth.data
            tcp1=ip1.data
            ip2=IPv4Address(ip1.src)
            try:
                r= http_pro.Request(tcp1.data)
                
                web= Website(str(ip2),r.headers['host'],datetime.datetime.fromtimestamp(ts))
                return web
            except dpkt.UnpackError:
                pass
    except:
        pass
def process_loop(filename,session):
    file1=read_file(filename)
    for ts , buf in file1:
        web= parse_requset(ts,buf)
        if web == None:
            pass
        else:
            session.add(web)
    session.commit()

def make_session(engine):
    Session=sessionmaker(bind=engine)
    session=Session()
    return session
def same_website(ip,website):
    #This function is for check wether the user in the same website , if it is 
    # we just update the time,,,,,maybe we can count ...but ..actually   i 
    # have not so much time to finish it !!!!!!
    
    pass
def begin(filename,dbname):
    engine=  make_table(dbname)
    session=make_session(engine)
#    session.add(User('202.206.219.98','huangjinchao'))
    process_loop(filename,session)

begin('ssds.pcap','sqlite:///mem2.db')

