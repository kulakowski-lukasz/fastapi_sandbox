from fastapi import FastAPI
import sqlite3

app = FastAPI()


# Connect to DB
@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/tracks", status_code=200)
async def get_tracks(page=0, per_page=10):
    # map responses to dicts
    app.db_connection.row_factory = sqlite3.Row
    # start cursor
    cursor = app.db_connection.cursor()
    # calculate offset
    offset = str(int(page)*int(per_page))
    # extract data
    data = cursor.execute('''
    SELECT * FROM tracks LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    return data
