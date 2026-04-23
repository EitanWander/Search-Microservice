from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from db import get_search_results, connect_to_db, close_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await connect_to_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/Items/search")
async def search(
    q: str = Query(..., min_length=1),
    tag_ids: Optional[str] = Query(None)
):
    try:
        filters = {"search": q}
        if tag_ids:
            # Convert comma-separated string to a list of ints
            filters["tag_ids"] = [int(tid) for tid in tag_ids.split(",") if tid]
        items = await get_search_results(filters)
        return items
    except Exception as error:
        print(f"Error searching knowledge items: {error}")
        raise HTTPException(status_code=500, detail="Failed to search knowledge items")