# pyFileServer
python file server and file client, translate file by tcp protocol. 

Client Usage:
./fileClient.py put/get ip port filename
1. put one file to fileserver
2. get one file from fileserver(store in the received directory)

Server Usage:
./fileServer.py port
1. support connect port config
2. save the received file in servDir directory.
3. send the requested file to client. (file in the servDir directory)

Client Usage example:
```
[/Users/aaa]$ ./fileClient.py put $destIP 28881 buff.txt
send file name and size to file server...
send file: buff.txt
send file success!
[/Users/aaa]$ ./fileClient.py get $destIP 28881 buff.txt
send request file name to file server...
receive file size: 173756
file existed, change file name to buff123.txt
receive and save file: ./received/buff123.txt
```

Message Sequence: Send File
Client-->
  #SENDFILE#
  FileName
  FileSize
Server-->
  #OK#
Client--> Send the file buffer
Server--> Receive file buffer and store it.
  #OK#

Message Sequence: Get File
Client-->
  #GETFILE#
  FileName
Server-->
  #OK#
  FileSize
Client-->
  #GETFILE#
Server--> Send the file buffer
Client--> Receive file buffer and store it.
  #OK#

