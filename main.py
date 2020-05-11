from fastapi import FastAPI, HTTPException, Response, status, Request, Query
import sqlite3
from pydantic import BaseModel

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


@app.get("/tracks/composers")
async def get_composer_tracks(response: Response, composer_name: str):
    cursor = app.db_connection.cursor()
    # extract data
    data = cursor.execute('''
    SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name
    ''', (composer_name, )).fetchall()
    if data == []:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Composer not found"}}
    return [item["Name"] for item in data]


class Album(BaseModel):
    title: str
    artist_id: int


@app.post("/albums", status_code=201)
async def add_albums(response: Response, album: Album):
    data = app.db_connection.execute('''
        SELECT Name FROM artists WHERE ArtistId = ?
        ''', (album.artist_id, )).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": f"Artist with id {album.artist_id} was not found"}}
    cursor = app.db_connection.execute('''
        INSERT INTO albums (Title, ArtistId) VALUES (?,?)
        ''', (album.title,album.artist_id))
    app.db_connection.commit()
    new_album_id = cursor.lastrowid
    return {"AlbumId": new_album_id, "Title": album.title, "ArtistId": album.artist_id}


@app.get("/albums/{album_id}")
async def get_album(response: Response, album_id: int):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.cursor()
    # extract data
    data = cursor.execute('''
    SELECT * FROM albums WHERE AlbumId = ?
    ''', (album_id, )).fetchone()
    if data == None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Album not found"}}
    return data

class UpdateCustomer(BaseModel):
    company: str
    address: str
    city: str
    state: str
    country: str
    postalcode: str
    fax: str

@app.put("/customers/{customer_id}")
async def update_customer(response: Response, customer_id: int, update: UpdateCustomer):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
        SELECT * FROM customers WHERE CustomerId = ?
        ''', (customer_id, )).fetchone()
    if data is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": f"Customer with id {customer_id} was not found"}}
    return data
    #TODO: tutaj dokonczyć


@app.get("/sales")
async def get_sales(response: Response, category: str = Query("customers")):
    column = category.capitalize()
    if column == "Postalcode":
        column = "PostalCode"

    if category == "customers":
        app.db_connection.row_factory = sqlite3.Row
        data = app.db_connection.execute('''
            SELECT customers.*, round(sum(invoices.total),2) AS SumTotal FROM customers 
            LEFT JOIN invoices ON customers.CustomerId = invoices.CustomerId
            GROUP BY customers.CustomerId
            ORDER BY SumTotal
            ''').fetchall()
        return data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": f"Data for summary was not found"}}

    



# new_artist_id = cursor.lastrowid
# artist = app.db_connection.execute(

# )
