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
async def websocket_endpoint(websocket: WebSocket):
    nc = app.state.nc
    await websocket.accept()
    subscription = None
    ws_open = True

    async def subscribe_handler(msg):
        if not ws_open:
            return
        try:
            data = msg.data.decode()
            fromPOS = srv.subMsg(json.loads(data))
            toWMF = srv.toWMF(fromPOS)
            await websocket.send_json(toWMF.toJson())
        except Exception:
            pass  # WebSocket closed, ignore

    try:
        subscription = await nc.subscribe('wmf.sub', cb=subscribe_handler)

        while True:
            message = await websocket.receive_json()

            if message["Purchase"]["MessageType"] != 9:
                purchase = wmf.Purchase(message)
                print("purchase: ", purchase.toJson())
                send2POS = srv.fromWMF(purchase)
                await pub_msg(send2POS.toJson())

    except Exception as e:
        print("WebSocket endpoint error: ", e)
        try:
            await pub_msg(str(e))
        except Exception:
            pass
    finally:
        ws_open = False
        # Unsubscribe to prevent memory leak
        if subscription:
            try:
                await subscription.unsubscribe()
                print("Unsubscribed from wmf.sub")
            except Exception as e:
                print(f"Error unsubscribing from wmf.sub: {e}")


async def client_task():
  nc = app.state.nc
  while True:
    print("start Connect")
    subscription = None

    try:
        async with websockets.connect(wmfURL) as websocket:
            # Flag to track if websocket is still open
            ws_open = True

            async def message_handler(msg):
                if not ws_open:
                    return
                subject = msg.subject
                data = msg.data.decode()
                print(f'Received a message on {subject}: {data}')
                try:
                    await websocket.send(data)
                except websockets.exceptions.ConnectionClosed:
                    pass  # WebSocket already closed, ignore

            subscription = await nc.subscribe("wmf.cmd", cb=message_handler)

            print("Connect")
            cn = {"Status": "Connected"}
            await nc.publish("wmf.msg", json.dumps(cn).encode())
            cn = {"function":"startPushErrors"}
            await nc.publish("wmf.cmd", json.dumps(cn).encode())

            try:
                while True:
                   data = await websocket.recv()
                   if data is None:
                         break
                   await nc.publish("wmf.msg", data.encode())
            finally:
                ws_open = False

    except Exception as e:
        print(f"WebSocket error: {e}")
        cn = {"Status": "Connection closed, retrying in 5 seconds..."}
        await nc.publish("wmf.msg", json.dumps(cn).encode())
    finally:
        # Always unsubscribe to prevent memory leak
        if subscription:
            try:
                await subscription.unsubscribe()
                print("Unsubscribed from wmf.cmd")
            except Exception as e:
                print(f"Error unsubscribing: {e}")

    await asyncio.sleep(5)  # Wait before retrying



async def pub_msg(msg):
    nc = app.state.nc
    await nc.publish("wmf.pub", msg.encode())

#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
