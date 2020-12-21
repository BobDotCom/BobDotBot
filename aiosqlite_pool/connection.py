import aiosqlite
import asyncio

class Connection(aiosqlite.Connection):
    def __init__(self,*args,**kwargs):
        if "pool" in kwargs:
            self._pool = kwargs.pop("pool")
        super().__init__(*args,**kwargs)
    
    async def close(self):
        self._pool._connections.remove(self)
        try:
            waiter = next(iter(self._pool._waiters))
        except StopIteration:
            await super().close()
            return
        if not waiter.done():
            waiter.set_result(True)
        await super().close()
         
    async def release(self):
        await self.close()
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self,*args):
        await self.release()