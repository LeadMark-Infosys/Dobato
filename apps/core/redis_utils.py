from django_redis import get_redis_connection

def get_redis():
    return get_redis_connection("default")

def set_withdrawal_limit(wallet_id, seconds=86400):
    redis_conn = get_redis()
    redis_key = f"withdrawal_limit:{wallet_id}"
    redis_conn.set(redis_key, 1, ex=seconds)

def check_withdrawal_limit(wallet_id):
    redis_conn = get_redis()
    redis_key = f"withdrawal_limit:{wallet_id}"
    return redis_conn.get(redis_key)

def set_token(key, value, seconds):
    redis_conn = get_redis()
    redis_conn.set(key, value, ex=seconds)

def get_token(key):
    redis_conn = get_redis()
    token = redis_conn.get(key)
    return token.decode() if token else None

def delete_token(key):
    redis_conn = get_redis()
    redis_conn.delete(key)