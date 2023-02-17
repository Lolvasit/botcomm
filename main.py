import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import traceback
from telethon.events import NewMessage
from telethon import TelegramClient
from telethon.events.common import EventBuilder
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType
from config import API_HASH, API_ID, API_TOKEN

from aiogram.contrib.fsm_storage.memory import MemoryStorage
import typing

from aiogram.dispatcher.filters import BoundFilter

# from peewee import *
import python_socks
# db = SqliteDatabase('db.sqlite')
import json


def readlines(filename: str):
    with open(filename, encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]

import json
with open("settings.json", "r") as f:
    settings: dict = json.load(f)

def proxy_gen():
    i = 0
    while True:
        proxy_list = readlines("proxy.txt")
        if i >= len(proxy_list):
            i = 0
        proxy = proxy_list[i].split(":")
        yield {
            "proxy_type": python_socks.ProxyType(int(proxy[0])),
            "addr": proxy[1],
            "port": int(proxy[2]),
            "username": proxy[3],
            "password": proxy[4],
        }
        i += 1

proxys = proxy_gen()


main_client = TelegramClient(
    f"accounts/main.session",
    api_id=API_ID,
    api_hash=API_HASH,
    # proxy=next(proxys)
)

def create_timed_rotating_log(path):
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(
        "logs/" + path, when="d", interval=1, backupCount=5
    )
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

    return logger


logger = create_timed_rotating_log("logs.log")

# db.create_tables([])
count_posts = 0

import python_socks




class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        return (str(obj.from_user.id) in readlines("admins.txt")) == self.is_admin



logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
dp.filters_factory.bind(AdminFilter)

@dp.message_handler(commands=["id"])
async def get_id(msg: Message):
    await msg.answer(msg.from_user.id)

new_kb = InlineKeyboardMarkup
btn = InlineKeyboardButton

@dp.message_handler(is_admin=True, commands=["start", "adm", "admin"])
async def start_get(msg: Message):
    kb = new_kb(row_width=1).add(
        btn("Проксі", callback_data="proxys"),
        btn("Акаунти", callback_data="accounts"),
        btn("Адміни", callback_data="admins"),
        btn("Канали", callback_data="channels"),
    )
    await msg.answer("Головне меню", reply_markup=kb)


