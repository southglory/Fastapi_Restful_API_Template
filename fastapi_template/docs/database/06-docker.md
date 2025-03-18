# Docker 환경 설정

이 문서는 FastAPI 프로젝트에서 Docker를 사용한 개발 및 배포 환경 설정 방법을 설명합니다.

## 목차

1. [Docker 소개](#docker-소개)
2. [Dockerfile](#dockerfile)
3. [Docker Compose](#docker-compose)
4. [개발 환경 설정](#개발-환경-설정)
5. [배포 환경 설정](#배포-환경-설정)

## Docker 소개

Docker는 애플리케이션을 개발, 배포, 실행하기 위한 오픈 플랫폼입니다. Docker를 사용하면 애플리케이션을 인프라에서 분리하여 소프트웨어를 빠르게 제공할 수 있습니다.

주요 장점:

- 일관된 환경 제공
- 의존성 관리 간소화
- 배포 프로세스 표준화
- 확장성 및 이식성 향상

## Dockerfile

`Dockerfile`은 Docker 이미지를 빌드하기 위한 지침을 포함하는 텍스트 파일입니다.

### FastAPI 애플리케이션을 위한 Dockerfile

프로젝트 루트 디렉토리에 `Dockerfile`을 생성합니다:

```dockerfile
# 베이스 이미지 선택
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose

`docker-compose.yml` 파일은 여러 Docker 컨테이너를 정의하고 구성하는 YAML 파일입니다.

### FastAPI, PostgreSQL, Redis를 위한 Docker Compose 설정

프로젝트 루트 디렉토리에 `docker-compose.yml`을 생성합니다:

```yaml
services:
  # PostgreSQL 서비스
  postgres:
    image: postgres:15
    container_name: fastapi_postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - fastapi_network

  # Redis 서비스
  redis:
    image: redis:7
    container_name: fastapi_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - fastapi_network

  # FastAPI 애플리케이션
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fastapi_app
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/fastapi_db
      - REDIS_URL=redis://redis:6379/0
    networks:
      - fastapi_network

networks:
  fastapi_network:

volumes:
  postgres_data:
  redis_data:
```

## 개발 환경 설정

### 개발 환경에서 Docker Compose 실행

개발 환경에서는 코드 변경 사항을 실시간으로 반영하기 위해 볼륨 마운트를 사용합니다:

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스만 시작
docker-compose up -d postgres redis
```

### 개발 환경에서 데이터베이스 마이그레이션

Docker 컨테이너 내에서 Alembic 마이그레이션을 실행합니다:

```bash
# 컨테이너에 접속
docker-compose exec app bash

# 마이그레이션 실행
alembic upgrade head
```

## 배포 환경 설정

### 프로덕션용 Docker Compose 설정

프로덕션 환경을 위한 별도의 Docker Compose 파일을 생성합니다:

```yaml
# docker-compose.prod.yml
services:
  postgres:
    image: postgres:15
    # 프로덕션 설정...
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    # 프로덕션 설정...
    restart: always
    volumes:
      - redis_prod_data:/data

  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    # 프로덕션 설정...

volumes:
  postgres_prod_data:
  redis_prod_data:
```

### 프로덕션용 Dockerfile

프로덕션 환경을 위한 최적화된 Dockerfile을 생성합니다:

```dockerfile
# Dockerfile.prod
FROM python:3.12-slim AS builder

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 최종 이미지
FROM python:3.12-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 빌더 스테이지에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--workers", "4"]
```

### 프로덕션 환경 배포

프로덕션 환경에서 Docker Compose를 사용하여 애플리케이션을 배포합니다:

```bash
# 환경 변수 파일 사용
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 환경 변수 관리

Docker 환경에서 환경 변수를 관리하는 방법:

### 개발 환경

`.env` 파일을 사용하여 개발 환경의 환경 변수를 설정합니다:

```env
# .env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/fastapi_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=dev_secret_key
```

### 프로덕션 환경

프로덕션 환경을 위한 별도의 환경 변수 파일을 생성합니다:

```env
# .env.prod
DATABASE_URL=postgresql://user:password@db.example.com:5432/fastapi_db
REDIS_URL=redis://redis.example.com:6379/0
SECRET_KEY=your_production_secret_key
```

## 데이터 지속성

Docker 볼륨을 사용하여 데이터를 지속적으로 저장합니다:

```yaml
volumes:
  postgres_data:  # PostgreSQL 데이터 저장
  redis_data:     # Redis 데이터 저장
```

이렇게 하면 컨테이너가 재시작되거나 삭제되어도 데이터가 유지됩니다.

## 다음 단계

이제 FastAPI 프로젝트에서 데이터베이스 통합에 대한 모든 문서를 완료했습니다. 이 문서들을 참고하여 프로젝트를 구성하고 개발할 수 있습니다.
