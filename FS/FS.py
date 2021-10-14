from flask import Flask,request,abort
import requests
import json
import socket 
app = Flask(__name__)

#curl --request PUT http://localhost:9090/register --header "Content-Type:application/json" --data '{"hostname":"fibonacci.com","ip":"0.0.0.0","as_ip":"0.0.0.0","as_port":"53533"}'
# curl --request PUT http://0.0.0.0:9090/register --header "Content-Type:application/json" --data '{"hostname":"fibonacci.com","ip":"172.18.0.3","as_ip":"172.18.0.4","as_port":"53533"}'
tempDict = {
    "hostname" : "",
    "ip" : "",
    "as_ip" : "",
    "as_port" : ""
}

def getFibonacciKeyFromSequence(n):
    prev, cur = 0, 1
    for i in range(n):
        temp = prev
        prev, cur = cur, temp + cur    
    return cur

@app.route('/fibonacci')
def index():
    queryNum = request.args['number']
    sequenceRes = getFibonacciKeyFromSequence(queryNum)
    queryFromUserBrowser = 'Fibonacci '+str(queryNum)
    return {queryFromUserBrowser:sequenceRes}


@app.route('/register', methods = ['PUT','GET'])
def register():
    if request.method == 'PUT' or request.method == 'GET':
        try:
            print("request: ",request.data)
            data = json.loads(request.data.decode('utf-8'))
            print("data: ",data)
            tempDict['hostname'] = str(data['hostname'])
            tempDict['ip'] = str(data['ip'])
            tempDict['as_ip'] = str(data['as_ip'])
            tempDict['as_port'] = str(data['as_port'])
            print("dict: ",tempDict)
        except Exception as e:
            abort(400)
    response = registerOnAuthoritativeServer()
    print(response[0])
    return str(response[0])

def registerOnAuthoritativeServer():
    print("IN registerOn")
    bufferSize = 1024
    as_ip = tempDict['as_ip']
    as_port = tempDict['as_port']
    server = (as_ip,int(as_port))
    print("SERVER address: ",server)
    fs_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    message = generateMessage()
    print("message to server: ",message)
    fs_socket.sendto(str.encode(message), server)
    response = fs_socket.recvfrom(bufferSize)
    print("RESPONSE FROM SERVER: ",response[0])
    return response[0]

def generateMessage():
    message = ""
    message = "TYPE=A\nNAME="+tempDict['hostname']+"\nVALUE="+tempDict['ip']+"\nTTL=10"
    print("MESSAGE: ",message)
    return message

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port='9090')