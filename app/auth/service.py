# app/auth/service.py
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.repository import UserRepository
from app.auth.schemas import UserRegister, UserLogin, Token, AccessToken
from app.core.security import(
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)
        
    
    async def register(self, data: UserRegister) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing is not None:
            raise ValueError("이미 가입된 이메일입니다.")
        
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
        )
        created = await self.repo.create(user)
        await self.session.commit()
        return created
    
    
    async def login(self, data: UserLogin) -> str:
        user = await self.repo.get_by_email(data.email)
        if user is None:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        if not verify_password(data.password, user.hashed_password):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")
        
        return Token(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )
        
    async def refresh(self, refresh_token: str) -> AccessToken:
        user_id = decode_refresh_token(refresh_token)
        if user_id is None:
            raise ValueError("유효하지 않거나 만료된 토큰입니다.")
        user = await self.repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise ValueError("유효하지 않거나 만료된 토큰입니다.")
        
        return AccessToken(access_token=create_access_token(str(user.id)))
    
    
    async def get_user_by_id(self, user_id: str) -> User | None:
        return await self.repo.get_by_id(uuid.UUID(user_id))