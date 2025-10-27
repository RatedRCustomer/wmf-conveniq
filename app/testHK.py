from keyboard import add_hotkey, wait
import asyncio
from nats import NATS
import json
import serv


jsIn = {"UUID": "123-125", "MachineID": 1, "Error": [0], "idError": 0, "MessageType": 4, "MessageTypeName": "CREDIT_DENY", "RcpNumber": 0, "RcpName": "DEFAULT", "TransactionStatusCode": 2, "TransactionStatusName": "ACCEPTED"}
jsOut = {"UUID": "1339068-99","MachineID": 222,"MessageType": 7,"MessageTypeName": "testName","Notification": "Drink Coffee!!", "RcpNumber":0,"RcpName":"DEFAULT","TransactionStatusCode":2,"TransactionStatusName":"DENIED" }

testIn = serv.pubMsg(jsIn)

async def main():
    nc = NATS()
    print("main")
    await nc.connect('nats://192.168.1.10:4222')
    async def subscribe_handler(msg):
        global testIn
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        testIn = serv.pubMsg(json.loads(data))
        print("testIn_sub", testIn.toJson())

        #print(test.toJson())
        #print(f"Received a message on {subject} {reply}: {data}')

    await nc.subscribe('wmf.pub', cb=subscribe_handler)
    await nc.flush()


async def on_callback(msg):
    global testIn
    nc1 = NATS()
    #print('pressed', key)
    await nc1.connect("nats://192.168.1.10:4222")
    print("testIn: ", testIn.toJson())

    dataOut = serv.subMsg(jsOut)
    dataOut.UUID = testIn.UUID
    dataOut.MachineID = testIn.MachineID
    dataOut.RcpName = testIn.RcpName
    dataOut.RcpNumber = testIn.RcpNumber
    if msg == "CREDIT_CONFIRM":
        dataOut.MessageTypeName = "CREDIT_CONFIRM"
        dataOut.MessageType = 3
        dataOut.Notification = "Test_CONFIRM"
        dataOut.TransactionStatusName = "ACCEPTED"
        dataOut.TransactionStatusCode = 1

    else:
        dataOut.MessageTypeName = "CREDIT_DENY"
        dataOut.MessageType = 4
        dataOut.Notification = "Test_Deny"
        dataOut.TransactionStatusName = "DENIED"
        dataOut.TransactionStatusCode = 2

    await nc1.publish("wmf.sub", f'{dataOut.toJson()}'.encode())
    await nc1.close()

    #await asyncio.sleep(1)
   # print('end for', key)

async def pr():
    global test
    nc1 = NATS()
    print("pr: ",test.__dict__)



#asyncio.run(main())
add_hotkey("a", lambda: asyncio.run(on_callback("CREDIT_CONFIRM")))
add_hotkey("d", lambda: asyncio.run(on_callback("CREDIT_DENY")))
#add_hotkey("1", lambda: asyncio.run(main()))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()

wait('esc')