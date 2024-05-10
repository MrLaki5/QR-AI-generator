from redis import Redis, ConnectionPool


class RedisConnector:
    TASK_QUEUE_ID_NAME = "task_queue_id"
    TASK_SET_DATA_NAME = "task_set_data"
    RESULT_QUEUE_NAME = "result_queue"
    CONNECTED_SOCKET_SET_NAME = "connected_socket_set"

    def __init__(self, host, port, password):
        connection_pool = ConnectionPool(host=host, port=port, password=password, decode_responses=True)
        self.redis = Redis.from_pool(connection_pool)

    # Queue operations
    def push_in_queue(self, queue_name, value):
        return self.redis.rpush(queue_name, value)

    def pop_from_queue(self, queue_name):
        return self.redis.blpop(queue_name)

    def get_queue_length(self, queue_name):
        return self.redis.llen(queue_name)

    def get_all_from_queue(self, queue_name):
        return self.redis.lrange(queue_name, 0, -1)

    # Set operations
    def put_in_set(self, hash_name, key, value):
        return self.redis.hset(hash_name, key, value)

    def check_in_set(self, hash_name, key):
        return self.redis.hexists(hash_name, key)

    def get_from_set(self, hash_name, key):
        return self.redis.hget(hash_name, key)

    def remove_from_set(self, hash_name, key):
        return self.redis.hdel(hash_name, key)
