from redis.asyncio import Redis

redis_master = Redis(
	host="redis-master.caching.svc.cluster.local",
	port=6379,
	decode_responses=True,
	password="cGFzc3dvcmQ",
)
redis_replica = Redis(
	host="redis-replicas.caching.svc.cluster.local",
	port=6379,
	decode_responses=True,
	password="cGFzc3dvcmQ",
)


async def get_master() -> Redis:
	return redis_master


async def get_replica() -> Redis:
	return redis_replica
