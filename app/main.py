from json import load
from typing import Optional
from fastapi import FastAPI , Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# Get the credentials from environment variables
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


app = FastAPI()


class Post(BaseModel):
    title: str 
    content: str
    published: bool = True 
    rating: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Database connection was successfull") 
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)


my_posts = [
    {"title":"title of post 1", "content":"content of post 1", "id":1},
    {"fav foods":"Bhindi", "Content":"I like Bhindi", "id":2}
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i



@app.get("/")
def index():
    return {"Message":"Server is running.."}


@app.get("/posts")
def get_posts():
    return {"data":my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0,1000000)
    my_posts.append(post_dict)
    return {"message": post_dict}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} not found")
    return {"data": post}

@app.delete("/posts/{id}")
def delete_post(id: int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    my_posts.pop(index)
    return {'message':"Post was deleted"}

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"message": "Updated Post"}

