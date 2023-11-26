#Imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import StrictRedis
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os

#App usage
app = FastAPI()
load_dotenv()

#Redis connection
redis = StrictRedis(
    host=os.getenv('redis_host'),
    port=os.getenv('redis_port'),
    password=os.getenv('redis_password'),
    decode_responses=True
)

#Cors connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8000'],
    allow_methods=['*'],
    allow_headers=['*']
)

#Model
class Product(BaseModel):
    name: str
    price: int
    quantity: int

'''
Api usage
'''
@app.get("/")
def read_root():
    return {"hello": "world"}

@app.post("/products", response_model=Product)
def create_product(product: Product):
    try:
        # Store product data in Redis
        redis.hmset(f"product:{product.name}", {"name": product.name, "price": product.price, "quantity": product.quantity})
        return product
    except Exception as e:
        return {"failed"}

@app.get("/products", response_model=List[Product])
def read_products():
    try:
        # Retrieve product data from Redis
        keys = redis.keys("product:*")
        products = [Product(**redis.hgetall(key)) for key in keys]
        return products
    except Exception as e:
        return {"failed"}

