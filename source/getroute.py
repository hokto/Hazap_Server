from websocket_server import WebsocketServer
import HazapModules
def new_client(client, server):
  print(server)


def send_msg_allclient(client, server,message):
  print(client)
  if message.split(":")[0] == "long":
  	size=len(message.split(":"))-1
  	data=""
  	for i in range(size):
  		data+=(":"+message.split(":")[i+1])
  	server.send_message_to_all("requested value"+data)
  elif message.split(":")[0]=="value":
      server.send_message_to_all("value:"+message.split(":")[1]+":"+message.split(":")[2])

server = WebsocketServer(5000, host=HazapModules.addres)
server.set_fn_new_client(new_client)
server.set_fn_message_received(send_msg_allclient)
server.run_forever()
