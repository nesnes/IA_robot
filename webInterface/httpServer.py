import SimpleHTTPServer
import SocketServer
import socket
import threading
import time
import __builtin__


class HttpServer():

    def __init__(self):
        self.httpPort = 8080
        self.httpHandler = SimpleHTTPServer.SimpleHTTPRequestHandler
        while True:
            try:
                self.htttpConnection = SocketServer.TCPServer(("", self.httpPort), self.httpHandler)
                break
            except:
                print "Can't use port", self.httpPort, "trying", self.httpPort+1
                self.httpPort += 1
        self.htttpConnection.timeout = 1
        self.httpThread = threading.Thread(target=self.htttpConnection.serve_forever)
        self.httpStopingThread = threading.Thread(target=self.stopHttpThread)
        self.httpThread.daemon = True
        self.stopHttp = False
        try:
            self.httpThread.start()
            self.httpStopingThread.start()
            print "http server launched on http://{}:{}/webInterface/index.html".format(socket.gethostname(), self.httpPort)
        except KeyboardInterrupt:
            self.htttpConnection.shutdown()
            print "ERROR http server not launched"

    def __del__(self):
        self.stopHttp = True
        self.htttpConnection.shutdown()

    def stopHttpThread(self):
        while not __builtin__.stopThread and not self.stopHttp:
            time.sleep(1)
        print "Stoping web interface, please refresh your navigator"
        self.htttpConnection.shutdown()
        print "Web interface stopped"
        self.htttpConnection.server_close()
        self.htttpConnection.socket.close()
