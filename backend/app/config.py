from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://busyness:busyness@db:5432/busyness"
    jwt_secret: str = "your-secret-key-change-this-in-production"
    app_url: str = "http://localhost:5173"

    @property
    def sqlalchemy_database_url(self) -> str:
        # Heroku provides DATABASE_URL starting with postgres://
        # SQLAlchemy 1.4+ requires postgresql://
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql://", 1)
        return self.database_url

    class Config:
        env_file = ".env"
        env_prefix = "" # Allows mapping DATABASE_URL to database_url



settings = Settings()
