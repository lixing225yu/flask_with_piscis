import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool


class TraditionalMultiThread:
    def __init__(self, method, method_params, max_count=5):
        self.method = method
        self.method_params = method_params
        self.max_count = max_count
        self.result = []

    def _execute_one(self, m):
        self.result.append(self.method(*m))

    def execute(self):
        with ThreadPoolExecutor(self.max_count) as executor:
            for m in self.method_params:
                executor.submit(self._execute_one, m)


class AsyncioMultiThread:
    def __init__(self, method, method_params, max_count=5):
        self.method = method
        self.method_params = method_params
        self.max_count = max_count
        self.result = []

    async def _execute_one(self, executor, p):
        result = asyncio.get_event_loop().run_in_executor(executor, self.method, *p)
        res = await result
        self.result.append(res)

    def execute(self):
        tpe = ThreadPoolExecutor(self.max_count)
        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(self._execute_one(tpe, p)) for p in self.method_params]
        loop.run_until_complete(asyncio.gather(*tasks))


class AsyncioCoroutine:
    def __init__(self, method, method_params, max_count=5):
        self.method = method
        self.method_params = method_params
        self.max_count = max_count
        self.result = []

    async def _execute_one(self, p):
        result = self.method(*p)
        res = await result
        self.result.append(res)

    def execute(self):
        loop = asyncio.get_event_loop()
        tasks = [asyncio.ensure_future(self._execute_one(p)) for p in self.method_params]
        loop.run_until_complete(asyncio.gather(*tasks))


# 多进程方法参数只能是一个
class MultiProcess:
    def __init__(self, method, method_params, max_count=5):
        self.method = method
        self.method_params = method_params
        self.max_count = max_count
        self.result = []

    def execute(self):
        with Pool(self.max_count) as p:
            self.result = p.map(self.method, self.method_params)

