"""
Database Schemas for Wedding Planner App

Each Pydantic model represents a collection in MongoDB. The collection name
is the lowercase of the class name (e.g., Planner -> "planner").
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class PackageOption(BaseModel):
    name: str = Field(..., description="Package name, e.g., 'Classic', 'Premium'")
    price: float = Field(..., ge=0, description="Package price in USD")
    features: List[str] = Field(default_factory=list, description="Included features")


class Planner(BaseModel):
    name: str = Field(..., description="Business or planner name")
    tagline: Optional[str] = Field(None, description="Short value proposition")
    location: str = Field(..., description="City/Region")
    rating: float = Field(5.0, ge=0, le=5, description="Average rating out of 5")
    reviews_count: int = Field(0, ge=0, description="Number of reviews")
    specialties: List[str] = Field(default_factory=list, description="Wedding styles and services")
    image_url: Optional[str] = Field(None, description="Cover image URL")
    packages: List[PackageOption] = Field(default_factory=list, description="Available packages")
    instagram: Optional[str] = Field(None, description="Instagram handle or URL")
    website: Optional[str] = Field(None, description="Company website")


class Inquiry(BaseModel):
    planner_id: Optional[str] = Field(None, description="Target planner ID (optional)")
    name: str = Field(..., description="Couple's name")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Phone number")
    event_date: Optional[str] = Field(None, description="Planned wedding date (YYYY-MM-DD)")
    guest_count: Optional[int] = Field(None, ge=0, description="Estimated guests")
    message: Optional[str] = Field(None, description="Brief about the vision/budget")
