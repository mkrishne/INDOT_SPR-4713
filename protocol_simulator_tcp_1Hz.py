import socketserver
import signal
import sys
import binascii 
import time
import socket
import base64
    
data1 = "8802070100000f00000000"
data2 = "8802050101000f00000000"
data3 = "88420a0102000f00000000"
data4 = "884207010200000000000100"
data5 = "88450c010300000000000100"
data6 = "884509010400000000001f0078000000780000002c0100002c0100005802000078000000141c04130000"       
data7 = "88400c01050000000000070035081811130d"        
data8 = "88401a010600000000000c000000000000000000000000"        
data9 = "88400a010700000000000100"        
data10 = "884205010800000000000100" #marked
          
data11 = "884105010900010000000400010000"         
data12 = "884022010a00000000000600000000a040"         
data13 = "884020010b00000000000100"        
data14 = "884105010c00020000000400020000"        
data15 = "884022010d00000000000600010000a040"       
data16 = "884020010e00000000000100"        
data17 = "884105010f00040000000400040000"       
data18 = "884022011000000000000600020000a040"       
data19 = "884020011100000000000100"       
data20 = "884105011200080000000400080000" 
      
data21 = "884022011300000000000600030000a040"       
data22 = "884020011400000000000100"
data23 = "8845060115000000000009002c66300b00000000"          
data24 = "884506011600000000000900ed6a300b00000000"          
data25 = "8845060117000000000009003570300b00000000"         
data26 = "8845060118000000000009000d75300b00000000"         
data27 = "884506011900000000000900d379300b00000000"         
data28 = "884506011a000000000009009c7e300b00000000"         
data29 = "88400d011b00000000000100"         
data30 = "884506011c00000000000900617f300b00000000"
            
data31 = "884506011d00000000000900747f300b00000000"        
data32 = "884506011e00000000000900897f300b00000000"       
data33 = "884506011f000000000009009c7f300b00000000"      
data34 = "884506012000000000000900af7f300b00000000"      
data35 = "884506012100000000000900c37f300b00000000"      
data36 = "884506012200000000000900d77f300b00000000"      
data37 = "884506012300000000000900eb7f300b00000000"     
data38 = "884506012400000000000900ff7f300b00000000"    
data39 = "8845060125000000000009001380300b00000000"      
data40 = "884511012600000000000a00040000000032000000"
data41 = "884510012700000000000100"
          
#dummy 20 byte send
data42 = "8845060128000000000009004580300b00000000"
data43 = "8845060129000000000009005580300b00000000"   
data44 = "884506012a000000000009006480300b00000000"
data45 = "884506016900000000000900ac88300b00000000"
data46 = "884506016a00000000000900798d300b00000000"
data47 = "884506016b000000000009004492300b00000000"

sample_start1 = "884404017c00000000000100"
                 

sample_start2 = "884014017d00000000000100"
                 

sample_start3 = "884018017e00000000000100"
                 

sample_start4 = "884024017f00000000000500d0070000"
                 

sample_start5 = "884015018000000000000100"
                 

sample_start6 = "8840260181000000000005000000803f"
                 

sample_start7 = "88410401820000000000050028000000"
                 

sample_start8 = "884402018300000000000100"
                 

sample_start9 = "884403018400000000000900f512261100000000"
                 

sample_start10 = "884506018500000000000900f50f261100000000"
                  

sample_start11 = "884506018600000000000900c014261100000000"
                  

sample_start12 = "88400001870000000000110000000000000000000000000000000000"
                  
sample_start13 = "88401701880000000000050088130000"     
                  

#dummy 14 byte send
sample_start14 = "884506018900000000000900e91b261100000000"

sample_stop1 = "884014018e000f0000000100"
sample_stop2 = "884018018f00000000000100"
sample_stop3 = "884404019000000000000100"

