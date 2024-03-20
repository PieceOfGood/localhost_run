from asyncio import Queue
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseQueue(Generic[T]):
    def __init__(self, queue: Queue[T]) -> None:
        self.queue = queue


class Sender(BaseQueue[T]):
    async def send(self, data: T) -> None:
        await self.queue.put(data)


class Receiver(BaseQueue[T]):
    async def recv(self) -> T:
        return await self.queue.get()


class Channel(Generic[T]):
    """ Asyncio one-way channel """
    def __call__(self) -> tuple[Sender[T], Receiver[T]]:
        queue: Queue[T] = Queue()
        return Sender[T](queue), Receiver[T](queue)
