"""
Application Configuration
==========================

환경 변수 및 설정을 관리하는 모듈입니다.
Pydantic Settings를 사용하여 타입 안전한 설정 관리를 제공합니다.
"""

from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
import json


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스

    환경 변수나 .env 파일에서 설정을 로드합니다.
    모든 설정은 타입 검증이 이루어집니다.
    """

    # ===========================================
    # Application Settings
    # ===========================================
    app_name: str = Field(default="FastAPI Boilerplate", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(default="change-this-secret-key", alias="SECRET_KEY")

    # ===========================================
    # Database Configuration
    # ===========================================
    db_type: str = Field(default="postgresql", alias="DB_TYPE")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="password", alias="DB_PASSWORD")
    db_name: str = Field(default="fastapi_db", alias="DB_NAME")
    sqlite_file: str = Field(default="./data/app.db", alias="SQLITE_FILE")

    # ===========================================
    # JWT Settings
    # ===========================================
    jwt_secret_key: str = Field(default="jwt-secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # ===========================================
    # CORS Settings
    # ===========================================
    cors_origins: str = Field(
        default='["http://localhost:3000","http://localhost:8080"]',
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(default='["*"]', alias="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default='["*"]', alias="CORS_ALLOW_HEADERS")

    # ===========================================
    # Theme Settings
    # ===========================================
    default_theme: str = Field(default="light", alias="DEFAULT_THEME")
    available_themes: str = Field(
        default='["light","dark","blue","green"]',
        alias="AVAILABLE_THEMES"
    )

    @property
    def database_url(self) -> str:
        """
        데이터베이스 URL을 생성합니다.

        DB_TYPE에 따라 적절한 연결 문자열을 반환합니다.

        Returns:
            str: SQLAlchemy 데이터베이스 URL
        """
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_file}"
        elif self.db_type == "postgresql":
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type in ["mysql", "mariadb"]:
            return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins를 리스트로 반환"""
        return json.loads(self.cors_origins)

    @property
    def cors_allow_methods_list(self) -> List[str]:
        """CORS methods를 리스트로 반환"""
        return json.loads(self.cors_allow_methods)

    @property
    def cors_allow_headers_list(self) -> List[str]:
        """CORS headers를 리스트로 반환"""
        return json.loads(self.cors_allow_headers)

    @property
    def available_themes_list(self) -> List[str]:
        """사용 가능한 테마를 리스트로 반환"""
        return json.loads(self.available_themes)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    설정 인스턴스를 반환합니다.

    lru_cache를 사용하여 설정 객체를 캐싱합니다.
    이렇게 하면 매번 .env 파일을 읽지 않아도 됩니다.

    Returns:
        Settings: 설정 인스턴스
    """
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
