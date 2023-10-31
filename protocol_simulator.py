from scapy.all import *
from scapy.utils import rdpcap
from scapy.utils import PcapWriter
import pydivert
import binascii
import time
import signal

def signal_handler(sig, frame):
    print('Pressed Ctrl+C!')
    print("Exiting...")
    w.close()
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

w = pydivert.WinDivert("inbound and tcp.DstPort == 7678")
w.open()

src_mac = "9c:eb:e8:28:d1:6e"
dst_mac = "00:23:a7:2c:ff:2a"
src_ip = "192.168.10.2"
dst_ips = ["192.168.17.64"]
interface = "Ethernet"
IP_id = 0x6470
TCP_seq = 2775400298
IP_TTL = 128
DATA2_RESP_LEN = 75
DATA3_RESP_LEN = 13
DATA4_RESP_LEN = 14
DATA5_RESP_LEN = 12
data1 = "8802070100000f00000000"
data2 = "8802050101000f00000000"
data3 = "88020a0102000f00000000"
data4 = "884207010200000000000100"
data5 = "88450c010300000000000100"
data6 = "884509010400000000001f0078000000780000002c0100002c0100005802000078000000141c04130000"
data7 = "88400c010500000000000700a41a17150517"
data8 = "88401a010600000000000c000000000000000000000000"
data9 = "88400a010700000000000100"
data10 = "884205010800000000000100"

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

data23 = "88450601150000000000090035a03f2000000000"
data24 = "884506011600000000000900fca43f2000000000"
data25 = "884506011700000000000900bca93f2000000000"
data26 = "88450601180000000000090081ae3f2000000000"
data27 = "8845060119000000000009004eb33f2000000000"
data28 = "884506011a000000000009001bb83f2000000000"

data29 = "88400d011b00000000000100"

data30 = "884506011c000000000009004fb93f2000000000"
data31 = "884506011d000000000009005eb93f2000000000"
data32 = "884506011e0000000000090074b93f2000000000"
data33 = "884506011f0000000000090087b93f2000000000"
data34 = "8845060120000000000009009ab93f2000000000"
data35 = "884506012100000000000900afb93f2000000000"
data36 = "884506012200000000000900c3b93f2000000000"
data37 = "884506012300000000000900d7b93f2000000000"
data38 = "884506012400000000000900ebb93f2000000000"
data39 = "884506012500000000000900ffb93f2000000000"

data40 = "884511012600000000000a00040000000032000000"
data41 = "884510012700000000000100"
layer2 = Ether(dst=dst_mac,src=src_mac,type="IPv4")
#pkt = sniff(filter="tcp",iface=interface,count=1)[0]

#pkt1; a SYN packet
pkt = w.recv()

#reply with a SYN-ACK pkt   
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=IP_id,len=44,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=TCP_seq,ack=int(pkt[TCP].seq) + 1, flags=0x012, window=64240,chksum=0x9cb1,options = [('MSS', 1460)])
my_pkt = layer2/layer3/layer4
sendp(my_pkt,iface=interface)


#print("===============================================")
#pkt2
pkt = w.recv()
while(pkt.tcp.rst != False): #response to SYN-ACK is an ACK without RST
    pkt = w.recv()
    
#reply with data1 - a len 11 pkt   
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=IP_id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=TCP_seq+1,ack=int(pkt[TCP].seq), flags=0x018, window=64240,chksum=0x9cb8)
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data1)
sendp(my_pkt,iface=interface)

#pkt3
pkt = w.recv() #response to data1 is a len 13 pkt; It is also the fist message with psh flag set; so we only check this
while(pkt.tcp.psh != True): #first push from device has to be len 13, so need to check
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data1)//2) #because its a rst msg, no need to update my_pkt[TCP].ack
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()
    
#reply with data2 - a len 11 pkt   
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data1)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data2)
sendp(my_pkt,iface=interface)  

#pkt4
pkt = w.recv() #response to data2 is a len 75 pkt
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while(pkt.ipv4.packet_len != (DATA2_RESP_LEN+40)):
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data2)//2) #keep sending data2 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40) #probably the len 13 pkt was retransmitted
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40) #if PSH flag is not set, then Paylod is null, so (pkt.ipv4.packet_len-40) = 0
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

