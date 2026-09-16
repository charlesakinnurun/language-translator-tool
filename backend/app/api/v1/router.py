"""Aggregate router for all v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, translation

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(translation.router)