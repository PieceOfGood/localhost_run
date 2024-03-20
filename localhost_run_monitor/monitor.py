import re
import asyncio
from .data import Sender

URL_MATCHER = re.compile(rb"https://[^.]+\.lhr\.life")


async def monitor(
        sender: Sender[str], *,
        on_host: str = "80:localhost:8000") -> None:
    """ Запускает процесс туннелирования по SSH и читает его
    стандартный вывод в поисках URL.
    :param sender: сторона канала для отправки URL
    :param on_host: строка с описанием сигнатуры туннеля
    """
    process = await asyncio.create_subprocess_exec(
        "ssh", "-R", on_host, "localhost.run",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        while True:
            stdout_data = await process.stdout.readline()
            if not stdout_data:
                break

            if m := URL_MATCHER.search(stdout_data):
                url = m.group(0).decode()
                await sender.send(url)

        await process.wait()

    except asyncio.CancelledError:
        process.terminate()
        await process.wait()
