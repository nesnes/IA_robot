import time
from boards.communicationI2C import CommunicationI2C

connection = CommunicationI2C("testCom", "0x07")
connection.connect()

sleepTime = 0.000
msgCountCurrent = 0
msgCount = 10001
meanRead = 0
meanWrite = 0
errorCount = 0
errorMissed = 0
result="MovingBaseAlexandreV4"
globalStart = time.time()
while msgCountCurrent < msgCount:
	msgCountCurrent += 1
	start=time.time()
	connection.sendMessage("id")
	meanWrite += (time.time()-start)*1000
	start=time.time()
	res = connection.receiveMessage(0.1)
	meanRead += (time.time()-start)*1000
	if res == "ERROR":
		errorCount += 1
	elif res != result:
		errorMissed += 1
	time.sleep(sleepTime)
	if msgCountCurrent % 100 == 1:
		print("error {}".format(errorCount))
		print("errorMissed {}".format(errorMissed))
		print("write {}ms".format(meanWrite/msgCountCurrent))
		print("read {}ms".format(meanRead/msgCountCurrent))
		print("{} msg in {}s".format(msgCountCurrent, time.time()-globalStart))
		print("----------------------------\n\n")
connection.disconnect()
