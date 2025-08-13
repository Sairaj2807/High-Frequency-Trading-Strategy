import asyncio
import json
import ssl
import websockets
import requests
import numpy as np
from datetime import datetime
from google.protobuf.json_format import MessageToDict

import MarketDataFeedV3_pb2 as pb
from config import INSTRUMENT_KEY, LIVE_ACCESS_TOKEN
from kalman import KalmanFilter
from trader import place_order, record_trade
from logger import log

kf = KalmanFilter()
position = 0

def get_market_data_feed_authorize_v3():
    url = 'https://api.upstox.com/v3/feed/market-data-feed/authorize'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {LIVE_ACCESS_TOKEN}'
    }
    response = requests.get(url=url, headers=headers)
    return response.json()

def decode_protobuf(buffer):
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return MessageToDict(feed_response)

def extract_ltp_from_dict(feed_dict):
    try:
        return float(
            feed_dict['feeds'][INSTRUMENT_KEY]['ff']['marketFF']['ltpc']['ltp']
        )
    except Exception as e:
        log(f" Failed to extract LTP: {e}")
        return None

async def fetch_market_data():
    global position
    log(" Starting Kalman strategy...")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    auth = get_market_data_feed_authorize_v3()
    uri = auth["data"]["authorized_redirect_uri"]

    async with websockets.connect(uri, ssl=ssl_context) as ws:
        log(" WebSocket connected...")

        await asyncio.sleep(1)

        sub_data = {
            "guid": "kalman-guid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": [INSTRUMENT_KEY]
            }
        }

        await ws.send(json.dumps(sub_data).encode())
        log(f" Subscription sent for: {INSTRUMENT_KEY}")

        while True:
            try:
                msg = await ws.recv()
                data_dict = decode_protobuf(msg)

                # Handle non-feed messages (type 0, 2)
                if "feeds" not in data_dict:
                    log(f" Non-feed message received: {data_dict}")
                    continue

                ltp = extract_ltp_from_dict(data_dict)
                if ltp is None:
                    continue

                est_price = kf.update(np.array([[ltp]]))
                log(f" Tick {kf.ticks} | Price ₹{ltp:.2f} | KF ₹{est_price:.2f}")

                if kf.ticks < 100:
                    continue

                rel_diff = (est_price - ltp) / ltp

                if rel_diff > 0.001 and position == 0:
                    if np.random.rand() > 0.5:
                        log(f" BUY SIGNAL | RelDiff {rel_diff:.5f}")
                        place_order("BUY")
                        record_trade("BUY", ltp, est_price)
                        position = 1

                elif rel_diff < -0.001 and position == 1:
                    if np.random.rand() > 0.5:
                        log(f" SELL SIGNAL | RelDiff {rel_diff:.5f}")
                        place_order("SELL")
                        record_trade("SELL", ltp, est_price)
                        position = 0

                if datetime.now().strftime("%H:%M") >= "15:29":
                    if position == 1:
                        log(" Market Close: Flattening position.")
                        place_order("SELL")
                        record_trade("EOD SELL", ltp, est_price)
                        position = 0
                    kf.__init__()
                    log(" Kalman filter reset for new session.")

            except Exception as e:
                log(f" Error in loop: {str(e)}")
                await asyncio.sleep(1)

# Start continuous event loop
if __name__ == "__main__":
    while True:
        try:
            asyncio.run(fetch_market_data())
        except Exception as e:
            log(f" WebSocket disconnected or crashed: {e}. Retrying in 5s...")
            asyncio.sleep(5)
