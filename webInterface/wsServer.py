from webInterface.SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import __builtin__

clients = []
class WSServer(WebSocket):

    def handleMessage(self):
        __builtin__.interface.onMessage(self, self.data)
        #client.sendMessage(self.address[0] + u' - ' + self.data)

    def handleConnected(self):
        print(self.address, 'connected')
        for client in clients:
            client.sendMessage(self.address[0] + u' - connected')
        clients.append(self)

    def handleClose(self):
        clients.remove(self)
        print(self.address, 'closed')
        for client in clients:
            client.sendMessage(self.address[0] + u' - disconnected')

