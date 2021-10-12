import socket
import json
from flask import abort

UDP_IP = "172.18.0.4"
UDP_PORT = 53533
FILE = "registry.json"

sock = socket.socket(socket.AF_INET, # Internet
                socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

def getDictionary(data):
    res = {}
    line = data.split("\n")
    for l in line:
        #print("line: ",l)
        key = l.split("=")[0]
        val = l.split("=")[1]
        res[key] = val
    return res

def updateEntry(data):
    try:
        with open(FILE) as f:
            reg_data = json.load(f)
    except Exception as e:
        print("REG file not found!!!!!!!!!!!!!")
        reg_data = {}

    if(str(data['NAME']) in reg_data): #update Entry
        reg_data[str(data['NAME'])]["TYPE"] =str(data['TYPE'])
        reg_data[str(data['NAME'])]["VALUE"] = str(data['VALUE'])
        reg_data[str(data['NAME'])]["TTL"] = int(data['TTL'])
    else:   # Create Entry
        temp = {}
        temp["TYPE"] =str(data['TYPE'])
        temp["VALUE"] = str(data['VALUE'])
        temp["TTL"] = int(data['TTL'])
        reg_data[str(data['NAME'])] = temp

    print("DATA: ",reg_data)
    try:
        with open(FILE, "w+") as f:
            json.dump(reg_data, f)
        print("REGISTERED SUCCESSFULLY!")
    except Exception as e:
        print("Error while registering hostname.")

def getResultFromQuery(data):
    try:
        with open(FILE) as f:
            entry = json.load(f)
    except Exception as e:
        print("Unable to open Register Entry file!")
        abort(400)
    
    hostname = ""
    query = data.split("\n")
    for q in query:
        key = q.split("=")[0]
        if(key == "NAME"):
            hostname = q.split("=")[1]
            break
    if(hostname in entry):
        response = {}
        response['NAME'] = hostname
        response['TYPE'] = entry[hostname]['TYPE']
        response['VALUE'] = entry[hostname]['VALUE']
        response['TTL'] = entry[hostname]['TTL']
        return response
    else:
        print("hostname not found in registry.")
        return {}
    
while True:
    print("LISTENING ON PORT",UDP_IP,UDP_PORT)
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message:" , data)
    data = data.decode('utf-8')
    if(data[0]=='#'):   #DNS query
        print("DNS QUERY : ")
        result = getResultFromQuery(data[1:])
        print("RESULT : ",result)
        sock.sendto(json.dumps(result).encode(),addr)
    else:
        dataDict = getDictionary(data)
        updateEntry(dataDict)
        print("Entry created/updated!!!")
        sock.sendto(str.encode("success:201"),addr)

