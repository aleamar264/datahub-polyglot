from faststream.kafka.fastapi import KafkaRouter, KafkaBroker
from faststream.kafka.opentelemetry import KafkaTelemetryMiddleware


kafka_router = KafkaRouter(
	bootstrap_servers=[
		"my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092",
	],
	middlewares=(KafkaTelemetryMiddleware(),),
	prefix="/kafka",
)


broker = kafka_router.broker
