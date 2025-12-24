# Python 기초 문법

## 개요

FastAPI를 이해하기 위해 필요한 Python 기초 문법을 설명합니다. 프로그래밍 경험이 없어도 이해할 수 있도록 각 개념을 자세히 설명합니다.

## 1. 변수와 데이터 타입

### 변수 선언

Python에서는 변수를 선언할 때 타입을 명시하지 않아도 됩니다.

```python
# 변수 선언
name = "홍길동"           # 문자열 (str)
age = 25                 # 정수 (int)
height = 175.5           # 실수 (float)
is_active = True         # 불리언 (bool)

# Python은 변수 타입을 자동으로 추론합니다
print(type(name))    # <class 'str'>
print(type(age))     # <class 'int'>
```

### 타입 힌트 (Type Hints)

FastAPI에서는 **타입 힌트**를 많이 사용합니다. 이는 변수의 타입을 명시적으로 표시합니다.

```python
# 타입 힌트 없이
name = "홍길동"

# 타입 힌트 사용 (권장)
name: str = "홍길동"
age: int = 25
height: float = 175.5
is_active: bool = True

# 타입 힌트는 "문서화" 역할을 합니다
# 실제로 강제되지는 않지만, 코드를 이해하기 쉽게 만듭니다
```

### 기본 데이터 타입

```python
# 1. 문자열 (str)
name: str = "Hello"
message: str = 'World'
multiline: str = """
    여러 줄
    문자열
"""

# 문자열 포맷팅 (f-string) - FastAPI에서 자주 사용
user = "홍길동"
greeting = f"안녕하세요, {user}님!"  # "안녕하세요, 홍길동님!"

# 2. 숫자
integer_num: int = 42
float_num: float = 3.14

# 3. 불리언
is_valid: bool = True
is_empty: bool = False

# 4. None (값이 없음)
result: None = None

# 5. 리스트 (list) - 여러 값을 순서대로 저장
numbers: list = [1, 2, 3, 4, 5]
names: list = ["Alice", "Bob", "Charlie"]

# 6. 딕셔너리 (dict) - 키-값 쌍으로 저장
user: dict = {
    "name": "홍길동",
    "age": 25,
    "email": "hong@example.com"
}
print(user["name"])  # "홍길동"

# 7. 튜플 (tuple) - 변경 불가능한 리스트
coordinates: tuple = (10, 20)
```

## 2. 함수 (Functions)

### 기본 함수

```python
# 기본 함수 정의
def greet():
    print("안녕하세요!")

# 함수 호출
greet()  # "안녕하세요!"
```

### 매개변수와 반환값

```python
# 매개변수가 있는 함수
def greet(name):
    print(f"안녕하세요, {name}님!")

greet("홍길동")  # "안녕하세요, 홍길동님!"

# 반환값이 있는 함수
def add(a, b):
    return a + b

result = add(3, 5)  # 8
```

### 타입 힌트가 있는 함수 (FastAPI 스타일)

```python
# 매개변수와 반환값에 타입 힌트 추가
def greet(name: str) -> str:
    return f"안녕하세요, {name}님!"

def add(a: int, b: int) -> int:
    return a + b

def divide(a: float, b: float) -> float:
    return a / b
```

**타입 힌트 문법:**
```
def 함수이름(매개변수: 타입) -> 반환타입:
    ...
```

### 기본값과 선택적 매개변수

```python
# 기본값이 있는 매개변수
def greet(name: str = "손님") -> str:
    return f"안녕하세요, {name}님!"

greet()         # "안녕하세요, 손님님!"
greet("홍길동")  # "안녕하세요, 홍길동님!"

# 선택적 매개변수 (None 허용)
from typing import Optional

def find_user(user_id: int, include_posts: Optional[bool] = None) -> dict:
    result = {"id": user_id}
    if include_posts:
        result["posts"] = []
    return result
```

### 키워드 인자

