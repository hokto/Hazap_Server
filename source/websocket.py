from websocket_server import WebsocketServer

def new_client(client, server):
  print(server)


def send_msg_allclient(client, server,message):
  print(client)
  if message.split(":")[0] == "long":
    server.send_message_to_all("requested value:"+message.split(":")[1]+":"+message.split(":")[2])
  elif message.split(":")[0]=="value":
    server.send_message_to_all("value:"+message.split(":")[1])

server = WebsocketServer(5000, host='192.168.11.2')
server.set_fn_new_client(new_client)
server.set_fn_message_received(send_msg_allclient)
server.run_forever()