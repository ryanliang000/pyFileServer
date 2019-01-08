# pyFileServer
python file server and file client, translate file by tcp protocol. 

Client Usage:
./fileClient.py put/get ip port filename
1. put one file to fileserver
2. get one file from fileserver(store in the received directory)

Server Usage:
./fileServer.py port
1. support connect from listening port
2. save the received file in servDir directory.
3. send the request file to fileClient.(file in the servDir directory)

Client Usage example:
```python
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

