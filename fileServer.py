#!/usr/bin/python
import sys,os
from socket import *
from time import ctime
if (len(sys.argv) != 2):
    print("Usage: {} port".format(sys.argv[0]))
    sys.exit(1)

host = ''
port = eval(sys.argv[1]) 
bufsize = 1500
addr = (host,port)
servDir = './servPath/'

if (not os.path.exists(servDir)):
    os.mkdir(servDir)

#return: uniquefilename,ischanged
def GetUniqueFilename(servDir, filename):
    if (not os.path.exists(servDir + filename)): 
        return filename, False
    nPos = filename.rfind('.')
    if (nPos != -1):
        prefix = filename[:nPos]
        posfix = filename[nPos:]
    else:
        prefix = filename
        posfix = ""
    nSeq = 1
    while(True):
        newfilename = prefix + str(nSeq) + posfix 
        if (not os.path.exists(servDir + newfilename)):
            return newfilename,True
        nSeq += 1

def ReceiveFile(tcpClient, filepathname, filesize):
    try:
        tempfilepathname = filepathname + ".tmp"
        fd = open(tempfilepathname, 'wb')
        nrecv = 0
        while(True):
            data = tcpClient.recv(bufsize)
            if (not data):
                fd.close()
                raise(Exception("receive file abnormal"))
            fd.write(data)
            nrecv += len(data)
            if (nrecv >= filesize):
                break;
        fd.close()
        os.rename(tempfilepathname, filepathname)
    finally:
        if (os.path.exists(tempfilepathname)):
            os.remove(tempfilepathname)

def SendFile(tcpClient, filepathname):
    fd = open(filepathname, 'rb')
    data = fd.read()
    fd.close()
    tcpClient.send(data)

tcpServer = socket(AF_INET, SOCK_STREAM)
tcpServer.bind(addr)
tcpServer.listen(5)  #5-max links limit
n = 0
try:
    while True:
        print('Waiting for connection...')
        tcpClient, addr = tcpServer.accept()
        n+=1
        print('No.={}, connect from {}'.format(n,addr))
        
        tempfilepathname = servDir + 'default.tmp'
        try:
            #step 0: verify client
            data = tcpClient.recv(bufsize)
            flag = data.decode('utf8')
            cmdinfos = flag.split('\n')
            if (cmdinfos[0] not in ('#SENDFILE#', '#GETFILE#')):
                raise(Exception('cmd verify failed: ' + cmdinfos[0])) 
            cmd = cmdinfos[0]
            print("receive cmd: " + cmd)
            if (cmd == "#SENDFILE#"):
                filename = cmdinfos[1]
                filesize = int(cmdinfos[2])
                print("receive file name: " + filename)
                print("receive file size: " + str(filesize))
                tcpClient.send('#OK#')
                #check filename
                filename, ischanged = GetUniqueFilename(servDir,filename)
                if (ischanged):
                    print("file existed, change file name to " + filename)

                #step 2: read buffer write to file
                filepathname = servDir + filename
                ReceiveFile(tcpClient, filepathname, filesize)
                tcpClient.send('#OK#')
                print("receive and save file: " + filepathname)
            elif (cmd == '#GETFILE#'):
                filepathname = servDir + cmdinfos[1] 

                #step 1: check file and return size
                print("receive: request file " + filepathname)
                #check file exist
                if (not os.path.exists(filepathname)):
                    tcpClient.send('file not exist')
                    raise(Exception('file<{}> not exist, please check'.format(filepathname)))
                filesize = os.path.getsize(filepathname)
                tcpClient.send('#OK#\n{}'.format(filesize).encode('utf8'))
                
                #step 2: send file
                data = tcpClient.recv(bufsize)
                if (data != b'#GETFILE#'):
                    tcpClient.send('check response error')                    
                    raise(Exception('client response error: ' + data))
                print('send file: ' + filepathname)
                SendFile(tcpClient, filepathname)
                recv = tcpClient.recv(bufsize)
                if (recv != b'#OK#'):
                    raise(Exception('client return error: {}'.format(recv)))
                print('send file success!')

        except Exception as e:
            print(e.args)
        finally:
            tcpClient.close()
finally:
    tcpServer.close()
    print("Socket closed.")
