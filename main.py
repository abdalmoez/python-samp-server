import logging
import socket
import Packet
import sys
import json
import random
import SampNetEncr
import binascii
from Reliability import *

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
def LOG_MSG(header, addr, data):
    log.debug("%s\t@%s\t%s" % (header, addr, binascii.hexlify(data)))
    
class Server:
    
    @staticmethod
    def RCONPacket(recp):
        
        pwdlen = int(recp[12] + (recp[13] << 8))
        idx = 14
        pwd = str(recp[idx:idx + pwdlen])
        idx += pwdlen

        if(pwd == Config['rcon_password']):
            cmdlen = int(recp[idx] + (recp[idx+1] << 8))
            idx += 2
            cmd = str(recp[idx:(idx + cmdlen)])
            idx += cmdlen

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
        'x': RCON
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
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

log.info("Listening on udp %s:%s" % (host, Config['port']))
server.bind((host, Config['port']))
while True:
    (data, addr) = server.recvfrom(128*1024)
    response = bytearray()
    if(data[0] == ord('S')):
        LOG_MSG(" INCOME", addr, data)
        query = SampQuery(data)
        if(query.type == 'i'):
            response = Server.GetServerInfoPacket(data)
        elif(query.type == 'r'):
            response = Server.GetServerRulesPacket(data)
        elif(query.type == 'c'):
            response = Server.GetBasicPlayersPacket(data)
        elif(query.type == 'd'):    
            response = Server.GetDetailedPlayersPacket(data)
        elif(query.type == 'p'):
            response = data
        elif(query.type == 'x'):
            print("  >>> RCON CMD: ", str(data[12:]))
    else:
        if(data[0] == Packet.ID_PING_OPEN_CONNECTIONS):
            LOG_MSG(" INCOME", addr, data)
            response = bytearray([Packet.ID_OPEN_CONNECTION_COOKIE, 0x08, 0xD2])
            #response=bytearray([Packet.ID_OPEN_CONNECTION_COOKIE, random.randint(0,255), random.randint(0,255)])
        else:
            decrypted_data = SampNetEncr.unKyretardizeDatagram(bytearray(data), len(data), Config['port'], 0)
            if(decrypted_data==False):
                continue
            LOG_MSG("+INCOME", addr, decrypted_data)
            if(decrypted_data[0] == Packet.ID_OPEN_CONNECTION_REQUEST):
                response = bytearray([Packet.ID_OPEN_CONNECTION_REPLY, 0x00])
                #response = bytearray([Packet.ID_NO_FREE_INCOMING_CONNECTIONS, 0x00])
                #response = bytearray([Packet.ID_CONNECTION_ATTEMPT_FAILED, 0x00])
                #response = bytearray([Packet.ID_CONNECTION_BANNED, 0x00])
            else:
                re = Reliability(decrypted_data)
                if(re.data[0] == Packet.ID_CONNECTION_REQUEST):
                    response = bytearray([0xE3, 0x00, 0x00])

    
    if(len(response) > 0):
        server.sendto(response,  addr)
        LOG_MSG(" SEND ", addr, response)

            
#"\x1a\xf4\x10" <=> "\xa8\x1e\x1a9"
#"\x1a\xab,"    <=> "\x8a\x1e\xf6\xf4"
#newid=69
#adr =  [int(el) for el in addr[0].split('.')]
#response=[Packet.ID_CONNECTION_REQUEST_ACCEPTED, adr[0],adr[1],adr[2],adr[3], 0xD2,0x04,newid,45,31,48,95]