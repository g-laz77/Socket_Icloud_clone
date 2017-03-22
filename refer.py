import socket
import threading
import hashlib
import os
import time
import magic
import re

port1 = 60005
port2 = 60008
port3 = 60006
port4 = 60009
s1 = socket.socket()
s2 = socket.socket()
s3 = socket.socket()
host1 = ""
host2 = ""
host3 = ""
host4 = ""

def in_epoch(date_time):
    pattern = '%a %b %d %H:%M:%S %Y'    
    epoch = int(time.mktime(time.strptime(date_time, pattern)))
    return float(epoch)

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync():
    while 1:
        #print "SYNC in progress!"
        fils = os.listdir(os.getcwd())
        for f in fils:
            if os.path.isdir(f):
                 continue
            has = md5(f)
            s4 = socket.socket()
            st = 0
            while not st:
                try:
                    s4.connect((host4,port4))
                except:
                    continue
                st = 1
            #print st
            s4.send("hash verify "+f)
            rec_hash = s4.recv(1024)
            if (not has == rec_hash.split("\t")[0]) and (in_epoch(rec_hash.split("\t")[1]) > os.path.getmtime(f)):
                s4.close()
                print "---------------------"
                print f," not updated"
                s5 = socket.socket()
                s5.connect((host4,port4))
                s5.send("download "+f)
                with open(f,'w+') as f:
                    while 1:
                        data = s5.recv(1024)
                        if data != "End":
                            print "Recieveing Data..."
                        else:
                            break
                        f.write(data)
                    f.close()
                    data = s5.recv(1024)
                print "---------------------"
                print "prompt> "

            else:
                #print f," is synced!"
                s4.close()
        s4 = socket.socket()
        s4.connect((host4,port4))
        s4.send("index longlist")
        rec_list = []
        #rec_list.append(s4.recv(1024).split("\t")[0])
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
                s5 = socket.socket()
                s5.connect((host2,port2))
                s5.send("download "+i)
                data = s5.recv(1024)
                if data == "folder":
                    try: 
                        os.stat(i)
                    except:
                        os.mkdir(i) 
                    print "folder created"
                    continue
                with open(i,'w+') as f:
                    while 1:
                        if data != "End":
                            f.write(data)
                            data = s5.recv(1024)
                            print "Recieveing Data..."
                        else:  
                            break
                        
                    f.close()
                    perm = s5.recv(1024)
                    os.chmod(os.getcwd()+'/'+comm[1],int(perm))
                    data = s5.recv(1024)
                print "---------------------"
                print "prompt> "
        time.sleep(10)


def client():
    ft = 0
    while True:
        #sync()
        com = raw_input("prompt> ")
        comm = com.split()
        if len(comm) == 1 and comm != "exit":
            print "invalid number of args!"
            continue
        #print comm[0]
        s2 = socket.socket()
        if comm[0] == "download":
            s2.connect((host2,port2))
            if len(comm) > 3:
                print "inavlid number of args!"
                s2.close()
                continue
            
            s2.send(com)
            data = s2.recv(1024)
            if data == "folder":
                try: 
                    os.stat(comm[1])
                except:
                    os.mkdir(comm[1]) 
                print "folder created"
                continue
            flag = 1
            with open(comm[1], 'w+') as f:
                print 'file opened'
                flag = 0
                while True:
                    
                    if data == "imaginary!":
                        print "File does not exist!"
                        flag = 1
                        break
                    if data != "End":
                        f.write(data)
                        data = s2.recv(1024)
                        print('receiving data...')
                    else:
                        break
                    
                f.close()

                if not flag:
                    perm = s2.recv(1024)
                    os.chmod(os.getcwd()+'/'+comm[1],int(perm))
                    data = s2.recv(1024)
                    print data
                else:
                    os.remove(f)
            s2.close()
            
        elif comm[0] == "hash":
            s2.connect((host2,port2))
            if comm[1] == "verify":
                if len(comm) > 3:
                    print "invalid number of args!"
                    s2.close()
                    continue
                s2.send(com)
                has = s2.recv(1024)
                if has == "imaginary!":
                    print "File does not exist!"
                else:
                    print has
            elif comm[1] == "checkall":
                if len(comm) > 2:
                    print "invalid number of args!"
                    s2.close()
                    continue
                s2.send(com)
                while 1:
                    tim = s2.recv(1024)
                    if tim == "END":
                        break
                    print tim
            s2.close()
            #s2 = socket.socket()

        elif comm[0] == "index":
            s2.connect((host2,port2))
            if comm[1] == "longlist":
                if len(comm) > 2:
                    print "invalid number of args!"
                    s2.close()
                    continue
                s2.send(com)
                while 1:
                    tim = s2.recv(1024)
                    if tim == "END":
                        break
                    print tim    
            elif comm[1] == "shortlist":
                if len(comm) > 4:
                    print "invalid number of args!"
                    s2.close()
                    continue
                s2.send(com)
                while 1:
                    tim = s2.recv(1024)
                    if tim == "END":
                        break
                    print tim
            elif comm[1] == "regex":
                if len(comm) > 3:
                    print "invalid number of args!"
                    s2.close()
                    continue
                s2.send(com)
                #while 1:
                tim = s2.recv(1024)
                print tim
            elif comm[1]:
                s2.connect((host2,port2))
                print "invalid flag!"
            s2.close()
            #s2 = socket.socket()

        elif comm[0] == "exit":
            s2.close()
            s1.close()
            exit(0)

