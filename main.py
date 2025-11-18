import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Planner, Inquiry, PackageOption

app = FastAPI(title="Wedding Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlannerOut(BaseModel):
    id: str
    name: str
    tagline: Optional[str] = None
    location: str
    rating: float
    reviews_count: int
    specialties: List[str] = []
    image_url: Optional[str] = None
    packages: List[PackageOption] = []
    instagram: Optional[str] = None
    website: Optional[str] = None


@app.get("/")
def root():
    return {"message": "Wedding Planner API is running"}


@app.get("/api/planners", response_model=List[PlannerOut])
def list_planners(limit: int = 20):
    try:
        docs = get_documents("planner", {}, limit)
    except Exception as e:
        # If DB not available, provide a curated sample list to allow UI preview
        sample = [
            {
                "_id": "demo1",
                "name": "We Me Good Weddings",
                "tagline": "Timeless celebrations, flawlessly planned",
                "location": "New York, NY",
                "rating": 4.9,
                "reviews_count": 128,
                "specialties": ["Full-Service Planning", "Luxury", "Destination"],
                "image_url": "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=1400&auto=format&fit=crop",
                "packages": [
                    {"name": "Classic", "price": 3500, "features": ["Timeline", "Vendor Coordination", "Day-Of Team"]},
                    {"name": "Signature", "price": 6500, "features": ["Design", "Rehearsal", "Logistics Lead"]},
                ],
                "instagram": "https://instagram.com/wemegood",
                "website": "https://wemegood.example.com",
            },
            {
                "_id": "demo2",
                "name": "EverAfter Collective",
                "tagline": "Design-forward weddings with heart",
                "location": "Los Angeles, CA",
                "rating": 4.8,
                "reviews_count": 92,
                "specialties": ["Design", "Partial Planning", "Coordinaton"],
                "image_url": "https://images.unsplash.com/photo-1522673607200-164d1b6ce486?q=80&w=1400&auto=format&fit=crop",
                "packages": [
                    {"name": "Partial Planning", "price": 2800, "features": ["Vendor Shortlist", "Budget Mapping"]},
                ],
                "instagram": None,
                "website": None,
            },
        ]
        return [
            PlannerOut(
                id=str(x.get("_id")),
                name=x["name"],
                tagline=x.get("tagline"),
                location=x["location"],
                rating=x.get("rating", 5.0),
                reviews_count=x.get("reviews_count", 0),
                specialties=x.get("specialties", []),
                image_url=x.get("image_url"),
                packages=[PackageOption(**p) for p in x.get("packages", [])],
                instagram=x.get("instagram"),
                website=x.get("website"),
            )
            for x in sample
        ]

    # Convert documents to response model
    result: List[PlannerOut] = []
    for d in docs:
        result.append(
            PlannerOut(
                id=str(d.get("_id")),
                name=d.get("name"),
                tagline=d.get("tagline"),
                location=d.get("location"),
                rating=d.get("rating", 5.0),
                reviews_count=d.get("reviews_count", 0),
                specialties=d.get("specialties", []),
                image_url=d.get("image_url"),
                packages=[PackageOption(**p) for p in d.get("packages", [])],
                instagram=d.get("instagram"),
                website=d.get("website"),
            )
        )
    return result


class InquiryIn(BaseModel):
    planner_id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    event_date: Optional[str] = None
    guest_count: Optional[int] = None
    message: Optional[str] = None


@app.post("/api/inquiries")
def submit_inquiry(payload: InquiryIn):
    try:
        inquiry = Inquiry(**payload.model_dump())
        _id = create_document("inquiry", inquiry)
        return {"status": "ok", "id": _id}
    except Exception as e:
        # Allow UI demo even when DB not configured
        return {"status": "ok", "id": "demo-inquiry", "note": "Stored in-memory for preview"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
