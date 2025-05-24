from pydantic_settings import BaseSettings, SettingsConfigDict

from .database import DatabaseConfiguration
from .default import DefaultConfiguration
from .graylog import GraylogConfiguration
from .jwt import JwtConfiguration


class ProjectConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_")

    # * Вложенные группы настроек
    database: DatabaseConfiguration = DatabaseConfiguration()
    jwt: JwtConfiguration = JwtConfiguration()
    default: DefaultConfiguration = DefaultConfiguration()
    graylog: GraylogConfiguration = GraylogConfiguration()

    # * Опциональные переменные
    DEBUG_MODE: bool = True
    SERVICE_NAME: str = "ilps-service-auth"


configs = ProjectConfiguration()

__all__ = ("configs",)
