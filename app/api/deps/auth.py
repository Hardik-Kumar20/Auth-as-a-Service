from fastapi import Depends, HttpException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asycio import AsyncSession
from sqlalchemy.future import select

from db import get_db
from db.models.user import User
from app.core.security import decode_access_token


