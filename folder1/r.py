import socket
import threading
import hashlib
import os
import time
import magic
import re

port1 = 60008
port2 = 60005
s1 = socket.socket()
s2 = socket.socket()
host1 = ""
host2 = ""

def cdownload(inp, flag, filename):
    s2 = socket.socket()    
    s2.connect((host2,port2))
    s2.send(inp)
    cont = s2.recv(1024)
    if cont == "folder":
        os.mkdir(filename) 
        print "Folder created.."
        return
    fl = 1
    with open(filename, 'w+') as f:
        fl = 0
        while True:

            if cont == "No":
                print "File does not exist!"
                fl = 1
                break
            if cont != "End":
                f.write(cont)
                cont = s2.recv(1024)
                print('receiving data...')
            else:
                break
            
        f.close()
        if not fl:
            perm = s2.recv(1024)
            os.chmod(os.getcwd()+'/'+filename,int(perm))
            prnt = s2.recv(1024)
            print prnt
        else:
            os.remove(filename)
    s2.close()

def chash(inp,cl_in):
    if comm[1] == "verify":
        s2.send(cl_in)
        hashish = s2.recv(1024)
        if has == "no":
            print "File does not exist!"
        else:
            print hashish
    elif comm[1] == "checkall":
        s2.send(cl_in)
        while 1:
            hashish = s2.recv(1024)
            if hashish == "END":
                break
            print hashish

def hash_md5(file_name):
    md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(2048), b""):
            md5.update(chunk)
    return md5.hexdigest()

def client():
    while True:
        cl_in = raw_input("client> ")
        inp = cl_in.split(" ")
        if inp[0] == 'download':
            if len(inp) != 3:
                print "invalid number of args"
                continue
            if (inp[1] == 'tcp' or inp[1] == 'udp'): #and len(inp) == 3:
                cdownload(cl_in,inp[1],inp[2])
            else:
                print "invalid option"

        elif inp[0] == 'hash':
            if len(inp) < 2:
                print "invalid number of args"
                continue
            if inp[1] == 'verify' or inp[1] == 'checkall':
                if (len(inp) != 3 and inp[1] == 'verify') or (len(inp) != 2 and inp[1] == 'checkall'):
                    print "invalid args"
                else:
                    chash(inp,cl_in)
            else:
                print 'invalid option'

def sdownload(comm,conn):
    fils = os.listdir(os.getcwd())
    if comm[2] in fils:
        
        if os.path.isdir(comm[2]):
            conn.send("folder")
            conn.close()
            return

        f = open(comm[2],'rb')
        l = f.read(1024)

        while (l):
            conn.send(l)
            l = f.read(1024)

        time.sleep(0.5)
        conn.send("End")
        time.sleep(0.5)
        perm = oct(os.stat(comm[2]).st_mode)[-4:]
        conn.send(perm)
        f.close()
        time.sleep(0.5)
        print('Done sending')
        conn.send(comm[2]+"\t"+repr(os.path.getsize(comm[2]))+"\t"+hash_md5(comm[2]))
    else:
        conn.send("No")

def shash(conn,comm):
    if comm[1] == "verify":
        if comm[2] in os.listdir(os.getcwd()):
            if os.path.isdir(comm[2]):
                conn.send(comm[1]+" : folder")
                conn.close()
                return
            mtim = os.path.getmtime(comm[2])
            hashish = md5(action[2])
            conn.send(hashish+"\t"+time.ctime(mtim))
        else:
            conn.send("no")
        conn.close()
    elif comm[1] == "checkall":
        fils = os.listdir(os.getcwd())
        for f in fils:
            if os.path.isdir(f):
                conn.send(f+" is a folder")
                continue 
            mtim = os.path.getmtime(f)
            hashish = hash_md5(f)
            conn.send(f+"\t"+hashish+"\t"+time.ctime(mtim))
        time.sleep(0.5)
        conn.send("END")

def server():
    s1.bind((host1, port1))
    s1.listen(5)
    print 'Server listening....'
    flag = 0
    while 1:
        conn, addr = s1.accept()
        print 
        print 'Got connection from', addr
        com = conn.recv(1024)
        comm = com.split()
        print comm
        if comm[0] == "download": 
            sdownload(comm,conn)
            conn.close()
        elif comm[0] == "hash":
            shash(conn,comm)
            conn.close()


clnt = threading.Thread(target=client,args=())
serv = threading.Thread(target=server,args=())
clnt.start()
serv.start()