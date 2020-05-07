from fastapi import FastAPI, HTTPException, Response, status
import sqlite3

app = FastAPI()


# Connect to DB
@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')
    app.db_connection.row_factory = sqlite3.Row

@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/tracks", status_code=200)
async def get_tracks(page=0, per_page=10):
    # start cursor
    cursor = app.db_connection.cursor()
    # calculate offset
    offset = str(int(page)*int(per_page))
    # extract data
    data = cursor.execute('''
    SELECT * FROM tracks LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    return data


@app.get("/tracks/composers")
async def get_composer_tracks(response: Response, composer_name: str):
    cursor = app.db_connection.cursor()
    # extract data
    data = cursor.execute('''
    SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name
    ''', (composer_name, )).fetchall()
    if data == []:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail":{"error":"Composer not found"}}
    return [item["Name"] for item in data]