@dp.callback_query_handler(text="proxys", is_admin=True)
async def proxys_get(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Команда для зміни проксі: /set_proxy <кожен проксі з нової строки>\nТипи проксі\nSOCKS4 = 1\nSOCKS5 = 2\nHTTP = 3\nФормат:\nТип проксі:адреса:порт:логін:пароль\nПриклад команди: /set_proxy 1:0.0.0.1:132:a:b\n2:0.0.0.1:133:a:b")
    proxy_list = readlines("proxy.txt")
    if len(proxy_list) == 0:
        await call.message.answer("Немає проксі")
        return
    await call.message.answer("\n".join(proxy_list))

@dp.message_handler(commands=["set_proxy"], is_admin=True)
async def proxys_get(msg: Message):
    with open("proxy.txt", "w") as f:
        f.write(msg.get_args())
    await msg.answer("Успішно!")
    proxy_list = readlines("proxy.txt")
    if len(proxy_list) == 0:
        await msg.answer("Немає проксі")
        return
    await msg.answer("\n".join(proxy_list))

@dp.callback_query_handler(text="admins", is_admin=True)
async def proxys_get(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Команда для зміни адмінів: /set_admins <кожен ID з нової строки>\nПриклад команди: /set_admins 2312414124\n21312313")
    proxy_list = readlines("admins.txt")
    if len(proxy_list) == 0:
        await call.message.answer("Немає адмінів")
        return
    await call.message.answer("\n".join(proxy_list))

@dp.message_handler(commands=["set_admins"], is_admin=True)
async def proxys_get(msg: Message):
    with open("admins.txt", "w") as f:
        f.write(msg.get_args())
    await msg.answer("Успішно!")
    proxy_list = readlines("admins.txt")
    if len(proxy_list) == 0:
        await msg.answer("Немає адмінів")
        return
    await msg.answer("\n".join(proxy_list))
    
@dp.callback_query_handler(text="accounts", is_admin=True)
async def proxys_get(call: CallbackQuery):
    await call.answer()
    kb = new_kb().add(btn("Новий акаунт", callback_data="new_acc"))
    await call.message.answer("Всі акаунти\nЩоб видалити введіть /delete_acc <назву файлу>", reply_markup=kb)
    accounts = get_accounts_dir()
    if len(accounts) == 0:
        await call.message.answer("Немає акаунтів")
        return
    await call.message.answer("\n".join(accounts))

from aiogram.dispatcher.filters.state import State, StatesGroup

class NewAccStates(StatesGroup):
    file = State()

def get_cancel_kb():
    return new_kb(row_width=1).add(btn("Відмінити", callback_data="cancel"))

from aiogram.dispatcher import FSMContext
@dp.callback_query_handler(text="cancel", state="*", is_admin=True)
async def proxys_get(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Відмінено")


@dp.callback_query_handler(text="new_acc", is_admin=True)
async def proxys_get(call: CallbackQuery):
    await NewAccStates.file.set()
    await call.message.answer("Відправте файл", reply_markup=get_cancel_kb())

@dp.message_handler(content_types=ContentType.DOCUMENT, state=NewAccStates.file)
async def proxys_get(msg: Message, state: FSMContext):
    account = msg.document.file_name
    await msg.document.download(f"accounts/{account}")
    await state.finish()

    channel_list = load_json("channels.txt")
    for channel in channel_list.values():
        await join_channel(account, channel)
    await msg.answer("Успішно збережено")

@dp.message_handler(commands=["delete_acc"], is_admin=True)
async def proxys_get(msg: Message):
    filename = msg.get_args()
    os.remove(f"accounts/{filename}")
    await msg.answer(f"Акаунт {filename} видалено")

def load_json(filename: str):
    with open(filename, "r") as f:
        return json.load(f)

@dp.callback_query_handler(text="channels", is_admin=True)
async def proxys_get(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Команда для зміни списку каналів: /add_channels <кожен канал з нової строки>\nФормат:Посилання на канал без @ або посилання-запрошення\nПриклад команди: /add_channels abc\nhttps://t.me/+p8jgJGoqxDiI1Mmy\nВийти з каналу /del_channel <id>")
    channels_list = load_json("channels.txt")
    if len(channels_list) == 0:
        await call.message.answer("Немає каналів")
        return
    await call.message.answer("\n".join([f"{i} - {j}" for i, j in channels_list.items()]))

logger.info("test")
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, GetHistoryRequest
async def join_channel(account: str, link: str, client=None, spam3=True):
    try:
        if client is None:
            client = TelegramClient(
                f"accounts/{account}",
                api_id=API_ID,
                api_hash=API_HASH,
                # proxy=next(proxys)
                )
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                return
    except Exception:
        if account != "main.session":
            await client.disconnect()
        logger.info(f"account {account}")
        logger.error(traceback.format_exc())
        return
    if link.startswith("https://t.me/+"):
        link = link.lstrip("https://t.me/+")
        try:
            res = await client(ImportChatInviteRequest(hash=link))
            chat_id = res.chats[0].id

            if account != "main.session":
                if spam3 and settings["spam3"] == True:
                    posts = await client(GetHistoryRequest(
                        peer=chat_id,
                        limit=3,
                        offset_date=None,
                        offset_id=0,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0))

                    for post in posts.messages:
                        try:
                            if os.path.exists("tmp.png"):
                                try:
                                    await client.send_file(chat_id, file="tmp.png", caption=settings["msg"], comment_to=post)
                                except:
                                    logger.error(traceback.format_exc())
                                    await client.send_message(chat_id, message=settings["msg"], comment_to=post)
                            else:
                                await client.send_message(chat_id, message=settings["msg"], comment_to=post)
                        except:
                            logger.error(traceback.format_exc())
                await client.disconnect()
            return chat_id
        except Exception:
            logger.info(f"channel {link}, account {account}")
            logger.error(traceback.format_exc())
        finally:
            if account != "main.session":
                await client.disconnect()
    else:
        try:
            res = await client(JoinChannelRequest(await client.get_input_entity(link)))
            chat_id = res.chats[0].id
            if account != "main.session":
                if spam3 and settings["spam3"] == True:
                    posts = await client(GetHistoryRequest(
                        peer=chat_id,
                        limit=3,
                        offset_date=None,
                        offset_id=0,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0))

                    for post in posts.messages:
                        try:
                            if os.path.exists("tmp.png"):
                                try:
                                    await client.send_file(chat_id, file="tmp.png", caption=settings["msg"], comment_to=post)
                                except:
                                    logger.error(traceback.format_exc())
                                    await client.send_message(chat_id, message=settings["msg"], comment_to=post)
                            else:
                                await client.send_message(chat_id, message=settings["msg"], comment_to=post)
                        except:
                            logger.error(traceback.format_exc())
                await client.disconnect()
            return res.chats[0].id
        except Exception:
            logger.info(f"channel {link}, account {account}")
            logger.error(traceback.format_exc())
        finally:
            if account != "main.session":
                await client.disconnect()

def get_accounts_dir():
    files = []
    for file in os.listdir("accounts"):
        if file.endswith(".session"):
            files.append(file)
    return files


@dp.message_handler(commands=["add_channels"], is_admin=True)
async def proxys_get(msg: Message):
    channels: dict = load_json("channels.txt")

    for channel in msg.get_args().split("\n"):
        for account in get_accounts_dir():
            if account == "main.session":
                chat_id = await join_channel(account, channel, client=main_client)
            else:
                chat_id = await join_channel(account, channel)
        if chat_id is not None:
            channels.update({chat_id:channel})
    with open("channels.txt", "w") as f:
        json.dump(channels, f)
    await msg.answer("Успішно!")
    channels_list = load_json("channels.txt")
    if len(channels_list) == 0:
        await msg.answer("Немає каналів")
        return
    await msg.answer("\n".join([f"{i} - {j}" for i, j in channels_list.items()]))

async def leave_channel(account: str, chat_id: int, client=None):
    try:
        if client is None:
            client = TelegramClient(
                f"accounts/{account}",
                api_id=API_ID,
                api_hash=API_HASH,
                # proxy=next(proxys)
                )
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                return
    except Exception:
        if account != "main.session":
            await client.disconnect()
        logger.info(f"account {account}")
        logger.error(traceback.format_exc())
        return
    try:
        res = await client(LeaveChannelRequest(await client.get_input_entity(int(chat_id))))
        if account != "main.session":
            await client.disconnect()
        return res.chats[0].id
    except Exception:
        logger.info(f"channel {chat_id}, account {account}")
        logger.error(traceback.format_exc())
    finally:
        if account != "main.session":
            await client.disconnect()

@dp.message_handler(commands=["del_channels"], is_admin=True)
async def proxys_get(msg: Message):
    channels: dict = load_json("channels.txt")

    for channel in msg.get_args().split("\n"):
        channels.pop(channel)
        for account in get_accounts_dir():
            if account == "main.session":
                await leave_channel(account, channel, client=main_client)
            else:
                await leave_channel(account, channel)
    with open("channels.txt", "w") as f:
        json.dump(channels, f)
    await msg.answer("Успішно!")
    channels_list = load_json("channels.txt")
    if len(channels_list) == 0:
        await msg.answer("Немає каналів")
        return
    await msg.answer("\n".join([f"{i} - {j}" for i, j in channels_list.items()]))

def save_settings():
    with open("settings.json", "w") as f:
        json.dump(settings,f)

@dp.message_handler(commands=["spam3_on"], is_admin=True)
async def spam3(msg: Message):
    global settings
    settings.update(spam3=True)
    save_settings()
    await msg.answer("Успішно включено")

@dp.message_handler(commands=["spam3_off"], is_admin=True)
async def spam3(msg: Message):
    global settings
    settings.update(spam3=False)
    save_settings()
    await msg.answer("Успішно виключено")

@dp.message_handler(commands=["set_count"], is_admin=True)
async def proxys_get(msg: Message):
    global settings
    settings.update(count_posts=int(msg.get_args().strip()))
    save_settings()
    await msg.answer("Успішно")

@dp.message_handler(lambda msg: msg.caption.startswith("/set_msg"), content_types=ContentType.PHOTO, is_admin=True)
async def proxys_get(msg: Message):
    global settings
    await msg.photo[-1].download(destination="tmp.png")
    settings.update(msg=msg.get_args())
    save_settings()
    await msg.answer("Успішно")


@dp.message_handler(commands=["del_img"], is_admin=True)
async def proxys_get(msg: Message):
    os.remove("tmp.png")
    await msg.answer("Успішно")


@dp.message_handler(commands=["set_msg"], content_types=ContentType.TEXT, is_admin=True)
async def proxys_get(msg: Message):
    global settings
    settings.update(msg=msg.get_args())
    save_settings()
    await msg.answer("Успішно")


@main_client.on(NewMessage())
async def my_event_handler(event: EventBuilder):
    global count_posts
    channels_list = load_json("channels.txt")
    chat = await event.get_chat()
    if chat is None:
        logger.info("none chat")
        return
    if str(event.chat.id) not in channels_list.keys():
        return
    if count_posts % int(settings["count_posts"]) != 0:
        return
    for account in get_accounts_dir():
        if account == "main.session":
            continue
        try:
            try:
                acc = TelegramClient(
                    f"accounts/{account}",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    # proxy=next(proxys)
                )
                await acc.connect()
                if not await acc.is_user_authorized():
                    await acc.disconnect()
                    continue
            except:
                await acc.disconnect()
                logger.error(traceback.format_exc())
                continue
            posts = await acc(GetHistoryRequest(
                    peer=event.message.chat.id,
                    limit=1,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0))

            post = posts.messages[0]
            try:
                if os.path.exists("tmp.png"):
                    try:
                        await acc.send_file(event.message.chat.id, file="tmp.png", caption=settings["msg"], comment_to=post)
                    except:
                        logger.error(traceback.format_exc())
                        await acc.send_message(event.message.chat.id, message=settings["msg"], comment_to=post)
                else:
                    await acc.send_message(event.message.chat.id, message=settings["msg"], comment_to=post)
            except:
                logger.error(traceback.format_exc())
            await acc.disconnect()
        except:
            await acc.disconnect()
            logger.error(traceback.format_exc())
            continue
        finally:
            await acc.disconnect()
        count_posts += 1
        break

async def on_startup(dispatcher: Dispatcher):
    await main_client.start()
    asyncio.create_task(main_client.run_until_disconnected())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)