```python
def create_user(name: str, age: int, email: str) -> dict:
    return {"name": name, "age": age, "email": email}

# 위치 인자
create_user("홍길동", 25, "hong@example.com")

# 키워드 인자 (순서 상관없음)
create_user(email="hong@example.com", name="홍길동", age=25)

# 혼합 사용
create_user("홍길동", email="hong@example.com", age=25)
```

## 3. 클래스 (Classes)

### 기본 클래스

```python
class User:
    """사용자 클래스"""

    def __init__(self, name: str, age: int):
        """
        생성자 메서드
        객체가 생성될 때 자동으로 호출됩니다.
        """
        self.name = name  # 인스턴스 변수
        self.age = age

    def greet(self) -> str:
        """인스턴스 메서드"""
        return f"안녕하세요, {self.name}입니다."

# 클래스 사용
user = User("홍길동", 25)  # 객체 생성
print(user.name)          # "홍길동"
print(user.greet())       # "안녕하세요, 홍길동입니다."
```

**클래스 핵심 개념:**
```
┌─────────────────────────────────────────────────────────────┐
│  class User:                                                │
│      │                                                      │
│      ├── __init__(self, ...)    생성자 (객체 초기화)         │
│      │       │                                              │
│      │       └── self.name      인스턴스 변수               │
│      │                                                      │
│      └── def greet(self)        인스턴스 메서드             │
│                                                             │
│  self = 현재 객체 자신을 가리킴                              │
└─────────────────────────────────────────────────────────────┘
```

### 클래스 상속

```python
# 부모 클래스
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."

# 자식 클래스 (상속)
class Dog(Animal):
    def speak(self) -> str:
        return "멍멍!"

class Cat(Animal):
    def speak(self) -> str:
        return "야옹!"

# 사용
dog = Dog("바둑이")
print(dog.name)    # "바둑이" (부모에서 상속)
print(dog.speak()) # "멍멍!" (자식에서 재정의)
```

### 프로퍼티 (Property)

```python
class User:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self) -> str:
        """
        @property 데코레이터를 사용하면
        메서드를 속성처럼 사용할 수 있습니다.
        """
        return f"{self.first_name} {self.last_name}"

# 사용
user = User("길동", "홍")
print(user.full_name)  # "길동 홍" (메서드지만 ()없이 호출)
```

## 4. 데코레이터 (Decorators)

데코레이터는 함수나 클래스를 **수정하거나 확장**하는 문법입니다. FastAPI에서 매우 자주 사용됩니다.

### 기본 개념

```python
# 데코레이터 = 함수를 감싸는 함수

@decorator
def my_function():
    pass

# 위 코드는 아래와 동일합니다
def my_function():
    pass
my_function = decorator(my_function)
```

### FastAPI에서의 데코레이터 사용

```python
from fastapi import FastAPI

app = FastAPI()

# @app.get("/")는 데코레이터입니다
# 이 함수가 GET /요청을 처리하도록 등록합니다
@app.get("/")
def read_root():
    return {"message": "Hello"}

# @app.post("/users")
# 이 함수가 POST /users 요청을 처리합니다
@app.post("/users")
def create_user(name: str):
    return {"name": name}
```

**데코레이터 동작 이해:**
```
┌─────────────────────────────────────────────────────────────┐
│  @app.get("/")                                              │
│  def read_root():                                           │
│      return {"message": "Hello"}                            │
│                                                             │
│  실행 과정:                                                  │
│  1. app.get("/")가 데코레이터 함수를 반환                     │
│  2. 그 데코레이터가 read_root를 인자로 받음                   │
│  3. read_root를 GET / 경로에 등록                            │
│  4. 누군가 GET /를 요청하면 read_root가 실행됨                │
└─────────────────────────────────────────────────────────────┘
```

### 간단한 데코레이터 만들기

```python
import time

def timer(func):
    """함수 실행 시간을 측정하는 데코레이터"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행 시간: {end - start}초")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "완료"

slow_function()  # "slow_function 실행 시간: 1.001초"
```

## 5. async/await (비동기 프로그래밍)

### 동기 vs 비동기

