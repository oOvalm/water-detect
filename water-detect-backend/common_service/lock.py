# -*- coding: utf-8 -*-
# @DateTime : 2022/8/25 17:38
# @Author   : charlesxie
import threading
import uuid
import weakref

import time
import redis

# 修改后的 LOCK_SCRIPT，去掉重入逻辑
LOCK_SCRIPT = b"""
if (redis.call('exists', KEYS[1]) == 0) then
    redis.call('set', KEYS[1], ARGV[2]);
    redis.call('expire', KEYS[1], ARGV[1]);
    return 1;
end ;
return 0;
"""
UNLOCK_SCRIPT = b"""
if (redis.call('exists', KEYS[1]) == 0) then
    return nil;
end ;
if (redis.call('get', KEYS[1]) == ARGV[1]) then
    redis.call('del', KEYS[1]);
    return 1;
end ;
return 0;
"""
RENEW_SCRIPT = b"""
if redis.call("exists", KEYS[1]) == 0 then
    return 1
elseif redis.call("ttl", KEYS[1]) < 0 then
    return 2
else
    redis.call("expire", KEYS[1], ARGV[1])
    return 0
end
"""

LOCK_PREFIX = "water-detect-RedisLock"

class RedisLock:
    """
    redis实现互斥锁，支持重入和续锁
    """

    def __init__(self, conn, lock_name, expire=30, uid=None, is_renew=True):
        self.conn = conn
        self.lock_script = None
        self.unlock_script = None
        self.renew_script = None
        self.register_script()

        self._name = f"{LOCK_PREFIX}:{lock_name}"
        self._expire = int(expire)
        self._uid = uid or str(uuid.uuid4())

        self._lock_renew_interval = self._expire * 2 / 3
        self._lock_renew_threading = None

        self.is_renew = is_renew
        self.is_acquired = None
        self.is_released = None

    @property
    def id(self):
        return self._uid

    @property
    def expire(self):
        return self._expire

    def acquire(self):
        result = self.lock_script(keys=(self._name,), args=(self._expire, self._uid))
        if self.is_renew:
            self._start_renew_threading()
        self.is_acquired = True if result else False
        return self.is_acquired

    def release(self):
        if self.is_renew:
            self._stop_renew_threading()

        result = self.unlock_script(keys=(self._name,), args=(self._uid,))
        self.is_released = True if result else False
        print(f"release lock: {self.is_released}")
        return self.is_released

    def register_script(self):
        self.lock_script = self.conn.register_script(LOCK_SCRIPT)
        self.unlock_script = self.conn.register_script(UNLOCK_SCRIPT)
        self.renew_script = self.conn.register_script(RENEW_SCRIPT)

    def renew(self, renew_expire=30):
        result = self.renew_script(keys=(self._name,), args=(renew_expire,))
        if result == 1:
            raise Exception(f"{self._name} cannot renew lock or lock has been expired!")
        elif result == 2:
            raise Exception(f"{self._name} not set expire")
        elif result:
            raise Exception(f"unknown error code: {result}")

    @staticmethod
    def _renew_scheduler(weak_self, interval, lock_event):
        while not lock_event.wait(timeout=interval):
            lock = weak_self()
            if lock is None:
                break
            lock.renew(renew_expire=lock.expire)
            del lock

    def _start_renew_threading(self):
        self.lock_event = threading.Event()
        self._lock_renew_threading = threading.Thread(target=self._renew_scheduler,
                                                      kwargs={
                                                          "weak_self": weakref.ref(self),
                                                          "interval": self._lock_renew_interval,
                                                          "lock_event": self.lock_event
                                                      })

        self._lock_renew_threading.demon = True
        self._lock_renew_threading.start()

    def _stop_renew_threading(self):
        if self._lock_renew_threading is None or not self._lock_renew_threading.is_alive():
            return
        self.lock_event.set()
        # join 作用是确保thread子线程执行完毕后才能执行下一个线程
        self._lock_renew_threading.join()
        self._lock_renew_threading = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.release()

    @staticmethod
    def is_locked(redisConn, lock_name):
        return redisConn.exists(f"{LOCK_PREFIX}:{lock_name}")


custom_redis = None
def _run_work(my_user_id):
    with RedisLock(custom_redis, "test", uid=my_user_id, expire=5) as r:
        if r.is_acquired:
            print(f"just do it,{my_user_id}")
            time.sleep(20)
        else:
            print(f"quit, {my_user_id}")


if __name__ == '__main__':

    custom_redis = redis.Redis(host="localhost", port=6379, db=2)
    a1 = threading.Thread(target=_run_work, args=("charles",))
    a2 = threading.Thread(target=_run_work, args=("xie",))

    a1.start()
    a2.start()