#reply with data3 - a len 11 pkt 
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data2)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data3)
sendp(my_pkt,iface=interface) 

#pkt5
pkt = w.recv() #response to data3 is a len 13 pkt
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while(pkt.ipv4.packet_len != (DATA3_RESP_LEN+40)): 
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data3)//2) #keep sending data3 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40) #probably the len 75 pkt was retransmitted
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

#reply with data4 - a len 12 pkt    
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data3)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data4)
sendp(my_pkt,iface=interface) 

#pkt6
pkt = w.recv() #response to data4 is a len 14 pkt
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while(pkt.ipv4.packet_len != (DATA4_RESP_LEN+40)): #response to data4 is a len 14 pkt
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data4)//2) #keep sending data4 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40) #probably the len 13 pkt was retransmitted
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

#reply with data5 - a len 12 pkt    
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data4)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data5)
sendp(my_pkt,iface=interface)  

#pkt7
pkt = w.recv() #response to data5 is a len 12 pkt - 88450c020300000000000100
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while(pkt.ipv4.packet_len != (DATA5_RESP_LEN+40)): #response to data5 is a len 12 pkt
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data5)//2) #keep sending data5 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40) #probably the len 14 pkt was retransmitted
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

#reply with data6 - a len 42 pkt    
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data5)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data6)
sendp(my_pkt,iface=interface)

#pkt8
pkt = w.recv() #response to data6 is a len 12 pkt - 884509020400000000000100
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while((pkt.tcp.payload) and (pkt.tcp.payload[4]!=4)): #checking for 4; if not 4, probably 88450c020300000000000100 was retransmitted
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data6)//2) #keep sending data6 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40)
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

#reply with data7 - a len 18 pkt    
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data6)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data7)
sendp(my_pkt,iface=interface)

#pkt9
pkt = w.recv() #response to data7 is a len 12 pkt - 88400c020500000000000100
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while((pkt.tcp.payload) and (pkt.tcp.payload[4]!=5)): #checking for 5; if not 5, probably 884509020400000000000100 was retransmitted
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data7)//2) #keep sending data7 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40)
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()
    
#reply with data8 - a len 23 pkt    
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data7)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data8)
sendp(my_pkt,iface=interface)

#pkt10
pkt = w.recv() #response to data8 is a len 12 pkt - 88401a020600000000000100
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while((pkt.tcp.payload) and (pkt.tcp.payload[4]!=6)): #checking for 6; if not 6, probably 88400c020500000000000100 was retransmitted
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data8)//2) #keep sending data8 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40)
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

#reply with data9 - a len 12 pkt    
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data8)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data9)
sendp(my_pkt,iface=interface)

#pkt11
pkt = w.recv() #response to data9 is a len 20 pkt - 88400a0207000000000009000600000000000000
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while((pkt.tcp.payload) and (pkt.tcp.payload[4]!=7)): #checking for 7; if not 7, probably 88401a020600000000000100 was retransmitted
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data9)//2) #keep sending data9 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40)
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

#reply with data10 - a len 12 pkt    
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data9)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data10)
sendp(my_pkt,iface=interface)

#pkt12
pkt = w.recv() #response to data10 is a len 76 pkt 
while(pkt.tcp.payload == b''):
    pkt = w.recv()
while((pkt.tcp.payload) and (pkt.tcp.payload[4]!=8)): #checking for 8; if not 8, probably 88400a0207000000000009000600000000000000 was retransmitted
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data10)//2) #keep sending data10 until the response is received
    my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40)
    my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()

