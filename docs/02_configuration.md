# 환경 설정 가이드

이 문서에서는 프로젝트의 모든 설정 옵션을 설명합니다.

## 목차

1. [환경 변수 개요](#환경-변수-개요)
2. [애플리케이션 설정](#애플리케이션-설정)
3. [데이터베이스 설정](#데이터베이스-설정)
4. [인증 설정](#인증-설정)
5. [CORS 설정](#cors-설정)
6. [테마 설정](#테마-설정)

---

## 환경 변수 개요

모든 설정은 `.env` 파일 또는 환경 변수로 관리됩니다.

### 설정 파일 위치

```
FastAPI_Tutorial/
├── .env              # 실제 설정 (git에 포함되지 않음)
├── .env.example      # 설정 템플릿
└── app/
    └── config.py     # 설정 로드 및 검증
```

### 설정 로드 방식

설정은 `app/config.py`의 `Settings` 클래스를 통해 로드됩니다:

```python
from app.config import settings

# 설정 사용 예시
print(settings.app_name)
print(settings.database_url)
```

---

## 애플리케이션 설정

### 기본 설정

```env
# 애플리케이션 이름 (API 문서에 표시)
APP_NAME="FastAPI Boilerplate"

# 버전
APP_VERSION="1.0.0"

# 디버그 모드 (개발: true, 프로덕션: false)
DEBUG=true

# 비밀 키 (세션, CSRF 등에 사용)
# 프로덕션에서는 반드시 변경하세요!
SECRET_KEY="your-secret-key-change-this-in-production"
```

### 디버그 모드 영향

| 기능 | DEBUG=true | DEBUG=false |
|------|------------|-------------|
| SQL 로깅 | 활성화 | 비활성화 |
| 상세 에러 | 표시 | 숨김 |
| 핫 리로드 | 자동 | 수동 |

### SECRET_KEY 생성

```python
# Python으로 안전한 키 생성
import secrets
print(secrets.token_urlsafe(32))
```

또는 명령줄에서:

```bash
openssl rand -hex 32
```

---

## 데이터베이스 설정

### 데이터베이스 유형 선택

```env
# 지원 유형: postgresql, mysql, mariadb, sqlite
DB_TYPE=postgresql
```

### PostgreSQL 설정

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=fastapi_db
```

생성되는 URL: `postgresql://postgres:password@localhost:5432/fastapi_db`

### MySQL/MariaDB 설정

```env
DB_TYPE=mysql  # 또는 mariadb
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=fastapi_db
```

생성되는 URL: `mysql+pymysql://root:password@localhost:3306/fastapi_db`

### SQLite 설정

```env
DB_TYPE=sqlite
SQLITE_FILE=./data/app.db
```

생성되는 URL: `sqlite:///./data/app.db`

### 연결 풀 설정 (코드 내)

```python
# app/database.py에서 설정
engine = create_engine(
    database_url,
    pool_pre_ping=True,   # 연결 유효성 검사
    pool_size=10,         # 기본 연결 수
    max_overflow=20,      # 추가 연결 최대 수
)
```

---

## 인증 설정

### JWT 설정

```env
# JWT 서명에 사용되는 비밀 키
# 프로덕션에서는 반드시 변경하세요!
JWT_SECRET_KEY="your-jwt-secret-key-change-this"

# 서명 알고리즘
JWT_ALGORITHM=HS256

# 액세스 토큰 만료 시간 (분)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 리프레시 토큰 만료 시간 (일)
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 토큰 만료 시간 권장값

| 환경 | 액세스 토큰 | 리프레시 토큰 |
|------|-------------|---------------|
| 개발 | 60분 | 30일 |
| 프로덕션 | 15-30분 | 7일 |
| 고보안 | 5-15분 | 1일 |

### 사용자 역할

시스템에서 지원하는 역할:

```python
class UserRole(str, Enum):
    ADMIN = "admin"          # 전체 권한
    MODERATOR = "moderator"  # 컨텐츠 관리 권한
    USER = "user"            # 일반 사용자
```

---

## CORS 설정

### 기본 설정

```env
# 허용된 오리진 (JSON 배열 형식)
# 개발 환경에서는 ["*"]를 사용하여 모든 오리진 허용 (기본값)
CORS_ORIGINS=["*"]

# 자격 증명 허용 (쿠키, Authorization 헤더 등)
CORS_ALLOW_CREDENTIALS=true

# 허용된 HTTP 메서드
CORS_ALLOW_METHODS=["*"]

# 허용된 헤더
CORS_ALLOW_HEADERS=["*"]
```

### 모든 오리진 허용 (개발 환경)

`CORS_ORIGINS=["*"]`로 설정하면 모든 오리진에서의 접속을 허용합니다.
이 설정은 내부적으로 `allow_origin_regex=r".*"`를 사용하여 `allow_credentials=true`와 함께 동작합니다.

```env
# 개발 환경: 모든 오리진 허용
CORS_ORIGINS=["*"]
```

이 설정을 사용하면:
- `http://localhost:3000` (로컬 개발)
- `http://192.168.0.x:3000` (같은 네트워크의 다른 PC)
- 기타 모든 오리진에서 접속 가능

### 프로덕션 설정 예시

```env
# 특정 도메인만 허용
CORS_ORIGINS=["https://myapp.com","https://admin.myapp.com"]

# 특정 메서드만 허용
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE"]

# 특정 헤더만 허용
CORS_ALLOW_HEADERS=["Authorization","Content-Type"]
```

### CORS 관련 주의사항

1. **개발 환경**: `["*"]` 사용으로 편리하게 개발 (내부적으로 `allow_origin_regex` 사용)
2. **프로덕션 환경**: 보안을 위해 구체적인 도메인 지정 권장
3. **프리플라이트 캐시**: 복잡한 요청의 경우 OPTIONS 요청 발생

### 외부 IP 접속 설정

같은 네트워크의 다른 PC에서 접속하려면:

1. **백엔드**: 모든 네트워크 인터페이스에서 수신하도록 실행
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0
   ```

2. **프론트엔드**: 기본적으로 동적 API URL을 사용하여 현재 접속한 호스트의 8000 포트로 연결
   - `NEXT_PUBLIC_API_URL` 환경변수가 없으면 브라우저의 현재 호스트명 기반으로 자동 설정
   - 예: `http://192.168.0.8:3000`으로 접속 시 API는 `http://192.168.0.8:8000`으로 연결

---

## 테마 설정

### 테마 옵션

```env
# 기본 테마
DEFAULT_THEME=light

# 사용 가능한 테마 목록
AVAILABLE_THEMES=["light","dark","blue","green"]
```

### 테마 커스터마이징

사용자별 테마 설정은 `user_themes` 테이블에 저장됩니다:

```python
# UserTheme 모델 필드
{
    "theme_name": "dark",           # 테마 이름
    "sidebar_collapsed": false,     # 사이드바 상태
    "custom_settings": {            # 확장 설정 (JSON)
        "font_size": "medium",
        "language": "ko"
    }
}
```

---

## 설정 검증

설정이 올바르게 로드되었는지 확인:

```python
# Python 셸에서 확인
from app.config import settings

print(f"앱 이름: {settings.app_name}")
print(f"DB 타입: {settings.db_type}")
print(f"DB URL: {settings.database_url}")
print(f"디버그: {settings.debug}")
```

또는 서버 시작 시 로그 확인:

```
🚀 FastAPI Boilerplate v1.0.0 시작...
📦 데이터베이스: postgresql
🔧 디버그 모드: True
✅ 데이터베이스 테이블 생성 완료
```

---

## 환경별 설정 관리

### 개발 환경 (.env.development)

```env
DEBUG=true
DB_TYPE=sqlite
SQLITE_FILE=./data/dev.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 테스트 환경 (.env.test)

```env
DEBUG=true
DB_TYPE=sqlite
SQLITE_FILE=:memory:
```

### 프로덕션 환경 (.env.production)

```env
DEBUG=false
DB_TYPE=postgresql
DB_HOST=production-db-host
SECRET_KEY=very-long-and-secure-key
JWT_SECRET_KEY=another-very-secure-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

---

## 다음 단계

- [사용 가이드](03_usage.md): API 사용 방법
- [API 레퍼런스](04_api_reference.md): 전체 API 문서
