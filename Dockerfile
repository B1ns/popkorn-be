# Dockerfile
FROM python:3.12-slim

# 작업 디렉토리
WORKDIR /app

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치
RUN uv sync --frozen --no-dev

# 앱 코드 복사
COPY . . 

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]