import webInterface
from webInterface.httpServer import HttpServer
from webInterface.wsServer import WSServer
from webInterface.SimpleWebSocketServer import SimpleWebSocketServer
import threading
import sys
import __builtin__
import time
import json
import inspect
import glob

class StdOutIntercepter:
    def __init__(self):
        self.content = []
        self._stdout = sys.stdout
        sys.stdout = self
    def write(self, string):
        self.content.append(string)
        self._stdout.write(string)
    def popLine(self):
        return self.content.pop(0)
    def getLineCount(self):
        return len(self.content)

def functionUI(json):
   def wrapper(func):
       setattr(func, 'functionUI', json)
       return func
   return wrapper

class MapElement(object):
    def __init__(self):
        self.id = 0
        self.x = 0
        self.y = 0
        self.angle = 0
        self.layer = 0
        self.forme = None
        self.zoneAcces = None
        self.zoneEvitement = None

    def serialize(self):
        str = u'{'
        str += u'"id":{},'.format(self.id)
        str += u'"x":{},'.format(self.x)
        str += u'"y":{},'.format(self.y)
        str += u'"angle":{}'.format(self.angle)
        if self.forme:
            str += u',"shape":'+self.forme.toJson()
        if self.zoneAcces:
            str += u',"accessPoint":'+self.zoneAcces.toJson()
        if self.zoneEvitement:
            str += u',"avoidShape":'+self.zoneEvitement.forme.toJson()
        str += u'}'
        return str

class RunningParameters(object):
    def __init__(self):
        self.mapFile = ""
        self.robotFile = ""
        self.objectiveFile = ""
        self.robotConnected = False

class RunningState:
    (PLAY,
     STOP,
     MANUAL
    ) = range(3)