data_for_conn_alive = "88450601280000000000090030ba3f2000000000"
data_num = 1

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global data_num
        while (data_num < 48):
            try:
                send_data = eval("data" + str(data_num))
                print(f"Sending init data {data_num} : {send_data}")
                self.request.sendall(binascii.unhexlify(send_data))
                self.request.settimeout(0.5)
                recv_data = self.request.recv(2048) # buffer size is 1024 bytes 
                recv_data_b64 = base64.b64encode(recv_data)
                print(f"Received data: {base64.b64decode(recv_data_b64).hex()}")
                #print("Received from {}:".format(self.client_address[0]))
                data_num = data_num+1
            except socket.timeout:
                print("Timeout waiting for response")
        
        print()
        data_num = 1
        time.sleep(1)
        while (data_num < 5):
            try:
                self.request.sendall(binascii.unhexlify(data_for_conn_alive))
                print("data_for_conn_alive sent")
                self.request.settimeout(0.5)
                recv_data = self.request.recv(2048) # buffer size is 1024 bytes 
                recv_data_b64 = base64.b64encode(recv_data)
                print(f"Received data: {base64.b64decode(recv_data_b64).hex()}")
                #print("Received from {}:".format(self.client_address[0]))
                time.sleep(0.5)
                data_num = data_num + 1
            except socket.timeout:
                print("Timeout waiting for response")
                
        data_num = 1 #resetting to send the sample start commands
        while (data_num < 15):
            try:
                send_data = eval("sample_start" + str(data_num))
                print(f"Sending sample start data{data_num} : {send_data}")
                self.request.sendall(binascii.unhexlify(send_data))
                self.request.settimeout(0.5)
                recv_data = self.request.recv(2048) # buffer size is 1024 bytes 
                recv_data_b64 = base64.b64encode(recv_data)
                hex_stream = base64.b64decode(recv_data_b64).hex()
                print(f"Received data: {hex_stream}")
                if(data_num == 8):
                    time.sleep(1.1)
                if(data_num == 9):
                    time.sleep(0.2)
                if(data_num == 10):
                    time.sleep(1.3)
                if(data_num == 11):
                    time.sleep(0.6)
                if(data_num == 12):
                    time.sleep(0.5)
                if(data_num == 12):
                    time.sleep(1.2)
                #print("Received from {}:".format(self.client_address[0]))
                #print()
                data_num = data_num+1
            except socket.timeout:
                print("Timeout waiting for response")
                
        print()
        recv_pkt_num = 1
        while (recv_pkt_num < 10):
            try:
                self.request.settimeout(2)
                recv_data = self.request.recv(2048) # buffer size is 1024 bytes 
                if(len(recv_data) != 28):
                    recv_data_b64 = base64.b64encode(recv_data)
                    print(f"Received data {recv_pkt_num} {len(recv_data)}: {base64.b64decode(recv_data_b64).hex()}")
                    recv_pkt_num = recv_pkt_num +1
                    #print("Received from {}:".format(self.client_address[0]))
            except socket.timeout:
                print("Timeout waiting for response")
                self.request.sendall(binascii.unhexlify(data_for_conn_alive))
                print("data_for_conn_alive sent")
        
        print()       
        data_num = 1 #resetting to send the sample stop commands
        while (data_num < 4):
            try:
                send_data = eval("sample_stop" + str(data_num))
                print(f"Sending STOP data {data_num}: {send_data}")
                self.request.sendall(binascii.unhexlify(send_data))
                self.request.settimeout(0.5)
                recv_data = self.request.recv(2048) # buffer size is 1024 bytes 
                recv_data_b64 = base64.b64encode(recv_data)
                print(f"Received data: {base64.b64decode(recv_data_b64).hex()}")
                #print("Received from {}:".format(self.client_address[0]))
                data_num = data_num + 1
            except socket.timeout:
                print("Timeout waiting for response")
        while True:
            try:
                self.request.sendall(binascii.unhexlify(data_for_conn_alive))
                print("data_for_conn_alive sent")
                self.request.settimeout(0.5)
                recv_data = self.request.recv(2048) # buffer size is 1024 bytes 
                recv_data_b64 = base64.b64encode(recv_data)
                print(f"Received data: {base64.b64decode(recv_data_b64).hex()}")
                #print("Received from {}:".format(self.client_address[0]))
            except socket.timeout:
                print("Timeout waiting for response")
            
if __name__ == "__main__":
    TCP_PORT = 7678
    INTERFACE = "192.168.10.2"  # Public IP Address of the system
    print('Press Ctrl+C to exit')
    with socketserver.ThreadingTCPServer((INTERFACE, TCP_PORT), MyTCPHandler) as server:
        server.serve_forever()