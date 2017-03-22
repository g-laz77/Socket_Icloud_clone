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
host1 = ""
host2 = ""
s3 = socket.socket()
port3 = 60009
port4 = 60006
host3 = ""
host4 = ""

def cdownload(inp, flag, filename):
    s2 = socket.socket()    
    s2.connect((host2,port2))
    s2.send(inp)
    cont = s2.recv(1024)
    if cont == "folder":
        os.mkdir(filename) 
        file_list = []
        while 1:
            index = s2.recv(1024)
            if index == "END":
                break
            print index
            file_list.append(filename+'/'+index.split()[0])
        s2.close()
        for f in file_list:
            inpu = "download tcp " + f
            cdownload(inpu,"tcp",f)
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
    s2 = socket.socket()    
    s2.connect((host2,port2))
    if inp[1] == "verify":
        s2.send(cl_in)
        hashish = s2.recv(1024)
        if hashish == "no":
            print "File does not exist!"
        else:
            print hashish
    elif inp[1] == "checkall":
        s2.send(cl_in)
        while 1:
            hashish = s2.recv(1024)
            if hashish == "END":
                break
            print hashish

def cindex(inp,cl_in):
    s2 = socket.socket()    
    s2.connect((host2,port2))
    if inp[1] == "shortlist"  or inp[1] == "longlist":
        s2.send(cl_in)
        while 1:
            index = s2.recv(1024)
            if index == "END":
                break
            print index
    elif inp[1] == "regex":
        s2.send(cl_in)
        index = s2.recv(1024)
        print index


def hash_md5(file_name):
    md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(2048), b""):
            md5.update(chunk)
    return md5.hexdigest()

def in_epoch(dat_tim):
    patt = '%a %b %d %H:%M:%S %Y'    
    epoch = int(time.mktime(time.strptime(dat_tim, patt)))
    return float(epoch)

def client():
    while True:
        cl_in = raw_input("client> ")
        inp = cl_in.split(" ")
        if inp[0] == 'download':
            if len(inp) != 3:
                print "Invalid number of args"
                continue
            if (inp[1] == 'tcp' or inp[1] == 'udp'): #and len(inp) == 3:
                cdownload(cl_in,inp[1],inp[2])
            else:
                print "Invalid option"

        elif inp[0] == 'hash':
            if len(inp) < 2:
                print "Invalid number of args"
                continue
            if inp[1] == 'verify' or inp[1] == 'checkall':
                if (len(inp) != 3 and inp[1] == 'verify') or (len(inp) != 2 and inp[1] == 'checkall'):
                    print "Invalid args"
                else:
                    chash(inp,cl_in)
            else:
                print 'Invalid option'
        
        elif inp[0] == "index":
            if len(inp) < 2:
                print "Invalid number of args"
                continue
            if inp[1] == 'shortlist' or inp[1] == 'longlist' or inp[1] == 'regex':
                if ((len(inp) != 3 and inp[1] == 'regex') or (len(inp) != 2 and inp[1] == 'longlist') 
                    or (len(inp) != 4 and inp[1] == 'shortlist')):
                    print "Invalid args"
                else:
                    cindex(inp,cl_in)
            else:
                print 'Invalid option'
        
        else:
            print "Invalid command!"


def sdownload(comm,conn):
    fils = os.listdir(os.getcwd())
    fils2 = []
    for path, subdirs, files in os.walk(os.curdir):
        for name in files:
             fils2.append(os.path.join(path,name)[2:]) 
    if comm[2] in fils:
        
        if os.path.isdir(comm[2]):
            conn.send("folder")
            time.sleep(0.5)
            di = os.getcwd()+'/'+comm[2]
            comm = "index longlist"
            sindex(conn,comm.split(),di)
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
    elif comm[2] in fils2:
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
                conn.send(comm[2]+" folder")
                conn.close()
                return
            mtim = os.path.getmtime(comm[2])
            hashish = hash_md5(comm[2])
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

def sindex(conn,comm,di):
    if comm[1] == "longlist":
        fils = os.listdir(di)
        for f in fils:
            ftim = os.path.getmtime(di+'/'+f)
            if os.path.isdir(di+'/'+f):
                ftyp = "folder"
            else:
                ftyp = magic.from_file(di+'/'+f,mime=True)
            fsiz = os.path.getsize(di+'/'+f)
            conn.send(f+"\t"+repr(fsiz)+"\t"+ftyp+"\t"+time.ctime(ftim))
        time.sleep(1)
        conn.send("END")

    elif comm[1] == "shortlist":
        fils = os.listdir(os.getcwd())
        for f in fils:
            ftim = os.path.getmtime(f)
            if os.path.isdir(f):
                ftyp = "folder"
            else:
                ftyp = magic.from_file(f,mime=True)
            fsiz = os.path.getsize(f)
            print ftim
            if ftim >= in_epoch(comm[2]) and ftim <= in_epoch(comm[3]):
                
                conn.send(f+"\t"+repr(fsiz)+"\t"+ftyp+"\t"+time.ctime(ftim))
        time.sleep(1)
        conn.send("END")
    
    elif comm[1] == "regex":
        stri = str(comm[2])
        files = os.listdir(os.curdir)
        final = ""
        file_cnt = 0
        for f in files:
            if re.search(stri, f):
                mtime = os.path.getmtime(f)
                st = os.stat(f)
                ty = magic.from_file(f)
                st = os.stat(f)
                final = final + f + ' ' + str(st.st_size) + ' ' + time.ctime(mtime) + ' ' + ty + '\n'
                file_cnt += 1
        if file_cnt is 0:
            conn.send('No files are found')
        else:
            conn.send(final)

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
        elif comm[0] == "index":
            sindex(conn,comm,os.getcwd())
            conn.close()

def synfunc():
    s3.bind((host3, port3))
    s3.listen(5)
    while 1:
        conn, addr = s3.accept()
        act = conn.recv(1024)
        action = act.split(" ")
        if action[0] == "hash":
            shash(conn,action)
        elif action[0] == "download":
            sdownload(conn,action)
        elif action[0] == "index":
            sindex(conn,action,os.getcwd())
        conn.close()

def sync():
    while 1:
        fils = os.listdir(os.getcwd())
        for f in fils:
            if os.path.isdir(f):
                continue
            # else:
            has = hash_md5(f)
            s4 = socket.socket()
            s4.connect((host4,port4))
            s4.send("hash verify "+f)
            rec_hash = s4.recv(1024)
            # print f
            # print rec_hash
            if rec_hash == "no":
                continue
            if (not has == rec_hash.split("\t")[0]) and (in_epoch(rec_hash.split("\t")[1]) > os.path.getmtime(f)):
                s4.close()
                print "---------------------"
                print f," not updated"
                cdownload("download tcp "+f, "tcp", f)
                print "---------------------"
                print "client> "   
            else:
                s4.close()
        s4 = socket.socket()
        s4.connect((host4,port4))
        s4.send("index longlist")
        rec_list = []
        while 1:
            tim = s4.recv(1024)
            if tim == "END":
                break
            else:
                rec_list.append(tim.split("\t")[0])
        s4.close()
        for i in rec_list:
            if i not in fils:
                print "---------------------"
                print i," not downloaded"
                cdownload("download tcp "+i,"tcp",i)
                print "---------------------"
                print "client> "
        time.sleep(10)

clnt = threading.Thread(target=client,args=())
clnt.start()
serv = threading.Thread(target=server,args=())
serv.start()
sync1 = threading.Thread(target=sync,args=())
sync2 = threading.Thread(target=synfunc,args=())
sync2.start()
time.sleep(10)
sync1.start()