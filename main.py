import time
import os
from socket import *
from thread import *
import random
theDict={}
my_pid=0
client_counter=1
conn_counter=0
reply_counter=0
polled = False
my_port=0
my_host='localhost'
Queue=[]
numofLikes=0
lamport_clock=0

def config():
    global my_pid
    global my_port
    global client_counter
    print "Configuration "
    my_pid=os.getpid()
    print 'My pid = ',my_pid
    f=open("config","a+")
    line=''
    ip=''
    port=''
    for line in f:
        ip,port=line.strip().split(' ')
        #print ip,port
        client_counter=client_counter+1
    f.close()

    f=open("config","a")
    if line:
        port=str(int(port)+1000)
    else:
        port=str(random.randint(3000,9999))
    my_port=int(port)
    print 'My port = ',my_port
    f.write('127.0.0.1 '+port+'\n')
    f.close()
    return (ip,port)

def read_config():
    #print "read config"
    f=open("config","r")
    global client_counter
    client_counter=0
    line=''
    ip=''
    port=''
    for line in f:
        ip,port=line.strip().split(' ')
        #print ip,port
        client_counter=client_counter+1
    f.close()
    return (ip,port)

def fetch_line(line_num):
    f=open("config","r")
    count=0
    for line in f:
        ip,port=line.strip().split(' ')
        count=count+1
        if (count == int(line_num)):
            break
    return (ip,port)

    
def poll():
    print "Polling"
    global polled
    temp_counter=client_counter
    read_config()
    if temp_counter<client_counter:
        count=client_counter-temp_counter
        for i in range(count):
            ip,port= fetch_line(i+1+temp_counter)
            polled = True
            #print ip,port,"poll "
            tcp_connect(ip,port)
    return
            
def tcp_wait():
    sock = socket(AF_INET,SOCK_STREAM)
    sock.bind((my_host,my_port))
    sock.listen(5)
    global conn_counter
    global theDict
    while True:
        conn, addr = sock.accept()
        theDict[conn_counter]=conn
        #print theDict
        #print conn,addr
        start_new_thread(clientthread,(conn,))
        if (conn):
            conn_counter=conn_counter+1
            break
    return


def clientthread(conn):
    global theDict
    
    conn.send(str(my_port))
    data=conn.recv(1024)
    print 'Connection Established between ',my_port,' & ',data
    #print data
    return
    

	



def tcp_connect(ip,port):
    #print ip,port
    global theDict
    global conn_counter
    sock=socket(AF_INET,SOCK_STREAM)
    sock.connect((ip,int(port)))
    
    data=sock.recv(1024)
    theDict[conn_counter]=sock
    conn_counter=conn_counter+1
    sock.send(str(my_port))
    print 'Connection Established between ',data,' & ',my_port
    return

def tcp_send(msg,socket_num):
    global lamport_clock
    if socket_num=='all':
        for i in range(conn_counter):
            lamport_clock=lamport_clock+1
            theDict[i].send(msg+' '+str(lamport_clock)+' '+str(my_pid))
            print 'Sending ',msg
            print 'Lamport Clock = ',lamport_clock
            
       
    else:
        lamport_clock=lamport_clock+1
        theDict[socket_num].send(msg+' '+str(lamport_clock)+' '+str(my_pid))
        print 'Sending ',msg
        print 'Lamport Clock = ',lamport_clock
    return 

