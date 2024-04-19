import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pathlib
from dotenv import main
import os
from tinydb import TinyDB, Query
import requests
import json
import bisect

class PostOrder(BaseModel):
    ticker: str
    value: str
    uid: str


basedir = pathlib.Path(__file__).resolve().parents[1]
main.load_dotenv(basedir / ".env")


db = TinyDB('db.json')
table = db.table('default')
query = Query()

app = FastAPI()

@app.post("/order")
async def post_order(order: PostOrder):
    
    def insert_sorted_order(order_list, user_list, value, user_id):
        """
        Inserts an order into the order list and the corresponding user ID into the user list,
        ensuring both lists remain sorted by the order values.
        """
        # Determine the correct position to insert the value
        position = 0
        while position < len(order_list) and (value < order_list[position] if value < 0 else value > order_list[position]):
            position += 1

        # Insert the order value and user ID at the found position
        order_list.insert(position, value)
        user_list.insert(position, user_id)
        return position

    def check_spread(buy_list, sell_list, userbuy, usersell):
        """
        Check if the spread is being shorted, i.e., highest buy price is higher than the lowest sell price.
        """

        print(f"buy list: {str(buy_list)}")

        highest_buy_index = -1
        lowest_sell_index = -1
        maxBuy = -1
        minSell = 1000000000
        
        if len(buy_list)==0:
            highest_buy_index=0
        else:
            maxBuy = buy_list[-1]
            highest_buy_index = len(buy_list)-1
        if len(sell_list)==0:
            # print("empty!")
            lowest_sell_index=0
        else:
            # print("list not empty!"+str(sell_list))
            minSell =sell_list[0]
            lowest_sell_index = 0
        if buy_list and sell_list and maxBuy>=minSell and buy_list!=[]:
            print("yayy")
        
            # Remove these orders and their corresponding user IDs
            buy_list.pop(highest_buy_index)
            userbuy.pop(highest_buy_index)
            sell_list.pop(lowest_sell_index)
            usersell.pop(lowest_sell_index)


    try:
        print("Received order:", order) 
        # request_body = await request.json()  # Asynchronously get the request body
        # print("Request body:", order)

        ticker = order.ticker
        value = int(order.value)
        uid = order.uid

        #fetching info from db
        result = db.search(query.defi.exists())
        print(result)
        print(ticker)
        print("*")
        
        tickerFound = False
        if ticker in result[0]['defi']:
            tickerFound = True

        if not tickerFound:
            # create new object to return
            new_object = {
                "B_L":[],
                "UB_L":[],
                "S_L":[],
                "US_L":[],
            }
            print("Creating ticker")

            result[0]['defi'][ticker] = new_object
            db.update({'defi': result[0]['defi']} )
            result = db.search(query.defi.exists())

        print(result[0]['defi'])

        print(result)


        print("Lists:")
        b_l, s_l, ub_l, us_l = result[0]['defi'][ticker]['B_L'], result[0]['defi'][ticker]['S_L'], result[0]['defi'][ticker]['UB_L'], result[0]['defi'][ticker]['US_L']
        # print("ticker_doc:"+str(msft_data))
        
        print(str(b_l) + str (s_l) +str(ub_l) + str(us_l))

        # Add to buy_list or sell_list based on val:
        resObj = {'B_L': b_l, 'UB_L': ub_l, 'S_L': s_l, 'US_L': us_l}
        print("resobj: "+str(resObj))

        if(value>0):
            insert_sorted_order(b_l, ub_l, value, uid)
        else:
            insert_sorted_order(s_l, us_l, -value, uid)

        resObj = {'B_L': b_l, 'UB_L': ub_l, 'S_L': s_l, 'US_L': us_l}
        print(resObj)
        
        check_spread(b_l, s_l, ub_l, us_l)
        

        resObj = {'B_L': b_l, 'UB_L': ub_l, 'S_L': s_l, 'US_L': us_l}
        result[0]['defi'][ticker] = resObj

        print(resObj)

        for item in result:
            if ticker in item['defi']: 
                # Perform the update
                db.update({'defi': result[0]['defi']}, doc_ids=[item.doc_id])
        print("db update performed")

        
        return {"message": "Order processed successfully"}
    

    except Exception as e:
        print("exception "+str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_orders_ticker")
async def get_orders(ticker: str):  # Assuming you want to fetch by ticker
    try:
        #fetching info from db
        result = db.search(query.defi.exists())
        msft_data = [item['defi'][ticker] for item in result if ticker in item['defi']]

        return msft_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        print("Exception: "+str(e))

@app.get("/get_orders_uid")
async def get_orders(uid: str):  # Assuming you want to fetch by ticker
    try:
        
        #fetching info from db
        result = db.search(query.defi.exists())
        print((result[0]['defi']))
        filtered_data = []
        filtered = {}
        transactions = []

        for i,ticker in enumerate(result[0]['defi']):
                print("!")
                print(result[0]['defi'])
                print(result[0]['defi'][ticker])
                # print(result[0]['defi'][ticker])
                x = result[0]['defi'][ticker]['UB_L']
                y = result[0]['defi'][ticker]['US_L']
                print(x)
                # print(x[1])
                if uid in x or uid in y:
                    if uid in x:
                        b_l = result[0]['defi'][ticker]['B_L']
                        s_l = result[0]['defi'][ticker]['B_L']
                        buy_orders = [b_l[index] for index, value in enumerate(x) if value == uid]
                        sell_orders = [s_l[index] for index, value in enumerate(y) if value == uid]
                        retObj = {"buy_orders":buy_orders, "sell_orders":sell_orders}


                    
                    if ticker in filtered:
                        filtered[ticker].append(retObj)
                    else:
                        filtered[ticker] = retObj

        return filtered 



    except Exception as e:
        print("Exception: "+str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cancel_order")
async def cancel_order(uid: str, ticker: str, ordertype: int, val: int):
    
    result = db.search(query.defi.exists())
    msft_data = [item['defi'][ticker] for item in result if ticker in item['defi']]

    

    
    try:
        order_canceled = False
        for record in msft_data:
            print("record: "+str(record))

            b_l, ub_l = result[0]['defi'][ticker]['B_L'], result[0]['defi'][ticker]['UB_L']
            s_l, us_l = result[0]['defi'][ticker]['S_L'], result[0]['defi'][ticker]['US_L']

            print("uid:"+str(uid))
            print(ub_l)

            # buy
            if ordertype == 1 and uid in ub_l:
                index = ub_l.index(uid)
                if(b_l[index]==val):
                    ub_l.pop(index)
                    b_l.pop(index)
                    order_canceled = True
            
            # sell
            elif ordertype == 2 and uid in us_l:
                index = us_l.index(uid)
                if(s_l[index]==val):
                    us_l.pop(index)
                    s_l.pop(index)
                    order_canceled = True

            if order_canceled:
                # Update the record with new lists
                print("!")
                new_data = {'B_L': b_l, 'UB_L': ub_l, 'S_L': s_l, 'US_L': us_l}
                db.update({'defi': {ticker: new_data}})
                break

        if order_canceled:
            return {"message": "Order canceled successfully"}
        else:
            return {"message": "Order not found", "status": 404}

    except Exception as e:
        print("Exception: "+str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except ValidationError as exc:
        print(repr(exc.errors()[0]['type']))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 8000)))