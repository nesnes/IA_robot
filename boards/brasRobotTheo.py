from boards.board import Board
from boards.board import RetryException
from boards.board import retry
from webInterface.interface import functionUI
import time
   
class BrasRobotTheo(Board):

    def __init__(self, nom, fonction, communication, param1=None, param2=None):
        Board.__init__(self, nom, fonction, communication, param1, param2)
        self.nom = nom
        self.fonction = fonction
        self.communication = communication
        
    @retry()
    def armSetServo(self, servo, angle):
        if self.isConnected():
            self.sendMessage("setArmServo {} {}".format(servo, angle))
            ack = self.receiveMessage()
            if "OK" not in ack:  # if ERROR is received, retry
                raise RetryException
            return True
        return False
        

    def armGetServos(self):
        if self.isConnected():
            self.sendMessage("getServos")
            ack = self.receiveMessage()
            print ack
            return True
        return False

    @retry()
    @functionUI(u'{"controls":['
    '{"arg":"a0","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a1","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a2","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a3","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a4","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"a5","type":"range","min":0,"max":180,"val":90},'
    '{"arg":"duration","type":"range","min":0,"max":999,"val":0}'
    ']}')
    def armSetPose(self, a0, a1, a2, a3, a4, a5, duration=0):
        if self.isConnected():
            self.sendMessage("Z {} {} {} {} {} {} {}".format(a0, a1, a2, a3, a4, a5, duration))
            ack = self.receiveMessage(1.5)
            if "OK" not in ack:  # if ERROR is received, retry
                raise RetryException
            return True
        return False

    @retry()
    def pumpOn(self):
        if self.isConnected():
            self.sendMessage("pump on")
            ack = self.receiveMessage()
            if "OK" not in ack:  # if ERROR is received, retry
                raise RetryException
            return True
        return False

    @retry()
    def pumpOff(self):
        if self.isConnected():
            self.sendMessage("pump off")
            ack = self.receiveMessage()
            if "OK" not in ack:  # if ERROR is received, retry
                raise RetryException
            return True
        return False

    """def armDefault(self, side):
        if self.isConnected():
            self.sendMessage("arm default {}\r\n".format(side))
            time.sleep(0.3)
            ack = self.receiveMessage(2)
            if "OK" not in ack:  # if ERROR is received, retry
                time.sleep(0.1)
                print "retry armDefault("+ack+")"
                return self.armDefault(side)
            return True
        return False"""

    
