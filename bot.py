import os, logging, asyncio

from telethon.errors import UserNotParticipantError
from telethon.sessions import MemorySession
from telethon import Button
from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

client = TelegramClient(MemorySession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

spam_chats = []

@client.on(events.NewMessage(pattern="^/start$"))
async def start(event):
  await event.reply(
    "__**Saya Kang Tag Robot**, saya bisa mention hampir semua member di grup atau channel 👻\nKlik **/help** untuk informasi lebih lanjut",
    link_preview=False,
    buttons=(
      [
        Button.url("Developer", "https://t.me/mazekubot"),
        Button.url("Support", f"https://t.me/dutabotid")
      ]
    )
  )

@client.on(events.NewMessage(pattern="^/help$"))
async def help(event):
  helptext = "**Menu Bantuan Kang Tag Robot**\n\nPerintah: /all\n__Anda dapat menggunakan perintah ini dengan teks apa yang ingin Anda sebutkan kepada orang lain.__\n`Contoh: @all Selamat Pagi!`\n__Anda dapat menggunakan perintah ini sebagai balasan untuk pesan apa pun. Bot akan menandai pengguna ke pesan balasan itu__."
  await event.reply(
    helptext,
    link_preview=False,
    buttons=(
      [
        Button.url("Developer", "https://t.me/mazekubot"),
        Button.url("Support", f"https://t.me/dutabotid")
      ]
    )
  )
  
@client.on(events.NewMessage(pattern="^/tagall|/call|/tall|/all|/mentionall|#all|@all?(.*)"))
async def mentionall(event):
  chat_id = event.chat_id
  if event.is_private:
    return await event.respond("__Perintah ini hanya dapat digunakan di dalam grup dan channel!__")
  
  is_admin = False
  try:
    partici_ = await client(GetParticipantRequest(
      event.chat_id,
      event.sender_id
    ))
  except UserNotParticipantError:
    is_admin = False
  else:
    if (
      isinstance(
        partici_.participant,
        (
          ChannelParticipantAdmin,
          ChannelParticipantCreator
        )
      )
    ):
      is_admin = True
  if not is_admin:
    return await event.respond("__Hanya admin yang bisa menyebutkan semuanya!__")
  
  if event.pattern_match.group(1) and event.is_reply:
    return await event.respond("__Beri aku satu argumen!__")
  elif event.pattern_match.group(1):
    mode = "text_on_cmd"
    msg = event.pattern_match.group(1)
  elif event.is_reply:
    mode = "text_on_reply"
    msg = await event.get_reply_message()
    if msg == None:
        return await event.respond("__Saya tidak bisa menyebutkan anggota untuk pesan lama! (pesan yang dikirim sebelum saya ditambahkan ke grup)__")
  else:
    return await event.respond("__Balas pesan atau beri saya beberapa teks untuk menyebutkan orang lain!__")
  
  spam_chats.append(chat_id)
  usrnum = 0
  usrtxt = ''
  async for usr in client.iter_participants(chat_id):
    if not chat_id in spam_chats:
      break
    usrnum += 1
    usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}) "
    if usrnum == 5:
      if mode == "text_on_cmd":
        txt = f"{usrtxt}\n\n{msg}"
        await client.send_message(chat_id, txt)
      elif mode == "text_on_reply":
        await msg.reply(usrtxt)
      await asyncio.sleep(2)
      usrnum = 0
      usrtxt = ''
  try:
    spam_chats.remove(chat_id)
  except:
    pass

@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
  if not event.chat_id in spam_chats:
    return await event.respond('__Tidak ada proses yang sedang berjalan...__')
  else:
    try:
      spam_chats.remove(event.chat_id)
    except:
      pass
    return await event.respond('__Stopped.__')

print("BOT STARTED")
client.run_until_disconnected()
