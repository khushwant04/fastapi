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
    cursor.execute("""Select * from posts""")
    posts = cursor.fetchall()
    return {"data":posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES(%s,%s,%s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"message": new_post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute(f"""SELECT * FROM posts WHERE id = %s""",(str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} not found")
    return {"data": post}

@app.delete("/posts/{id}")
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s""",(str(id)))
    deleted_post = cursor.fetchone()
    # if index == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    # # my_posts.pop(index)
    return {'message':deleted_post}

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()
    return {"message": updated_post}