class Interface():

    def __init__(self):
        __builtin__.interface = self
        webInterface.instance = self
        self.httpServer = HttpServer()
        self.wsServer = SimpleWebSocketServer('', 8090, WSServer)
        self.wsThread = threading.Thread(target=self.runWSThread)
        self.stopWs = False
        try:
            self.wsThread.start()
            print "WS server launched"
        except KeyboardInterrupt:
            print "ERROR WS server not launched"

        self.outputIntercetion = StdOutIntercepter()

        self.mapElementList = []
        self.dynamicElementList = []
        self.callableElementList = []
        self.mapBackground = None
        self.runningState = RunningState.STOP
        self.runningParameters = RunningParameters()

    def __del__(self):
        self.stopWs = True

    def runWSThread(self):
        while not __builtin__.stopThread and not self.stopWs:
            self.wsServer.serveonce()
        print "Stoping WS server"
        self.wsServer.close()
        print "WS server stopped"

    def __removeFromList(self, obj, list):
        for element in list:
            if element.id == id(obj):
                list.remove(element)
                break

    def __addToList(self, obj, list):
        elem = MapElement()
        foundObj = False
        for element in list:
            if element.id == id(obj):
                elem = element
                foundObj = True
                break

        elem.id = id(obj)
        if hasattr(obj, 'x'):
            elem.x = obj.x
        if hasattr(obj, 'y'):
            elem.y = obj.y
        if hasattr(obj, 'angle'):
            elem.angle = obj.angle
        if hasattr(obj, 'forme'):
            elem.forme = obj.forme
        if hasattr(obj, 'zoneAcces'):
            elem.zoneAcces = obj.zoneAcces
        if hasattr(obj, 'zoneEvitement'):
            elem.zoneEvitement = obj.zoneEvitement
        if not foundObj:
            list.append(elem)


    def removeMapElement(self, obj):
        self.__removeFromList(obj, self.mapElementList)

    def addMapElement(self, obj):
        self.__addToList(obj, self.mapElementList)

    def removeDynamicElement(self, obj):
        self.__removeFromList(obj, self.mapElementList)

    def addDynamicElement(self, obj):
        self.__addToList(obj, self.dynamicElementList)

    def clearCallableObjectList(self):
        self.callableElementList = []

    def addCallableObject(self, object):
        for element in self.callableElementList:
            if id(element) == id(object):
                self.callableElementList.remove(element)
                break
        self.callableElementList.append(object)

    def serializeCallableObjects(self):
        str = u'['
        for e in range(0, len(self.callableElementList)):
            str += u'{"object":"'+self.callableElementList[e].__class__.__name__+u'",'
            str += u'"functions":['
            functions = [method_name for method_name in dir(self.callableElementList[e]) if method_name[0] != "_" and callable(getattr(self.callableElementList[e], method_name))]
            for i in range(0, len(functions)):
                str += u'{"name":"'+ functions[i] + u'",'
                str += u'"arguments":['
                argList = [arg for arg in inspect.getargspec(getattr(self.callableElementList[e],functions[i])).args if arg != "self"]
                for a in range(0, len(argList)):
                    str += u'"' + argList[a] + u'"'
                    if a < len(argList) - 1:
                        str += u','
                str += u']'
                if hasattr(getattr(self.callableElementList[e],functions[i]), "functionUI"):
                    #print "{} {}:".format(self.callableElementList[e].__class__.__name__,functions[i])
                    #print getattr(getattr(self.callableElementList[e],functions[i]), "functionUI")
                    str += u',"functionUI":'
                    str += getattr(getattr(self.callableElementList[e],functions[i]), "functionUI")
                str += u'}'
                if i < len(functions) - 1:
                    str += u','
            str += u']'
            str += u'}'
            if e < len(self.callableElementList) - 1:
                str += u','
        str += u']'
        return str

    def stringify(self, obj):
        return u''+json.dumps(obj, separators=(',',':'))


    def serializeElementList(self, list):
        str = u'['
        for i in range(0, len(list)):
            str += list[i].serialize()
            if i < len(list)-1:
                str += u','
        str += u']'
        return str

    def createMessage(self, function, data):
        str = u'{'
        str += u'"function":"{}",'.format(function)
        str += u'"data":{}'.format(data)
        str += u'}'
        return str

    def onMessage(self, client, message):
        if "getMapElements" in message:
            data = self.serializeElementList(self.mapElementList)
            msg = self.createMessage("getMapElements", data)
            client.sendMessage(msg)
        if "getMapBackground" in message:
            data = u'""'
            if self.mapBackground:
                data = u'"/'+self.mapBackground+u'"'
            msg = self.createMessage("getMapBackground", data)
            client.sendMessage(msg)
        if "getDynamicElements" in message:
            data = self.serializeElementList(self.dynamicElementList)
            msg = self.createMessage("getDynamicElements", data)
            client.sendMessage(msg)
        if "getCallableElements" in message:
            data = self.serializeCallableObjects()
            msg = self.createMessage("getCallableElements", data)
            client.sendMessage(msg)
        if "callObjectFunction" in message:
            paramsJson = message[len("callObjectFunction "):]
            params = json.loads(paramsJson)
            for obj in self.callableElementList:
                if obj.__class__.__name__ == params["object"]:
                    argumentList = []
                    for arg in params["arguments"]:
                        val = None
                        try:
                            val = int(arg)
                        except ValueError:
                            try:
                                val = float(arg)
                            except ValueError:
                                val = arg
                        argumentList.append(val)
                    print "------> Calling ", params["object"], params["function"], argumentList
                    if hasattr(obj, params["function"]):
                        thread = threading.Thread(target=getattr(obj, params["function"]), args=argumentList)
                        thread.start()
                    else:
                        print "Can't find", params["function"]
                    break
        if "setRunningState" in message:
            state = message[len("setRunningState "):]
            if state == "PLAY":
                self.runningState = RunningState.PLAY
                self.mapElementList = []
                self.dynamicElementList = []
            if state == "MANUAL":
                self.runningState = RunningState.MANUAL
                self.mapElementList = []
                self.dynamicElementList = []
            if state == "STOP":
                self.runningState = RunningState.STOP
        if "setRunningParameters" in message:
            paramsJson = message[len("setRunningParameters "):]
            params = json.loads(paramsJson)
            if 'mapFilePath' in params:
                self.runningParameters.mapFile = params["mapFilePath"]
            if 'robotFilePath' in params:
                self.runningParameters.robotFile = params["robotFilePath"]
            if 'objectiveFilePath' in params:
                self.runningParameters.objectiveFile = params["objectiveFilePath"]
            if 'robotConnected' in params:
                self.runningParameters.robotConnected = params["robotConnected"]
        if "getFileContent" in message:
            path = message[len("getFileContent "):]
            result = {"path":path, "content":""}
            try:
                with open(path, 'r') as file:
                    result["content"] = file.read()
            except:
                print "Can't open ", path
            msg = self.createMessage("getFileContent", self.stringify(result))
            client.sendMessage(msg)
        if "setFileContent" in message:
            data = message[len("setFileContent "):]
            result = json.loads(data)
            if 'path' in result and "content" in result:
                with open(result["path"], 'w') as file:
                    print "Saving", result["path"]
                    file.write(result["content"])
        if "getOutputLines" in message:
            msgList = []
            while self.outputIntercetion.getLineCount():
                msgList.append(self.outputIntercetion.popLine())
            msg = self.createMessage("getOutputLines", self.stringify(msgList))
            client.sendMessage(msg)
        if "getFileList" in message:
            fileList = []
            fileList += glob.glob("robots/*.py")
            fileList += glob.glob("robots/*.xml")
            fileList += glob.glob("intelligence/*.py")
            fileList += glob.glob("cartographie/*.py")
            fileList += glob.glob("boards/*.py")
            fileList += glob.glob("cartes/*.xml")
            fileList += glob.glob("objectifs/*.xml")
            fileList += glob.glob("objectifs/*/*.xml")
            #fileList += glob.glob("webInterface/*.py")
            fileList += glob.glob("webInterface/*.html")
            fileList += glob.glob("webInterface/css/*.css")
            fileList += glob.glob("webInterface/js/*.js")
            msg = self.createMessage("getFileList", self.stringify(fileList))
            client.sendMessage(msg)


if __name__ == '__main__':
    interface = Interface()
    print "created"
