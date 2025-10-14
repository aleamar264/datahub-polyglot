from faststream.kafka.fastapi import KafkaRouter
from faststream.kafka.opentelemetry import KafkaTelemetryMiddleware

from utils.kafka.settings import ReadEnvKafkaSettings

settings = ReadEnvKafkaSettings()

kafka_router = KafkaRouter(
	bootstrap_servers=[
		f"{settings.host}:{settings.port}",
	],
	middlewares=(KafkaTelemetryMiddleware(),),
	prefix="/kafka",
)


broker = kafka_router.broker
