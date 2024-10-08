from json import load
from pyexpat import model
from typing import Optional
from fastapi import Depends, FastAPI , Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import time

from sqlalchemy.orm import Session
from . import models , schemas
from .db import engine
from .db import get_db


models.Base.metadata.create_all(bind=engine)

# Load environment variables from .env file
load_dotenv()

# Get the credentials from environment variables
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")


app = FastAPI()

@app.get("/")
def index():
    return {"Message":"Server is running.."}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""Select * from posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data":posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES(%s,%s,%s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute(f"""SELECT * FROM posts WHERE id = %s""",(str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with {id} not found")
    
    return {"data": post}

@app.delete("/posts/{id}")
def delete_post(id: int,  db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s""",(str(id)))
    # deleted_post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")


    post.delete(synchronize_session=False)
    db.commit()
    return {'message':"deleted_post"}


@app.put("/posts/{id}")
def update_post(id: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} does not exist")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return {"message": post_query.first()}