prev_data =  data10 
PAYLOAD_CHECKER = 8  
#reply with data11-data41    
for data_var_num in range(11,42):
    data_var = "data" + str(data_var_num)
    data = globals()[data_var]
    pkt = IP(pkt.raw.tobytes())
    layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
    layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(prev_data)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
    my_pkt = layer2/layer3/layer4/binascii.unhexlify(data)
    sendp(my_pkt,iface=interface)
    prev_data = data
    
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        pkt = w.recv()
    PAYLOAD_CHECKER = PAYLOAD_CHECKER+1
    print(PAYLOAD_CHECKER)
    print(pkt.tcp.payload)
    print(binascii.hexlify(pkt.tcp.payload))
    while((pkt.tcp.payload) and (pkt.tcp.payload[4]!=PAYLOAD_CHECKER)): 
        my_pkt[IP].id = my_pkt[IP].id + 1
        my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data)//2) #keep sending data10 until the response is received
        my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40)
        my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
        sendp(my_pkt,iface=interface)
        pkt = w.recv()
        while(pkt.tcp.payload == b''):
            pkt = w.recv()
        print(binascii.hexlify(pkt.tcp.payload))
        
data42 = "88450601280000000000090030ba3f2000000000"
pkt = IP(pkt.raw.tobytes())
layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(prev_data)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
my_pkt = layer2/layer3/layer4/binascii.unhexlify(data42)
sendp(my_pkt,iface=interface)
print("============================================================")
print("in while")
i = 0
while(1):
    i = i+1
    print(i)
    pkt = w.recv()
    while(pkt.tcp.payload == b''):
        #my_pkt[IP].id = my_pkt[IP].id + 1
        #my_pkt[TCP].seq = my_pkt[TCP].seq+(len(data42)//2)
        #sendp(my_pkt,iface=interface)
        pkt = w.recv()
    print(pkt.tcp.payload)
    print(binascii.hexlify(pkt.tcp.payload))
    pkt = IP(pkt.raw.tobytes())
    data42 = data42[:8] + "0x{:02x}".format(int(data42[8:10],16)+1)[-2:] + data42[10:]
    print(data42)
    print(data42[8:10])
    if(my_pkt[TCP].window <= 2*(pkt[IP].len-40)):
        my_pkt[TCP].window = 65535
    if(my_pkt[IP].id == 65535):
        my_pkt[IP].id = 0
    if(my_pkt[TCP].seq+(len(data42)//2) > 4294967296):
        my_pkt[TCP].seq = (my_pkt[TCP].seq - 4294967296) #reducing here so that in layer4 it is wrapped around
    if(int(pkt[TCP].seq)+(pkt[IP].len-40) > 4294967296):
        pkt[TCP].seq = (int(pkt[TCP].seq) - 4294967296) #reducing here so that in layer4 it is wrapped around
    layer3 = IP(src=src_ip,dst=pkt[IP].src,id=my_pkt[IP].id+1,ttl=IP_TTL,proto="tcp",flags=2,chksum=0)
    layer4 = TCP(sport=pkt[TCP].dport,dport=pkt[TCP].sport, seq=my_pkt[TCP].seq+(len(data42)//2),ack=int(pkt[TCP].seq)+(pkt[IP].len-40), flags=0x018, window=my_pkt[TCP].window-(pkt[IP].len-40))
    my_pkt = layer2/layer3/layer4/binascii.unhexlify(data42)
    sendp(my_pkt,iface=interface)

    

'''
while((pkt.tcp.psh != True) and (pkt.ipv4.packet_len != (12+40))): #response to data6 is a len 12 pkt
    my_pkt[IP].id = my_pkt[IP].id + 1
    my_pkt[TCP].seq = my_pkt[TCP].seq+12 #keep sending data5 until the response is received
    if((pkt.tcp.psh == True) and (pkt.ipv4.packet_len != (12+40))): #say, we get the same len 14 pkt again
        my_pkt[TCP].window = my_pkt[TCP].window - (pkt.ipv4.packet_len-40) #probably the len 14 pkt was retransmitted
        my_pkt[TCP].ack = pkt.tcp.seq_num+(pkt.ipv4.packet_len-40)
    sendp(my_pkt,iface=interface)
    pkt = w.recv()  
'''

'''    
print(hexdump(my_pkt))
a = my_pkt.show(dump=True)
print(a)
    
'''

w.close()

'''
while(1):
    pkt = w.recv()
'''
