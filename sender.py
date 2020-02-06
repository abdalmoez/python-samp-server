import socket
import sys
import threading





#UDP_IP = "80.211.132.171"#0.3.DL
UDP_IP = "194.5.159.52"#0.3.7
UDP_PORT = 7777

#UDP_IP = "127.0.0.1"
#UDP_PORT = 1234
#MESSAGE = b"SAMP\x7f\x00\x00\x01\xd2\x04i"#Information from GUI
MESSAGE = b'\x08\x1e\xc4\xda'#OnPlayerConnect

print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("Message:", MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(b'\x08\x1e\xc4\xda', (UDP_IP, UDP_PORT))
(data, addr) = sock.recvfrom(1024) # buffer size is 1024 bytes
print ("Received message:", data)




'''
b"SAMP\x7f\x00\x00\x01\xd2\x04i"
[83, 65, 77, 80, 127, 0, 0, 1, 210, 4, 105]
b'SAMP\x7f\x00\x00\x01\xd2\x04i\x00\x00\x00d\x00\x17\x00\x00\x00Exodus Roleplay [0.3.7]\r\x00\x00\x00EX:RP v2.1.10\x07\x00\x00\x00English'
[83, 65, 77, 80, 127, 0, 0, 1, 210, 4, 105, 0, 0, 0, 100, 0, 23, 0, 0, 0, 69, 120, 111, 100, 117, 115, 32, 82, 111, 108, 101, 112, 108, 97, 121, 32, 91, 48, 46, 51, 46, 55, 93, 13, 0, 0, 0, 69, 88, 58, 82, 80, 32, 118, 50, 46, 49, 46, 49, 48, 7, 0, 0, 0, 69, 110, 103, 108, 105, 115, 104]
b'SAMP\x7f\x00\x00\x01\xd2\x04i\x01\x00\x00\x9d\x00 \x00\x00\x00[! 0.3.DL !] West Side Role Play\x16\x00\x00\x00Roleplay | WSRP v3.1.1\x07\x00\x00\x00English'
[83, 65, 77, 80, 127, 0, 0, 1, 210, 4, 105, 1, 0, 0, 157, 0, 32, 0, 0, 0, 91, 33, 32, 48, 46, 51, 46, 68, 76, 32, 33, 93, 32, 87, 101, 115, 116, 32, 83, 105, 100, 101, 32, 82, 111, 108, 101, 32, 80, 108, 97, 121, 22, 0, 0, 0, 82, 111, 108, 101, 112, 108, 97, 121, 32, 124, 32, 87, 83, 82, 80, 32, 118, 51, 46, 49, 46, 49, 7, 0, 0, 0, 69, 110, 103, 108, 105, 115, 104]
'''