```
동기 (Synchronous):
─────────────────────────────────────
작업1 시작 → 완료 → 작업2 시작 → 완료 → 작업3 시작 → 완료

비동기 (Asynchronous):
─────────────────────────────────────
작업1 시작 ─────────────────→ 완료
   작업2 시작 ─────────────────→ 완료
      작업3 시작 ─────────────────→ 완료

비동기는 여러 작업을 동시에 처리할 수 있어 효율적입니다.
```

### async/await 기본

```python
import asyncio

# async def로 비동기 함수 정의
async def fetch_data():
    print("데이터 가져오는 중...")
    await asyncio.sleep(1)  # 1초 대기 (비동기)
    print("데이터 완료!")
    return {"data": "결과"}

# await로 비동기 함수 호출
async def main():
    result = await fetch_data()
    print(result)

# 실행
asyncio.run(main())
```

### FastAPI에서의 async

```python
from fastapi import FastAPI

app = FastAPI()

# 동기 함수 (def)
@app.get("/sync")
def sync_endpoint():
    return {"type": "sync"}

# 비동기 함수 (async def)
@app.get("/async")
async def async_endpoint():
    # 데이터베이스 조회 같은 I/O 작업에 적합
    await some_async_operation()
    return {"type": "async"}
```

**언제 async를 사용할까?**
```
┌─────────────────────────────────────────────────────────────┐
│  async def 사용:                                            │
│  - 데이터베이스 조회/저장                                    │
│  - 외부 API 호출                                            │
│  - 파일 읽기/쓰기                                           │
│  - 네트워크 요청                                            │
│                                                             │
│  def 사용 (동기):                                           │
│  - 단순 계산                                                │
│  - 메모리 내 데이터 처리                                     │
│  - CPU 집약적 작업                                          │
└─────────────────────────────────────────────────────────────┘
```

## 6. import 문

### 기본 import

```python
# 모듈 전체 import
import os
import json

# 모듈에서 특정 항목만 import
from datetime import datetime
from typing import Optional, List

# 별칭 사용
import numpy as np
from datetime import datetime as dt
```

### 상대/절대 경로 import

```python
# 절대 경로 import (권장)
from app.models.user import User
from app.services.auth import AuthService

# 상대 경로 import (같은 패키지 내에서)
from .user import User        # 같은 폴더
from ..models.user import User  # 상위 폴더의 models
```

### 프로젝트 구조와 import

```
app/
├── __init__.py          # 패키지임을 표시
├── main.py
├── models/
│   ├── __init__.py
│   └── user.py          # class User 정의
└── services/
    ├── __init__.py
    └── auth.py

# auth.py에서 User를 import
from app.models.user import User
```

**`__init__.py`의 역할:**
```python
# app/models/__init__.py
from .user import User
from .post import Post

# 다른 곳에서
from app.models import User, Post  # 더 간단하게 import 가능
```

## 7. typing 모듈 (타입 힌트)

FastAPI는 타입 힌트를 많이 사용합니다.

### 기본 타입

```python
from typing import Optional, List, Dict, Union, Any

# Optional: None이 될 수 있음
def find_user(user_id: int) -> Optional[dict]:
    """사용자가 없으면 None 반환"""
    return None

# List: 리스트
def get_users() -> List[dict]:
    return [{"id": 1}, {"id": 2}]

# Dict: 딕셔너리
def get_config() -> Dict[str, str]:
    return {"key": "value"}

# Union: 여러 타입 중 하나
def get_id() -> Union[int, str]:
    return 123  # 또는 "abc"

# Any: 모든 타입 허용
def process_data(data: Any) -> Any:
    return data
```

### 제네릭 타입

```python
from typing import List, Dict

# List[타입]: 특정 타입의 리스트
numbers: List[int] = [1, 2, 3]
names: List[str] = ["Alice", "Bob"]

# Dict[키타입, 값타입]
user: Dict[str, int] = {"age": 25}
config: Dict[str, str] = {"mode": "debug"}

# 중첩 타입
users: List[Dict[str, str]] = [
    {"name": "Alice"},
    {"name": "Bob"}
]
```

