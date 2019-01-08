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


