#!/usr/bin/python
import sys,os
from socket import *

if (len(sys.argv) != 5):
    print("Usage: {} put/get ip port filename".format(sys.argv[0]))
    sys.exit(1)

opentype = sys.argv[1]
host = sys.argv[2] 
port = eval(sys.argv[3]) 
filename = sys.argv[4]
bufsize = 1480
addr = (host,port)
saveDir = "./received/"

def SendFile(tcpClient, filepathname):
    fd = open(filepathname, 'rb')
    data = fd.read()
    fd.close()
    tcpClient.send(data)

def SendFileToServer(addr, filename):
    sendfilename = os.path.basename(filename)
    #check file exist
    if (not os.path.exists(filename)):
        print('file<{}> not exist, please check'.format(filename))
        sys.exit(1)
    filesize = os.path.getsize(filename) 
    tcpClient = socket(AF_INET, SOCK_STREAM)
    try:
        tcpClient.connect(addr)
        #step1: send command flag, filenane, filesize
        print('send file name and size to file server...') 
        cmd = '#SENDFILE#\n{}\n{}'.format(filename, filesize)
        tcpClient.send(cmd.encode('utf8'))
        recv = tcpClient.recv(bufsize)
        if (recv != b'#OK#'):
            raise(Exception('file server return error: {}'.format(recv)))
    
        #step2: send file binary
        print('send file: ' + filename)
        SendFile(tcpClient, filename)
        recv = tcpClient.recv(bufsize)
        if (recv != b'#OK#'):
            raise(Exception('file server return error: {}'.format(recv)))
        print('send file success!')
    except Exception as e:
        print(e)
    finally:
        tcpClient.close();

#return: uniquefilename,ischanged
def GetUniqueFilename(servDir, filename):
    if (not os.path.exists(servDir)):
        os.mkdir(servDir)
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
            data = tcpClient.recv(filesize)
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

def GetFileFromServer(addr, filename):
    tcpClient = socket(AF_INET, SOCK_STREAM)
    try:
        tcpClient.connect(addr)
        
        #step1: send get size command flag, filenane
        print('send request file name to file server...') 
        cmd = '#GETFILE#\n{}'.format(filename)
        tcpClient.send(cmd.encode('utf8'))
        recv = tcpClient.recv(bufsize)
        if (not recv.startswith(b'#OK#')):
            raise(Exception('file server return error: {}'.format(recv)))
        infos = recv.decode('utf8').split('\n')
        if (len(infos) < 2):
            raise(Exception('get file size failed. error return: {}'.format(recv)))
        filesize = int(infos[1])
        print("receive file size: " + str(filesize))

        #step2: get file command flag, filename
        tcpClient.send(b'#GETFILE#')
        filename, ischanged = GetUniqueFilename(saveDir,filename)
        if (ischanged):
            print("file existed, change file name to " + filename)
        filepathname = saveDir + filename
        ReceiveFile(tcpClient, filepathname, filesize)
        tcpClient.send('#OK#')
        print("receive and save file: " + filepathname)
    except Exception as e:
        print(e)
    finally:
        tcpClient.close();

if (opentype == 'put'):
    SendFileToServer(addr, filename)
elif (opentype == 'get'):
    GetFileFromServer(addr, filename)

