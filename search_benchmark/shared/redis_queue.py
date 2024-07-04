import redis
import sys
import os
import time
from search_benchmark.shared.config import get_redis_url
class RedisQueue:
    def __init__(self, queue='task_queue', model=None):
        try:

            timeout = 3600
            redis_url = get_redis_url()
            self._redis = redis.Redis.from_url(redis_url, socket_timeout=timeout)
            self._queue = queue
            self.model = model
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")

    def send_to_queue(self, body):
        try:
            self._redis.lpush(self._queue, body)
            print(f" [x] Sent {body}")
        except Exception as e:
            print(f"An error occurred in redis: {e}")

    def start_consuming(self, callback):
        print(" [*] Waiting for messages. To exit press CTRL+C")
        try:
            while True:
                body = self._redis.rpop(self._queue)
                if body:
                    retries = 5
                    while retries > 0:
                        try:
                            callback(body)
                            break
                        except Exception as e:
                            retries -= 1
                            print(f"Callback failed, retrying... ({5 - retries}/5). Error: {e}")
                            if retries == 0:
                                print("Callback failed after 5 retries.")
                else:
                    # Sleep to prevent tight looping when the queue is empty
                    time.sleep(1)
        except KeyboardInterrupt:
            print('\nInterrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception as e:
            print(f"An error occurred in start_consuming: {e}")

    def close_connection(self):
        # Redis connection is managed automatically, so there might not be a need to explicitly close it.
        print("Connection closed")
    def start_consuming_batch_loop(self, callback, count):
            print("[*] Waiting for messages. To exit press CTRL+C")
            try:
                while True:
                    # Use a pipeline to execute multiple RPOP commands simultaneously
                    pipeline = self._redis.pipeline()
                    for _ in range(count):
                        pipeline.rpop(self._queue)
                    batch = pipeline.execute()

                    # Filter out None values (in case the queue is empty)
                    batch = [body for body in batch if body]

                    if batch:
                        retries = 5
                        while retries > 0:
                            try:
                                callback(batch)
                                break
                            except Exception as e:
                                retries -= 1
                                print(f"Callback batch failed, retrying... ({5 - retries}/5). Error: {e}")
                                if retries == 0:
                                    print("Callback batch failed after 5 retries.")
                    else:
                        # Sleep to prevent tight looping when the queue is empty
                        time.sleep(1)
            except KeyboardInterrupt:
                print('\nInterrupted')
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
            except Exception as e:
                print(f"An error occurred in start_consuming_batch_loop: {e}")

# Example callback function
def process_message(message):
    print(f"Processing message: {message}")

# Example usage
if __name__ == "__main__":
    queue = RedisQueue('my_task_queue')
    queue.send_to_queue('Hello, Redis!')
    queue.start_consuming(process_message)