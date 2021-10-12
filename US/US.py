from flask import Flask,request,abort
import requests
import json
import socket

app = Flask (__name__)

#For localhost 
# http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=0.0.0.0&as_port=53533

#For Docker 
# http://localhost:8080/fibonacci?hostname=fibonacci.com&fs_port=9090&number=10&as_ip=as&as_port=53533

#status codes
BAD_REQUEST = 400
OK = 200
#####
BUFFER_SIZE = 1024

def validateParams(host,f_port,num,a_ip,a_port):
    if(host == '' or f_port == '' or num == '' or a_ip == '' or a_port == ''):
        return (False,BAD_REQUEST)
    return (True,OK)

def getFibonacciQueryUrl(ip,num):
    url = 'http://'+ip+':9090/fibonacci?number='+num
    return url

def getDnsQueryMessage(hostname):
    TYPE = "A"
    query =  str("#TYPE="+TYPE+"\nNAME="+hostname)
    return query


def queryIpFromAuthoritativeServer(hostname,as_ip,as_port):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    dnsquery = getDnsQueryMessage(hostname)
    server = (as_ip,int(as_port))
    # print("&&&&&&& :",dnsquery)
    sock.sendto(str.encode(dnsquery),server)
    response = sock.recvfrom(BUFFER_SIZE)
    response = json.loads(response[0].decode())
    return response


@app.route('/fibonacci')
def index():
    hostname = request.args['hostname']
    fs_port = request.args['fs_port']
    number = request.args['number']
    as_ip = request.args['as_ip']
    as_port = request.args['as_port']
    (isValid,code) = validateParams(hostname,fs_port,number,as_ip,as_port)
    if(code == BAD_REQUEST):
        abort(400)
    
    #Query AServer for IP address of hostname
    query_dict = {'TYPE':'A','NAME':hostname}
    response = queryIpFromAuthoritativeServer(hostname,as_ip,as_port)
    print("RESPONSE from server: ",response)
    
    #Send reqeust to Fibonacci server with number parameter
    #res_dict has IP address of fibonacci server, returned by Authoritative Server
    fib_ip = response['VALUE']
    fib_query_url = getFibonacciQueryUrl(fib_ip,number)
    result = requests.get(fib_query_url)
    # print("**************************",result.text)
    return result.text
    

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port='8080')

