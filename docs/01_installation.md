# 설치 가이드

이 문서에서는 FastAPI 보일러플레이트 프로젝트와 Next.js 프론트엔드를 설치하고 실행하는 방법을 설명합니다.

## 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [프로젝트 설치](#프로젝트-설치)
3. [데이터베이스 설정](#데이터베이스-설정)
4. [백엔드 서버 실행](#백엔드-서버-실행)
5. [프론트엔드 설치 및 실행](#프론트엔드-설치-및-실행)
6. [Docker로 실행](#docker로-실행)

---

## 시스템 요구사항

### 백엔드 필수 사항

- **Python**: 3.10 이상
- **pip**: 최신 버전 권장
- **데이터베이스**: PostgreSQL, MySQL, MariaDB, 또는 SQLite

### 프론트엔드 필수 사항

- **Node.js**: 18.0 이상
- **npm**: 9.0 이상 (또는 yarn, pnpm)

### 선택 사항

- **Docker**: 컨테이너 기반 실행 시
- **Git**: 버전 관리

---

## 프로젝트 설치

### 1. 저장소 클론

```bash
git clone <repository-url>
cd vibe_saas_front_react
```

### 2. 가상환경 생성

가상환경을 사용하여 의존성을 격리합니다.

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일 편집 (자신의 환경에 맞게 수정)
nano .env  # 또는 원하는 편집기 사용
```

---

## 데이터베이스 설정

### PostgreSQL (기본 권장)

#### 설치

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# https://www.postgresql.org/download/windows/ 에서 다운로드
```

#### 데이터베이스 생성

```bash
# PostgreSQL에 접속
sudo -u postgres psql

# 데이터베이스 및 사용자 생성
CREATE USER fastapi_user WITH PASSWORD 'your_password';
CREATE DATABASE fastapi_db OWNER fastapi_user;
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
\q
```

#### .env 설정

```env
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=fastapi_user
DB_PASSWORD=your_password
DB_NAME=fastapi_db
```

### MySQL/MariaDB

#### 설치

```bash
# Ubuntu/Debian
sudo apt install mysql-server
# 또는
sudo apt install mariadb-server

# macOS (Homebrew)
brew install mysql
# 또는
brew install mariadb
```

#### 데이터베이스 생성

```bash
# MySQL에 접속
mysql -u root -p

# 데이터베이스 및 사용자 생성
CREATE DATABASE fastapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'fastapi_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON fastapi_db.* TO 'fastapi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### .env 설정

```env
DB_TYPE=mysql  # 또는 mariadb
DB_HOST=localhost
DB_PORT=3306
DB_USER=fastapi_user
DB_PASSWORD=your_password
DB_NAME=fastapi_db
```

### SQLite (개발용)

SQLite는 별도 설치 없이 사용할 수 있습니다.

#### .env 설정

```env
DB_TYPE=sqlite
SQLITE_FILE=./data/app.db
```

`data` 디렉토리는 자동으로 생성됩니다.

---

## 백엔드 서버 실행

### 개발 서버

```bash
# 기본 실행 (핫 리로드 활성화)
uvicorn app.main:app --reload

# 특정 포트 지정
uvicorn app.main:app --reload --port 8080

# 모든 인터페이스에서 접속 허용
uvicorn app.main:app --reload --host 0.0.0.0

# 워커 수 지정 (프로덕션)
uvicorn app.main:app --workers 4
```

### 프로덕션 서버

프로덕션 환경에서는 Gunicorn과 함께 사용하는 것을 권장합니다.

```bash
# Gunicorn 설치
pip install gunicorn

# 실행
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 서버 확인

서버 실행 후 다음 URL에서 확인할 수 있습니다:

- **API 루트**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

---

## 프론트엔드 설치 및 실행

### 1. 프론트엔드 디렉토리 이동

```bash
cd frontend
```

### 2. 의존성 설치

```bash
npm install
```

### 3. 환경 변수 설정 (선택)

백엔드 서버가 `http://localhost:8000`이 아닌 경우, `.env.local` 파일을 생성합니다:

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://your-backend-url:8000
```

### 4. 개발 서버 실행

```bash
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

### 5. 프로덕션 빌드

```bash
# 빌드
npm run build

# 프로덕션 서버 실행
npm start
```

### 프론트엔드 기술 스택

- **Next.js 16**: React 프레임워크 (App Router)
- **React 19**: UI 라이브러리
- **TypeScript 5**: 타입 안전성
- **Tailwind CSS 4**: 유틸리티 CSS
- **shadcn/ui**: UI 컴포넌트 (Radix UI 기반)
- **Zustand 5**: 상태 관리
- **React Hook Form + Zod**: 폼 및 유효성 검사

---

## Docker로 실행

### Dockerfile 생성

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml 생성

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_TYPE=postgresql
      - DB_HOST=db
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_NAME=fastapi_db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Docker 실행

```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 다음 단계

설치가 완료되면 다음 문서를 참조하세요:

- [환경 설정](02_configuration.md): 상세 설정 옵션
- [사용 가이드](03_usage.md): API 사용 방법
- [API 레퍼런스](04_api_reference.md): 전체 API 문서
