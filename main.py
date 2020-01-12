import logging
import socket
import Packet 
import sys
import json


config_file = open('config.json')
Config      = json.load(config_file)
config_file.close()

def UInt32ToByteArray(value):
    ar = bytearray()
    ar.append(value & 0xFF)
    ar.append((value>>8) & 0xFF)
    ar.append((value>>16) & 0xFF)
    ar.append((value>>24) & 0xFF)
    return ar

def UInt16ToByteArray(value):
    ar = bytearray()
    ar.append(value & 0xFF)
    ar.append((value>>8) & 0xFF)
    return ar

class Server:
    

    @staticmethod
    def GetServerRulesPacket(recp):
        packet = bytearray()
        packet.extend(recp[:12])
        rules = Config['rules'].items()
        packet.extend(UInt16ToByteArray(len(rules)))
        for rule in rules:
            packet.append(len(rule[0]))
            packet.extend(bytearray(rule[0].encode()))
            packet.append(len(rule[1]))
            packet.extend(bytearray(rule[1].encode()))
        return bytes(packet)

    
    @staticmethod
    def GetBasicPlayersPacket(recp):
        packet = bytearray()
        packet.extend(recp[:12])
        players = Config['test']['OnlinePlayers']
        packet.extend(UInt16ToByteArray(len(players)))
        for player in players:
            packet.append(len(player['name']))
            packet.extend(bytearray(player['name'].encode()))
            packet.extend(UInt32ToByteArray(player['score']))
        return bytes(packet)
    
    @staticmethod
    def GetDetailedPlayersPacket(recp):
        packet = bytearray()
        packet.extend(recp[:12])
        players = Config['test']['OnlinePlayers']
        packet.extend(UInt16ToByteArray(len(players)))
        for player in players:
            packet.append(player['id'])
            packet.append(len(player['name']))
            packet.extend(bytearray(player['name'].encode()))
            packet.extend(UInt32ToByteArray(player['score']))
            packet.extend(UInt32ToByteArray(player['ping']))
        return bytes(packet)
    
    @staticmethod
    def GetServerInfoPacket(recp):
        packet = bytearray()
        packet.extend(recp[:12])
        packet.append(Config['password']!="")
        packet.extend(UInt16ToByteArray(len(Config['test']['OnlinePlayers'])))
        packet.extend(UInt16ToByteArray(Config['maxplayers']))
        packet.extend(UInt32ToByteArray(len(Config['hostname'])))
        packet.extend(bytearray(Config['hostname'].encode()))
        packet.extend(UInt32ToByteArray(len(Config['gamemode'])))
        packet.extend(bytearray(Config['gamemode'].encode()))
        packet.extend(UInt32ToByteArray(len(Config['language'])))
        packet.extend(bytearray(Config['language'].encode()))
        return bytes(packet)


class SampQuery:
    '''
    PACKET STRUCTURE:
        'SAMP' + IP[0] + IP[1] + IP[2] + IP[3] + PORT[0] + PORT[1] + TYPE
    The ip and port are for the server.
    The type can be:
        'i': Get server information.
        'c': Get basic players
        'd': Get detailed player info
        'r': Get Server rules
        'p': Ping
        'p0101': Attempt connection to server
    '''
    def __init__(self, msg):
        self.signature=str(msg[:4])
        self.ip=str(msg[4]) + '.' + str(msg[5]) + '.' + str(msg[6]) + '.' + str(msg[7])
        self.port= int(msg[8] + (msg[9]<<8))
        self.type= chr(msg[10])
    def __str__(self):
        return self.signature+'\t'+self.ip+'\t'+str(self.port)+'\t'+self.type


log = logging.getLogger('udp_server')
FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)


host='127.0.0.1'
port=1234
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

log.info("Listening on udp %s:%s" % (host, port))
s.bind((host, port))
while True:
    (data, addr) = s.recvfrom(128*1024)
    query = SampQuery(data)
    log.debug("@%s\t%r\t%s" % (addr, data, query.__str__()))
    if(query.type=='i'):
        d = Server.GetServerInfoPacket(data)
        s.sendto(d,  addr)
        print("  >>> Sending ", d)
    elif(query.type=='r'):
        d = Server.GetServerRulesPacket(data)
        s.sendto(d,  addr)
        print("  >>> Sending ", d)
    elif(query.type=='c'):
        d = Server.GetBasicPlayersPacket(data)
        s.sendto(d,  addr)
        print("  >>> Sending ", d)
    elif(query.type=='d'):
        d = Server.GetDetailedPlayersPacket(data)
        s.sendto(d,  addr)
        print("  >>> Sending ", d)
    elif(query.type=='p'):
        d = data
        s.sendto(d,  addr)
        print("  >>> Sending ", d)
