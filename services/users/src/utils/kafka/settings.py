from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ReadEnvKafkaSettings(BaseSettings):
	"""
	Read Environment variables to get the basic configuration
	of the database. In this case the file used is a .env called
	`.database.env`

	If you want to use other file
	.. code-block:: python
	    ReadEnvDatabaseSettings(_env_file="name_of_env_file")

	"""  # noqa: E101

	host: str = Field(..., description="Host for Kafka Bootstrap", alias="KAFKA_HOST")
	port: int = Field(..., description="Database Port", alias="KAFKA_PORT")

	model_config = SettingsConfigDict(
		env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
	)
