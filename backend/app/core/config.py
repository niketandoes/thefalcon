from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Split It Fair"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str | None = None
    
    DB_HOST: str = "localhost"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "split_it_fair"
    DB_PORT: int = 5432

    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # Dev only
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @computed_field
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            # asyncpg doesn't support sslmode query param directly in some versions
            # and SQLAlchemy tries to pass it to the connect() function.
            from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
            
            url = self.DATABASE_URL
            # Replace scheme
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            # Remove sslmode if present to avoid TypeError in asyncpg
            u = urlparse(url)
            query = parse_qs(u.query)
            query.pop('sslmode', None)
            new_query = urlencode(query, doseq=True)
            url = urlunparse(u._replace(query=new_query))
            return url
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

settings = Settings()
