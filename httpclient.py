#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, Xuping Fang, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def get_host_port(self,url):
        return [socket.gethostbyname(url.split("://")[-1].split("/")[0]),80]

    def connect(self, host, port):
        # use sockets!
        if port==None:
            port=80
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((host,port))
        return sock

    def get_code(self, data):
        return int(data.split(" ")[1])

    def get_headers(self, data):
        return data.split("\r\n\r\n",1)[0]

    def get_body(self, data):
        return data.split("\r\n\r\n",1)[1]
    
    def parse_url(self,url,component):
        o=urlparse.urlparse(url)
        if(component=="port"):
            return o.port
        if(component=="path"):
            return o.path
        if(component=="hostname"):
            return o.hostname
    
    def construct_request(self,method,url,args):
        if args==None:
            encode_args=""
        else:
            encode_args=urllib.urlencode(args)        
        
        if method=="GET":
            return "GET "+self.parse_url(url,"path")+" HTTP/1.1\r\nHost: "+self.parse_url(url,"hostname")+"\r\n\r\n"
        elif method=="POST":
            return "POST "+self.parse_url(url,"path")+" HTTP/1.1\r\nHost: "+self.parse_url(url,"hostname")+"\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "+str(len(encode_args))+"\r\n\r\n"+encode_args+"\r\n"

    # read everything from the socket
    def recvall(self,sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)
    
    def HTTP_method(self,method,url,args=None):
        request = self.construct_request(method,url,args)
        
        sock=self.connect(self.parse_url(url,"hostname"),self.parse_url(url,"port"))
        sock.sendall(request)      
        response=self.recvall(sock)
        
        sock.close()      
        code=self.get_code(response)
        try:
            body=self.get_body(response)
        except IndexError:
            body=""
                
        return HTTPResponse(code,body)        

    def GET(self,url,args=None):
        return self.HTTP_method("GET",url,args)

    def POST(self,url,args=None):
        return self.HTTP_method("POST",url,args)

    def command(self,url,command="GET",args=None):
        if (command == "POST"):
            return self.POST(url,args)
        else:
            return self.GET(url,args)
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command(sys.argv[2],sys.argv[1] )
    else:
        print client.command(sys.argv[1])   
