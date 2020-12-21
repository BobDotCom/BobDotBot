import aiosqlite
import asyncio
import aiosqlite_pool

 
class Pool:
    def __init__(self,database,max_connection=5,*args,**kwargs):
        self._database = database
        self._max_connection = max_connection
        self.__args = [args,kwargs]
        self._connections = []
        self._waiters = []
        self._loop = asyncio.get_event_loop()
    
    async def acquire(self,*,timeout=0):
        if len(self._connections) >= self._max_connection:
            fut = self._loop.create_future()
            self._waiters.append(fut)
            if timeout > 0:
                await asyncio.wait_for(fut, timeout=timeout)
            else:
                await fut
            self._waiters.remove(fut)
        args,kwargs = self.__args
        conn = await aiosqlite_pool.connect(self._database,*args,**kwargs)
        conn._pool = self
        self._connections.append(conn)
        return conn

 
async def main():
    pool = Pool(":memory:")
    