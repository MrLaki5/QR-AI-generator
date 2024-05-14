from redis import Redis, ConnectionPool
import time


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
        while True:
            try:
                return self.redis.rpush(queue_name, value)
            except Exception as e:
                print("RedisConnector.push_in_queue() error: ", e)
                time.sleep(1)

    def pop_from_queue(self, queue_name):
        while True:
            try:
                return self.redis.blpop(queue_name)
            except Exception as e:
                print("RedisConnector.pop_from_queue() error: ", e)
                time.sleep(1)

    def get_queue_length(self, queue_name):
        while True:
            try:
                return self.redis.llen(queue_name)
            except Exception as e:
                print("RedisConnector.get_queue_length() error: ", e)
                time.sleep(1)

    def get_all_from_queue(self, queue_name):
        while True:
            try:
                return self.redis.lrange(queue_name, 0, -1)
            except Exception as e:
                print("RedisConnector.get_all_from_queue() error: ", e)
                time.sleep(1)

    # Set operations
    def put_in_set(self, hash_name, key, value):
        while True:
            try:
                return self.redis.hset(hash_name, key, value)
            except Exception as e:
                print("RedisConnector.put_in_set() error: ", e)
                time.sleep(1)

    def check_in_set(self, hash_name, key):
        while True:
            try:
                return self.redis.hexists(hash_name, key)
            except Exception as e:
                print("RedisConnector.check_in_set() error: ", e)
                time.sleep(1)

    def get_from_set(self, hash_name, key):
        while True:
            try:
                return self.redis.hget(hash_name, key)
            except Exception as e:
                print("RedisConnector.get_from_set() error: ", e)
                time.sleep(1)

    def remove_from_set(self, hash_name, key):
        while True:
            try:
                return self.redis.hdel(hash_name, key)
            except Exception as e:
                print("RedisConnector.remove_from_set() error: ", e)
                time.sleep(1)
