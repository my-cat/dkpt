command= (
    ( 0x0001,	"log out " ),
    ( 0x0004,	"Update User information" ),
    ( 0x0005,	"Search user" ),
    ( 0x0006,	"Get User informationBroadcast" ),
    ( 0x0009,	"Add friend no auth" ),
    ( 0x000a,	"Delete user" ),
    ( 0x000b,	"Add friend by auth" ),
    ( 0x000d,	"Set status" ),
    ( 0x0012,	"Confirmation of receiving message from server" ),
    ( 0x0016,	"Send message" ),
    ( 0x0017,	"Receive message" ),
    ( 0x0018,	"Retrieve information" ),
    ( 0x001a,	"Reserved " ),
    ( 0x001c,	"Delete Me" ),
    ( 0x001d,	"Request KEY" ),
    ( 0x0021,	"Cell Phone" ),
    ( 0x0022,	"Log in" ),
    ( 0x0026,	"Get friend list" ),
    ( 0x0027,	"Get friend online" ),
    ( 0x0029,	"Cell PHONE" ),
    ( 0x0030,	"Operation on group" ),
    ( 0x0031,	"Log in test" ),
    ( 0x003c,	"Group name operation" ),
    ( 0x003d,	"Upload group friend" ),
    ( 0x003e,	"MEMO Operation" ),
    ( 0x0058,	"Download group friend" ),
    ( 0x005c,	"Get level" ),
    ( 0x0062,	"Request login" ),
    ( 0x0065,	"Request extra information" ),
    ( 0x0067,	"Signature operation" ),
    ( 0x0080,	"Receive system message" ),
    ( 0x0081,	"Get status of friend" ),
    ( 0x00b5,	"Get friend's status of group" ),
    ( 0,      None ))
commanddict={}
for k in command:
    commanddict[k[0]]=k[1]
#print (commanddict)
import dpkt
'''
Protocol Flag:     8bit unsigned
Sender Flag:       16bit unsigned
Command Number:    16bit unsigned
Sequence Number:   16bit unsigned
OICQ  Number:      32bit unsigned
Data:              Variable Length data
'''
class OICQ(dpkt.Packet):
    __hdr__= (  
        ('p_fg','B',0 ),
        ('send','H' ,0),
        ('com_n','H',0),
        ('eq_n','H',0),
        ('qq','I',0)
        )

    def  parse_command(self):
        self.com_n =commanddic[self.com_n]
    def __str__(self):

            
        if self.com_n in commanddict.keys():
            
            self.com_n =commanddict[self.com_n]
        return dpkt.Packet.__str__(self)
