Простой Python-сценарий без каких-либо зависимостей, оборачивающий стандартный вывод при туннелировании локального окружения в интернет, для сервиса [localhost.run](https://localhost.run/).

Пригодится для разработки продуктов, требующих интеграции с различными сервисами, вроде серверов Telegram.

Работает с однонаправленной очередью на основе `asyncio.Queue`, отправитель которой помещается в задачу монитора, а получатель интегрируется в Вашу логику.

### Условия для использования

Пользоваться услугами localhost.run можно и без регистрации, но тогда динамически изменяемый адрес будет изменяться довольно часто. Рекомендуется пройти простую [верификацию](https://admin.localhost.run/) чтобы попасть в пространство личного кабинета, в разделе "SSH Keys" которого, произвести настройку ключа, который будет использоваться в соединении.

#### SSH-Key
Если сгенерированного ключа ещё нет, завести его можно следуя этим инструкциям для:
  * [Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement#user-key-generation)
  * [Linux](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

Инструкции для Linux так же имеют указания и для того, как добавить сгенерированный ключ в окружение агента. Для Windows, среди прочих, можно пойти следующим путём:
  1. Пройдите по пути "Ваш системный диск(обычно это диск C):\Users\[имя Вашего пользователя]\.ssh" и откройте файл с именем `config`. Он не имеет расширения и открывается даже блокнотом.
  2. Вставьте в него следующий текст:
```shell
Host localhost.run
    HostName localhost.run
        IdentityFile ~/.ssh/id_ed25519
```
   В некоторых случаях может потребоваться указать `%UserProfile%` вместо тильды(~).
  3. Сохраните файл и закройте его.
  4. В том же блокноте откройте файл `id_ed25519.pub` и скопировав его содержимое, вставьте в поле "SSH public key" в разделе "SSH Keys", в [личном кабинете сайта localhost.run](https://admin.localhost.run/), для доступа к которому Вы уже должны были пройти верификацию.
  5. Там же заполните поле "description", чтобы у ключа было отличимое имя.
  6. Примените изменения.

Теперь, при выполнении в терминале дефолтного:
```shell
ssh -R 80:localhost:8080 localhost.run
```
Перед выводом текущего публичного адреса, по которому доступен Ваш localhost, должно быть упоминание почты, которая была использована для авторизации.

Это сделает событие изменения адреса заметно реже.

### Install

Клонируйте этот репозиторий в папку проекта:
```shell
git clone https//:...
```


### Пример

```python
import asyncio
from localhost_run_monitor import (
    monitor, Channel, Receiver)

RED_CMD = "\x1b[31m{}\x1b[0m"
GREEN_CMD = "\x1b[32m{}\x1b[0m"


async def repeater(receiver: Receiver[str]) -> None:
    print(GREEN_CMD.format("Starting URL repeater..."))
    while True:
        print("Waiting for URL...")
        try:
            url = await receiver.recv()
        except asyncio.CancelledError:
            print(RED_CMD.format("URL repeater stopped"))
            break
        print(f"{GREEN_CMD.format('Received URL:')} {url}")


async def main() -> None:
    channel = Channel[str]()
    sender, receiver = channel()
    
    print("Press Ctrl+C to stop")
    print(GREEN_CMD.format("Test starting..."))
    repeater_task = asyncio.create_task(repeater(receiver))
    monitor_task = asyncio.create_task(monitor(
        sender, on_host="80:localhost:8000"))

    await monitor_task
    repeater_task.cancel()
    await repeater_task
    print(GREEN_CMD.format("Test finished"))


if __name__ == "__main__":
    asyncio.run(main())
```