## 8. 컨텍스트 매니저 (with 문)

### 파일 처리

```python
# 기존 방식 (수동 close 필요)
file = open("data.txt", "r")
content = file.read()
file.close()

# with 문 사용 (자동 close)
with open("data.txt", "r") as file:
    content = file.read()
# 블록을 벗어나면 자동으로 close됨
```

### 데이터베이스 세션 (FastAPI)

```python
# FastAPI에서 데이터베이스 세션 관리
def get_db():
    db = SessionLocal()
    try:
        yield db  # 세션 제공
    finally:
        db.close()  # 자동 정리

# 사용
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    # db 사용
    # 함수 종료 시 자동으로 db.close() 호출
```

## 9. 예외 처리 (try/except)

### 기본 예외 처리

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다")

# 여러 예외 처리
try:
    data = json.loads(invalid_json)
except json.JSONDecodeError:
    print("JSON 파싱 실패")
except Exception as e:
    print(f"알 수 없는 에러: {e}")
```

### FastAPI에서의 예외 처리

```python
from fastapi import HTTPException, status

def get_user(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # HTTP 404 에러 발생
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    return user
```

## 10. Enum (열거형)

```python
from enum import Enum

# 문자열 Enum 정의
class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

# 사용
role = UserRole.ADMIN
print(role.value)  # "admin"

# 비교
if role == UserRole.ADMIN:
    print("관리자입니다")

# 이 프로젝트에서 사용 (app/models/user.py)
class UserRole(str, Enum):
    ADMIN = "admin"          # 관리자
    MODERATOR = "moderator"  # 운영자
    USER = "user"            # 일반 사용자
```

## 11. Generator와 yield

### 기본 Generator

```python
# 일반 함수: 모든 값을 한 번에 반환
def get_numbers_list():
    return [1, 2, 3, 4, 5]

# Generator: 값을 하나씩 생성
def get_numbers_generator():
    for i in range(1, 6):
        yield i  # 하나씩 반환

# 사용
for num in get_numbers_generator():
    print(num)  # 1, 2, 3, 4, 5
```

### FastAPI에서의 Generator (의존성)

```python
# 데이터베이스 세션을 Generator로 관리
def get_db():
    """
    데이터베이스 세션을 생성하고 제공하는 Generator
    """
    db = SessionLocal()  # 세션 생성
    try:
        yield db  # 세션 제공 (여기서 멈춤)
    finally:
        db.close()  # 정리 (요청 완료 후 실행)

# 사용
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    #          ↑ get_db가 yield한 db를 받음
    return db.query(User).all()
    # 함수 종료 후 get_db의 finally 블록 실행
```

**Generator 동작 흐름:**
```
┌─────────────────────────────────────────────────────────────┐
│  def get_db():                                              │
│      db = SessionLocal()    # 1. 세션 생성                   │
│      try:                                                   │
│          yield db           # 2. 세션 제공 → 멈춤            │
│      finally:                                               │
│          db.close()         # 4. 정리                       │
│                                                             │
│  @app.get("/")                                              │
│  def endpoint(db = Depends(get_db)):                        │
│      # 3. db 사용                                           │
│      return db.query(...)   # → 완료되면 4번으로            │
└─────────────────────────────────────────────────────────────┘
```

## 요약

FastAPI 개발에 필요한 Python 핵심 개념:

| 개념 | FastAPI 사용 예 |
|------|----------------|
| 타입 힌트 | 매개변수/반환값 검증 |
| 클래스 | Pydantic 모델, SQLAlchemy 모델 |
| 데코레이터 | `@app.get()`, `@router.post()` |
| async/await | 비동기 엔드포인트 |
| Generator | 의존성 주입 (`get_db`) |
| Enum | 사용자 역할 정의 |
| 예외 처리 | `HTTPException` |

## 다음 단계

다음 문서 [02-fastapi-fundamentals.md](./02-fastapi-fundamentals.md)에서는 FastAPI의 핵심 개념을 학습합니다.
