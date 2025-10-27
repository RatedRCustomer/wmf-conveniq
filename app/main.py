import json

from fastapi import FastAPI, WebSocket
from nats.aio.client import Client
from contextlib import asynccontextmanager
import asyncio
import serv as srv
import WMF as wmf
import os
import websockets

natsUrl = os.environ.get("NATS_URL", "nats://nats:4222")
wmfURL = os.environ.get("WMF_URL", "ws://192.168.143.31:25000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    #
    print("Start")
    nc = Client()
    await nc.connect(servers=natsUrl)
    app.state.nc = nc
    # await nc.subscribe('wmf.sub', cb=subscribe_handler)
    asyncio.create_task(client_task())
    yield
    #
    print("Stop")
    await nc.close()


app = FastAPI(lifespan=lifespan)

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):  # Додано nc як аргумент
    # send2POS = srv.pubMsg()
    # global send2POS
    nc = app.state.nc
    await websocket.accept()
    async def subscribe_handler(msg):
        data = msg.data.decode()
#        print("Data: ", data)

        fromPOS = srv.subMsg(json.loads(data))
#        print("fromPOS: ", fromPOS.toJson())
        toWMF = srv.toWMF(fromPOS)

#        print("toWMF: ", toWMF.toJson())
        await websocket.send_json(toWMF.toJson())

    await nc.subscribe('wmf.sub', cb=subscribe_handler)

    while True:
        try:
            # message = await websocket.receive_text()
            message = await websocket.receive_json()

            if message["Purchase"]["MessageType"] != 9:
                purchase = wmf.Purchase(message)
                print("purchase: ", purchase.toJson())
                send2POS = srv.fromWMF(purchase)
                if purchase.MessageType == 2:
                    await pub_msg(send2POS.toJson());

                else:
                    await pub_msg(send2POS.toJson());


        except Exception as e:
            print("Exc: ", e)
            await pub_msg(str(e))
            break


async def client_task():
  nc = app.state.nc
  while True:
    print("start Connect")

    #url = "ws://localhost:25000"   ## URL WS - server
    try:
        async with websockets.connect(wmfURL) as websocket:

            async def message_handler(msg):
                subject = msg.subject
                reply = msg.reply
                data = msg.data.decode()
                print(f'Received a message on {subject}: {data}')
                await websocket.send(data)

            await nc.subscribe("wmf.cmd", cb=message_handler)

            print("Connect")
            cn = {"Status": "Connected"}
            await nc.publish("wmf.msg", json.dumps(cn).encode())
            cn = {"function":"startPushErrors"}
            await nc.publish("wmf.cmd", json.dumps(cn).encode())

            while True:
               data = await websocket.recv()
               if data is None:
                     break
               #print(f"Received from wmf: {data}")
               await nc.publish("wmf.msg", data.encode())

    except Exception as e :
        #print(f"Connection closed, retrying in 5 seconds...")
        #print(e)
        cn = {"Status": "Connection closed, retrying in 5 seconds..."}
        await nc.publish("wmf.msg", json.dumps(cn).encode())
        await asyncio.sleep(5)  # Wait before retrying



async def pub_msg(msg):
    nc = app.state.nc
    await nc.publish("wmf.pub", msg.encode())

#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
