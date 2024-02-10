import redis
import os
import dotenv
dotenv.load_dotenv()

client = redis.Redis(
  host='redis-16508.c253.us-central1-1.gce.cloud.redislabs.com',
  port=16508,
  password='z6vIXisQfDGwTf4sisq7fHj7bvDQAkfd',
  decode_responses=True)

print(client.get("uses"))
