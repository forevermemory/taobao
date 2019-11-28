
import redis


def get_redis_conn():
    pool = redis.ConnectionPool(host='106.14.205.232',port=6379,db=8,encoding='utf-8',decode_responses=True)
    conn = redis.Redis(connection_pool=pool)
    # conn = redis.Redis(host='127.0.0.1',port=6379,db=8,encoding='utf-8',decode_responses=True)
    return conn