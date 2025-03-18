# FastAPI RESTful API Template

FastAPI 기반의 확장 가능한 RESTful API 템플릿 프로젝트입니다. 현대적인 Python 웹 애플리케이션 개발에 필요한 다양한 기능을 모듈화하여 제공합니다.

## 🚀 주요 특징

- 📦 **모듈형 설계**: 재사용 가능한 컴포넌트 기반
- 🔐 **보안 기능**: JWT 인증, Rate Limiting, 데이터 암호화
- 🎯 **개발 효율**: CRUD 보일러플레이트, 자동 문서화
- 🔄 **고성능**: 비동기 지원, Redis 캐싱
- 🐳 **손쉬운 배포**: Docker 기반 개발/배포 환경

## 🛠 기술 스택

- **핵심**: FastAPI, SQLAlchemy, Pydantic, async/await
- **데이터**: PostgreSQL, Redis
- **배포**: Docker, Docker Compose

## ⚡️ 빠른 시작

```bash
# 저장소 클론 및 설정
git clone https://github.com/yourusername/fastapi-template.git
cd fastapi_template
cp .env.example .env

# 실행
docker-compose up -d
```

상세한 설정 및 실행 방법은 [기술 문서](fastapi_template/README.md)를 참조하세요.

## 📚 문서

- **API 문서**: <http://localhost:8000/docs> (서버 실행 시)
- **상세 문서**: [기술 문서](fastapi_template/README.md)
- **아키텍처**: [아키텍처 설계](fastapi_template/docs/architecture.md)
- **모듈 문서**: [공통 모듈 문서](fastapi_template/docs/common_modules.md)
- **개발 가이드**: [개발 계획](fastapi_template/docs/development_plan.md)
- **테스트 가이드**: [테스트 작성/실행](fastapi_template/docs/testing_guide.md)

## 🤝 기여 및 지원

- ⭐ **스타**: 저장소에 스타를 눌러주세요!
- 🔄 **공유**: 동료, 친구, SNS에 이 프로젝트를 공유해주세요.
- 💬 **피드백**: 이슈를 통해 개선점이나 아이디어를 제안해주세요.
- 👥 **협업**: 함께 일하고 싶으시다면 이메일(<devramyun@gmail.com>)로 연락주세요!

## 📄 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
