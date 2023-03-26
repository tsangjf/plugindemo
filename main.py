import json
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class Book(BaseModel):
    title: str

books: Dict[str, Book] = {}

@app.get("/books", response_model=List[Book])
async def list_books():
    return list(books.values())

@app.post("/books")
async def add_book(book: Book):
    book_id = str(len(books) + 1)
    books[book_id] = book
    return {"id": book_id}

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    return books[book_id]

@app.put("/books/{book_id}")
async def rename_book(book_id: str, book: Book):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    books[book_id] = book
    return {"id": book_id}

@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    if book_id not in books:
        raise HTTPException(status_code=404, detail="Book not found")
    del books[book_id]
    return {"id": book_id}

@app.get("/.mybook/book-plugin.json", include_in_schema=False)
async def serve_manifest():
    with open("manifest.json") as f:
        manifest_data = json.load(f)
    return JSONResponse(content=manifest_data)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Books API",
        version="1.0.0",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

