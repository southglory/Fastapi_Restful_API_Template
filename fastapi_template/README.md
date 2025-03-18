# FastAPI RESTful API 기술 문서

이 문서는 FastAPI 템플릿의 상세 기술 명세와 구현 가이드를 제공합니다.

## 📚 관련 문서

- **아키텍처**: [아키텍처 설계](./docs/architecture.md)
- **모듈 문서**: [공통 모듈 문서](./docs/common_modules.md)
- **개발 가이드**: [개발 계획](./docs/development_plan.md)
- **테스트 가이드**: [테스트 작성/실행](./docs/testing_guide.md)
- **API 문서**: 서버 실행 후 <http://localhost:8000/docs> 접속

## 🏗 아키텍처

### 계층형 아키텍처

```
프레젠테이션 계층 (API Layer)
    │
서비스 계층 (Business Layer)
    │
데이터 계층 (Data Layer)
```

### 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, Pydantic
- **데이터베이스**: PostgreSQL, Redis
- **개발 도구**: Docker, JWT

## 📁 모듈 구조

프로젝트의 상세한 디렉토리 구조는 [py_project_tree.txt](./py_project_tree.txt)를 참조하세요.

주요 디렉토리에 대한 설명은 [공통 모듈 문서](./docs/common_modules.md)에서 확인하세요.

## 라이센스

MIT
