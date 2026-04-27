from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from db import get_search_results, connect_to_db, close_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await connect_to_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/api/Items/search")
async def search(
    q: Optional[str] = Query(None, min_length=1),
    tag_ids: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    try:
        filters = {"search": q}
        if tag_ids:
            # Convert comma-separated string to a list of ints
            filters["tag_ids"] = [int(tid) for tid in tag_ids.split(",") if tid]
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        items = await get_search_results(filters)
        return items
    except Exception as error:
        print(f"Error searching knowledge items: {error}")
        raise HTTPException(status_code=500, detail="Failed to search knowledge items")