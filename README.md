
# API Documentation

## Overview

This API provides methods for posting, fetching, and managing orders within a trading system. It integrates functionalities like order sorting, order matching based on spread, and transaction cancellation.

  

### Base URL

http://127.0.0.1:8000

  

### Authentication

This API does not currently require or implement authentication.

  

## Endpoints

## POST: /order

Adds a new order to the system.

  

### Request Body

ticker: string - The ticker symbol for the order.

value: string - The order value (positive for buy, negative for sell).

uid: string - The unique identifier for the user.


    {
    
    "ticker": "AAPL",
    
    "value": "150",
    
    "uid": "user123"
    
    }

### Responses

200 OK: Returns a message indicating successful order processing.  

    {
    
    "message": "Order processed successfully"
    
    }

500 Internal Server Error: Indicates an issue with processing the order.

    {
    
    "detail": "Error description"
    
    }

  

## GET /get_orders_ticker

Fetches orders by ticker symbol.

  

### Query Parameters

ticker: string - The ticker symbol for the orders.

### Responses

200 OK: Returns all orders associated with the specified ticker.

  

    [
    
	    {
	    
		    "B_L": [150, 200],
		    
		    "UB_L": ["user1", "user2"],
		    
		    "S_L": [-100, -50],
		    
		    "US_L": ["user3", "user4"]
	    
	    }
    
    ]


## GET /get_orders_uid

Fetches orders by user ID.
### Query Parameters

uid: string - The user ID.

### Responses

200 OK: Returns all orders associated with the specified user ID.

  
  
  

    {
    
    "AAPL": {
    
    "buy_orders": [150, 200],
    
    "sell_orders": [-100, -50]
    
    }
    
    }


## POST /cancel_order

Cancels a specific order for a user.

  

### Request Body

uid: string - The user ID.

ticker: string - The ticker symbol.

ordertype: int - Type of order (1 for buy, 2 for sell).

val: int - Value of the order to be canceled.

  

      
    
    {
    
	    "uid": "user123",
	    
	    "ticker": "AAPL",
	    
	    "ordertype": 1,
	    
	    "val": 150
    
    }

Responses

200 OK: Returns a message indicating successful cancellation.

  
  
  

    {
    
	    "message": "Order canceled successfully"
    
    }


Errors

Errors are returned as standard HTTP status codes along with a detailed message. For internal server errors, a detailed description of the error is returned.

  

Development

To run the API server locally, use the following command:
`python3 api.py`

Ensure that all dependencies are installed and the environment variables are set correctly before starting the server.