def tcp_recv(flag):
    global reply_counter
    global lamport_clock
    global Queue
    global numofLikes
    while True:
        try:
            for i in range(conn_counter):
                try:
                    theDict[i].settimeout(0)
                    data=theDict[i].recv(200)
                    msg=data.strip().split(' ')
                    if 'request' in data:
                        print 'Got a request from ',msg[2]
                        lamport_clock=max(lamport_clock,int(msg[1]))+1
                        print 'Lamport Clock = ',lamport_clock
                        Queue.append([int(msg[1]),int(msg[2])])
                        Queue.sort()
                        print Queue
                        tcp_send('reply',i)
                    elif 'reply' in data:
                        lamport_clock=max(lamport_clock,int(msg[1]))+1
                        
                        reply_counter=reply_counter+1
                        print 'Got reply from ', msg[2]
                        print 'Lamport Clock = ',lamport_clock
                    elif 'release' in data:
                        lamport_clock=max(lamport_clock,int(msg[1]))+1
                        
                        print 'Removing the head of the queue ',msg[2]
                        print 'Lamport Clock = ',lamport_clock
                        del(Queue[0])
                        Queue.sort()
                        print Queue
                    elif 'Like' in data:
                        lamport_clock=max(lamport_clock,int(msg[1]))+1
                        
                        s,like=msg[0].strip().split(':')
                        numofLikes=numofLikes+int(like)
                        print 'numofLikes = ',numofLikes
                        print 'Lamport Clock = ',lamport_clock
                except:
                    #print 'no data from '+str(theDict[i])
                    pass
        except:
            print "thread error"
            pass


def get_client_counter():
    f=open("config","r")
    count=0
    for line in f:
        count=count+1
    return count



def new_post(flag):
    global reply_counter
    global lamport_clock
    global numofLikes
    global Queue
    while True:
        try:
            print "A new post is available!! Do you want ot read it?(Y/N)"
            response=raw_input()
            if(response=='Y'or response=='y'):
                tcp_send('request','all')
                Queue.append([lamport_clock,my_pid])
                print Queue
                while (reply_counter!=conn_counter):
                    pass
                reply_counter=0
                time.sleep(5)
                while Queue[0][1]!=my_pid:
                    print 'Im not the head , ',Queue[0] , 'is the head'
                print 'Im at the head of the queue'
                f=open("post.txt",'r')
                for line in f:
                    if 'Like' in line:
                        s,numlike=line.strip().split(':')
                        numofLikes=int(numlike)
                        print 'numofLikes = ',numofLikes
                    else:
                        print line
                f.close()
                del (Queue[0])
                print Queue
                tcp_send('release','all')
                while True:
                    print 'Do you want to like the post(Y/N)?'
                    t=raw_input()
                    if(t=='Y'or t=='y'):
                        print 'By how many times?'
                        t=raw_input()
                        if t.isdigit():
                            t=int(t)
                            numofLikes=numofLikes+t
                            print 'numofLikes = ',numofLikes
                            tcp_send('request','all')
                            Queue.append([lamport_clock,my_pid])
                            print Queue
                            while (reply_counter!=conn_counter):
                                pass
                            time.sleep(1)
                            reply_counter=0
                            time.sleep(5)
                            while Queue[0][1]!=my_pid:
                                print 'Im not the head , ',Queue[0] , 'is the head'
                            print 'Im at the head of the queue'
                            f=open("post.txt",'r')
                            lines=f.readlines()
                            f=open('post.txt','w')
                            for line in lines:
                                if 'Like:' in line:
                                    f.write('Like:'+str(numofLikes))
                                else:
                                    f.write(line)
                            del (Queue[0])
                            print Queue
                            tcp_send('release','all')
                            tcp_send(('Like:'+str(t)),'all')
                        else:
                            print 'Invalid number'
        except:
            print 'error in new post'
            pass
        









#MAIN CODE




config()
while True:
    if (client_counter==1):
        poll()
        time.sleep(2+(my_port/10000.0)*3)
    elif polled:
        print "polling done"
        break
    else:
        print "waiting"
        #raw_input()
        #wait for tcp connection
        tcp_wait()
        if conn_counter==client_counter-1:
            break
while True:
    poll()
    time.sleep(2+(my_port/10000.0)*3)
    #print theDict
    if conn_counter==2:
        break
start_new_thread(new_post,(1,))
start_new_thread(tcp_recv,(1,))
#print "this is the post"
while True:
    pass









print "clients = "+str(client_counter)
