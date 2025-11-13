from fastapi import APIRouter, Depends
from app.schemas import UserSchema
from app.services import auth_service
from app.api.deps import get