def synfunc():
    s3.bind((host3, port3))
    s3.listen(5)
    while 1:
        conn, addr = s3.accept()
        #print 
        #print 'Got connection from', addr
        act = conn.recv(1024)
        action = act.split(" ")
        if action[0] == "hash":
            if action[1] == "verify":
                ans = ""
                if os.path.isdir(action[2]):
                    conn.send(action[1]+" is a folder")
                    conn.close()
                    continue
                has = md5(action[2])
                tim = os.path.getmtime(action[2])
                conn.send(has+"\t"+time.ctime(tim))
            conn.close()
        elif action[0] == "download":
            if os.path.isdir(action[1]):
                conn.send("folder")
                conn.close()
                continue
            f = open(action[1],'rb')
            fl = ""
            l = f.read(1024)
            fl += l
            while (l):
                conn.send(l)
                #print('Sent ',repr(l))
                l = f.read(1024)
                fl += l
            time.sleep(1)
            conn.send("End")
            #print "FIle is empty now"
            time.sleep(1)
            perm = oct(os.stat(action[1]).st_mode & 0777)
            conn.send(perm)
            f.close()
            time.sleep(1)
            print('Done sending')
            conn.send(action[1]+"\t"+repr(os.path.getsize(action[1]))+"\t"+md5(action[1]))
            conn.close()
        elif action[0] == "index":
            if action[1] == "longlist":
                fils = os.listdir(os.getcwd())
                for f in fils:
                    siz = os.path.getsize(f)
                    tim = os.path.getmtime(f)
                    if os.path.isdir(f):
                        typ = "folder"
                    else:
                        typ = magic.from_file(f,mime=True)
                    conn.send(f+"\t"+repr(siz)+"\t"+typ+"\t"+time.ctime(tim))
                time.sleep(1)
                conn.send("END")


def server():
    s1.bind((host1, port1))
    s1.listen(5)
    #print 'Server listening....'
    flag = 0
    while 1:
        conn, addr = s1.accept()
        print 
        print 'Got connection from', addr
        act = conn.recv(1024)
        action = act.split(" ")
        if action[0] == "download":
            fils = os.listdir(os.getcwd())
            if action[1] in fils:
                if os.path.isdir(action[1]):
                    conn.send("folder")
                    conn.close()
                    continue
                f = open(action[1],'rb')
                fl = ""
                l = f.read(1024)
                fl += l
                while (l):
                    conn.send(l)
                    #print('Sent ',repr(l))
                    l = f.read(1024)
                    fl += l
                time.sleep(1)
                conn.send("End")
                #print "FIle is empty now"
                time.sleep(1)
                perm = oct(os.stat(action[1]).st_mode & 0777)
                conn.send(perm)
                f.close()
                time.sleep(1)
                print('Done sending')
                conn.send(action[1]+"\t"+repr(os.path.getsize(action[1]))+"\t"+md5(action[1]))
            else:
                conn.send("imaginary!")
            conn.close()

        elif action[0] == "hash":
            if action[1] == "verify":
                ans = ""
                if action[1] in os.listdir(os.getcwd()):
                    if os.path.isdir(action[2]):
                        conn.send(action[1]+" is a folder")
                        conn.close()
                        continue
                    has = md5(action[2])
                    tim = os.path.getmtime(action[2])
                    conn.send(has+"\t"+time.ctime(tim))
                else:
                    conn.send("imaginary!")

            elif action[1] == "checkall":
                fils = os.listdir(os.getcwd())
                for f in fils:
                    if os.path.isdir(f):
                        conn.send(f+" is a folder")
                        continue
                    has = md5(f)
                    tim = os.path.getmtime(f)
                    conn.send(f+"\t"+has+"\t"+time.ctime(tim))
                time.sleep(1)
                conn.send("END")
            conn.close()
        
        elif action[0] == "index":
            if action[1] == "longlist":
                fils = os.listdir(os.getcwd())
                for f in fils:
                    siz = os.path.getsize(f)
                    tim = os.path.getmtime(f)
                    if os.path.isdir(f):
                        typ = "folder"
                    else:
                        typ = magic.from_file(f,mime=True)
                    conn.send(f+"\t"+repr(siz)+"\t"+typ+"\t"+time.ctime(tim))
                time.sleep(1)
                conn.send("END")

            elif action[1] == "shortlist":
                fils = os.listdir(os.getcwd())
                for f in fils:
                    siz = os.path.getsize(f)
                    tim = os.path.getmtime(f)
                    if os.path.isdir(f):
                        typ = "folder"
                    else:
                        typ = magic.from_file(f,mime=True)
                    if tim >= float(action[2]) and tim <= float(action[3]):
                        conn.send(f+"\t"+repr(siz)+"\t"+typ+"\t"+time.ctime(tim))
                time.sleep(1)
                conn.send("END")
            elif action[1] == "regex":
                stri = str(action[2])
                files = os.listdir(os.curdir)
                fin = ""
                fc = 0
                for f in files:
                    if re.search(stri, f):
                        st = os.stat(f)
                        ty = magic.from_file(f)
                        mtime = os.path.getmtime(f)
                        fin = fin + f + ' ' + str(st.st_size) + ' ' + time.ctime(mtime) + ' ' + ty + '\n'
                        fc += 1
                if fc is 0:
                    conn.send('No files found')
                else:
                    conn.send(fin)
            conn.close()

clt = threading.Thread(target=client,args=())
ser = threading.Thread(target=server,args=())
syn1 = threading.Thread(target=sync,args=())
syn2 = threading.Thread(target=synfunc,args=())

clt.start()
ser.start()
syn2.start()
time.sleep(10)
syn1.start()
