# app/auth/service.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.repository import UserRepository
from app.auth.schemas import UserSignup, UserLogin
from app.core.security import(
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)
        
    
    async def signup(self, data: UserSignup) -> User:
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
        
        
        return create_access_token(str(user.id))