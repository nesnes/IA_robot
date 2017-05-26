import serial
class CommunicationRobot:

    def __init__(self,port):
        self.portserie = port
        if self.portserie == '':
            return
        try:
            self.portserie = serial.Serial(port, 115200, timeout=10)
            self.portserie.flushInput()
            self.portserie.flushOutput()
        except:
            print "ERREUR: Impossible d'ouvrir le port serie " + port + "!!! As tu bien utilise SUDO ?"
            exit(1)
            self.portserie = ''

    def envoyer(self,message):
        if self.portserie == '':
            return
        if self.portserie.isOpen():
            self.portserie.write(message)
        else:
            print "ERREUR: Impossible d'acceder au port serie"

    def recevoir(self):
        if self.portserie == '':
            return ""
        if self.portserie.isOpen():
            message = self.portserie.readline()
            self.portserie.flushInput()
            return message
        else:
            print "ERREUR: Impossible d'acceder au port serie"
        return ""
