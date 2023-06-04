# Copas Teriak Copas MONYET
# Gay Teriak Gay Anjeng
# @Rizzvbss | @Kenapanan
# Kok Bacot
# © @KynanSupport | Nexa_UB
# FULL MONGO NIH JING FIX MULTI CLIENT
from pyrogram.raw.functions.messages import DeleteHistory

from . import *

PM_GUARD_WARNS_DB = {}
PM_GUARD_MSGS_DB = {}

DEFAULT_TEXT = """
**Saya adalah Naya-Premium yang menjaga Room Chat Ini . Jangan Spam Atau Anda Akan Diblokir Otomatis.**
"""

PM_WARN = """
**Halo  {} 👋 .
Pesan Keamanan Milik {} 👮!**

{}

**Anda memiliki `{}/{}` peringatan . Hati-hati !**
"""

LIMIT = 5

flood = {}


class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0


LOG_CHATS_ = LOG_CHATS()


@bots.on_message(filters.command(["pmpermit", "antipm"], cmd) & filters.me)
async def permitpm(client, message):
    user_id = client.me.id
    babi = await message.edit("`Processing...`")
    bacot = get_arg(message)
    if not bacot:
        return await babi.edit(f"**Gunakan Format : `{cmd[0]}pmpermit on or off`.**")
    is_already = await get_var(user_id, "ENABLE_PM_GUARD")
    if bacot.lower() == "on":
        if is_already:
            return await babi.edit("`PMPermit Sudah DiHidupkan.`")
        await set_var(user_id, "ENABLE_PM_GUARD", True)
        await babi.edit("**PMPermit Berhasil DiHidupkan.**")
    elif bacot.lower() == "off":
        if not is_already:
            return await babi.edit("`PMPermit Sudah DiMatikan.`")
        await set_var(user_id, "ENABLE_PM_GUARD", False)
        await babi.edit("**PMPermit Berhasil DiMatikan.**")
    else:
        await babi.edit(f"**Gunakan Format : `{cmd[0]}pmpermit on or off`.**")


@bots.on_message(filters.command(["ok", "a"], cmd) & filters.me)
async def approve(client, message):
    babi = await message.edit("`Processing...`")
    chat_type = message.chat.type
    if chat_type == "me":
        return await babi.edit("`Apakah anda sudah gila ?`")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not message.reply_to_message.from_user:
            return await babi.edit("`Balas ke pesan pengguna, untuk disetujui.`")
        user_id = message.reply_to_message.from_user.id
    elif chat_type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
    else:
        return
    already_apprvd = await check_user_approved(user_id)
    if already_apprvd:
        return await babi.edit("`Manusia ini sudah Di Setujui Untuk mengirim pesan.`")
    await add_approved_user(user_id)
    if user_id in PM_GUARD_WARNS_DB:
        PM_GUARD_WARNS_DB.pop(user_id)
        try:
            await client.delete_messages(
                chat_id=user_id, message_ids=PM_GUARD_MSGS_DB[user_id]
            )
        except:
            pass
    await babi.edit("**Baiklah, pengguna ini sudah disetujui untuk mengirim pesan.**")


@bots.on_message(filters.command(["no", "da"], cmd) & filters.me)
async def disapprove(client, message):
    babi = await message.edit("`Processing...`")
    chat_type = message.chat.type
    if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not message.reply_to_message.from_user:
            return await babi.edit("`Balas ke pesan pengguna, untuk ditolak.`")
        user_id = message.reply_to_message.from_user.id
    elif chat_type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
    else:
        return
    already_apprvd = await check_user_approved(user_id)
    if not already_apprvd:
        return await babi.edit(
            "`Manusia ini memang belum Di Setujui Untuk mengirim pesan.`"
        )
    await rm_approved_user(user_id)
    await babi.edit("**Baiklah, pengguna ini ditolak untuk mengirim pesan.**")


@bots.on_message(filters.command(["setmsg"], cmd) & filters.me)
async def set_msg(client, message):
    babi = await message.edit("`Processing...`")
    user_id = client.me.id
    r_msg = message.reply_to_message
    args_txt = get_arg(message)
    if r_msg:
        if r_msg.text:
            pm_txt = r_msg.text
        else:
            return await babi.edit(
                "`Silakan balas ke pesan untuk dijadikan teks PMPermit !`"
            )
    elif args_txt:
        pm_txt = args_txt
    else:
        return await babi.edit(
            "`Silakan balas ke pesan atau berikan pesan untuk dijadikan teks PMPermit !\n**Contoh :** {cmd[0]}setmsg Halo saya anuan`"
        )
    await set_var(user_id, "CUSTOM_PM_TEXT", pm_txt)
    await babi.edit(f"**Pesan PMPemit berhasil diatur menjadi : `{pm_txt}`.**")


@bots.on_message(filters.command(["setlimit"], cmd) & filters.me)
async def set_limit(client, message):
    babi = await message.edit("`Processing...`")
    user_id = client.me.id
    args_txt = get_arg(message)
    if args_txt:
        if args_txt.isnumeric():
            pm_warns = int(args_txt)
        else:
            return await babi.edit("`Silakan berikan untuk angka limit !`")
    else:
        return await babi.edit(
            f"`Silakan berikan pesan untuk dijadikan angka limit !\n**Contoh :** {PREFIX[0]}setlimit 5`"
        )
    await set_var(user_id, "CUSTOM_PM_WARNS_LIMIT", pm_warns)
    await babi.edit(f"**Pesan Limit berhasil diatur menjadi : `{args_txt}`.**")


@bots.on_message(
    filters.private
    & filters.incoming
    & ~filters.service
    & ~filters.me
    & ~filters.bot
    & ~filters.via_bot
)
async def pmpermit_func(client, message, victim):
    org = message.from_user.id
    gua = client.me.id
    chat_id = message.chat.id
    biji = message.from_user.mention
    botlog = await get_log_groups(gua)
    is_pm_guard_enabled = await get_var(gua, "ENABLE_PM_GUARD")
    if message.chat.id != 777000:
        if LOG_CHATS_.RECENT_USER != message.chat.id:
            LOG_CHATS_.RECENT_USER = message.chat.id
            if LOG_CHATS_.NEWPM:
                await LOG_CHATS_.NEWPM.edit(
                    LOG_CHATS_.NEWPM.text.replace(
                        "**💌 #NEW_MESSAGE**",
                        f" • `{LOG_CHATS_.COUNT}` **Pesan**",
                    )
                )
                LOG_CHATS_.COUNT = 0
            LOG_CHATS_.NEWPM = await client.send_message(
                botlog,
                f"💌 <b><u>MENERUSKAN PESAN BARU</u></b>\n<b> • Dari :</b> {biji}\n<b> • User ID :</b> <code>{org}</code>\n",
                parse_mode=enums.ParseMode.HTML,
            )
        try:
            async for pmlog in client.search_messages(message.chat.id, limit=1):
                await pmlog.forward(botlog)
            LOG_CHATS_.COUNT += 1
        except BaseException:
            pass
    if not is_pm_guard_enabled or await check_user_approved(org):
        return
    elif org in DEVS:
        try:
            await add_approved_user(chat_id)
            await client.send_message(
                chat_id,
                f"<b>Menerima Pesan Dari {biji} !!\nTerdeteksi Developer Dari Naya-Premium.</b>",
                parse_mode=enums.ParseMode.HTML,
            )
        except:
            pass
        return
    async for m in client.get_chat_history(org, limit=6):
        if m.reply_markup:
            await m.delete()
    if str(org) in flood:
        flood[str(org)] += 1
    else:
        flood[str(org)] = 1
    if flood[str(org)] > 5:
        await message.reply_text("SPAM DETECTED, BLOCKED USER AUTOMATICALLY!")
        return await client.block_user(org)
    results = await client.get_inline_bot_results(app.me.username, f"pmpermit {org}")
    await client.send_inline_bot_result(
        org,
        results.query_id,
        results.results[0].id,
    )


flood2 = {}


@app.on_callback_query(filters.regex("pmpermit"))
async def pmpermit_cq(_, cq, victim):
    user_id = cq.from_user.id
    data, victim = (
        cq.data.split(None, 2)[1],
        cq.data.split(None, 2)[2],
    )
    if data == "approve":
        if user_id != client.me.id:
            return await cq.answer("Bukan untuk anda.")
        await add_approved_user(int(victim))
        return await app.edit_inline_text(
            cq.inline_message_id, "Baiklah pengguna ini sudah disetujui."
        )

    if data == "block":
        if user_id != client.me.id:
            return await cq.answer("Bukan untuk anda.")
        await cq.answer()
        await app.edit_inline_text(cq.inline_message_id, "Aavv Di Blok.")
        await bots.block_user(int(victim))
        return await bots.invoke(
            DeleteHistory(
                peer=(await bots.resolve_peer(victim)),
                max_id=0,
                revoke=False,
            )
        )

    if user_id == client.me.id:
        return await cq.answer("Untuk manusia lain.")

    if data == "to_scam_you":
        async for m in bots.get_chat_history(user_id, limit=6):
            if m.reply_markup:
                await m.delete()
        await bots.send_message(user_id, "Blocked, Go scam someone else.")
        await bots.block_user(user_id)
        await cq.answer()

    elif data == "approve_me":
        await cq.answer()
        if str(user_id) in flood2:
            flood2[str(user_id)] += 1
        else:
            flood2[str(user_id)] = 1
        if flood2[str(user_id)] > 5:
            await bots.send_message(user_id, "SPAM DETECTED, USER BLOCKED.")
            return await bots.block_user(user_id)
        await bots.send_message(
            user_id,
            "I'm busy right now, will approve you shortly, DO NOT SPAM.",
        )


@app.on_inline_query()
async def pmpermit_func(answers, user_id, victim):
    if user_id != client.me.id:
        return
    caption = f"Hi, I'm {bot.me.first_name}, What are you here for?, You'll be blocked if you send more than 5 messages."
    buttons = InlineKeyboard(row_width=2)
    buttons.add(
        InlineKeyboardButton(
            text="To Scam You", callback_data="pmpermit to_scam_you a"
        ),
        InlineKeyboardButton(
            text="For promotion",
            callback_data="pmpermit to_scam_you a",
        ),
        InlineKeyboardButton(text="Approve me", callback_data="pmpermit approve_me a"),
        InlineKeyboardButton(
            text="Approve", callback_data=f"pmpermit approve {victim}"
        ),
        InlineKeyboardButton(
            text="Block & Delete",
            callback_data=f"pmpermit block {victim}",
        ),
    )
    answers.append(
        InlineQueryResultArticle(
            title="do_not_click_here",
            reply_markup=buttons,
            input_message_content=InputTextMessageContent(caption),
        )
    )
    return answers


__MODULE__ = "antipm"
__HELP__ = f"""
✘ Bantuan Untuk PM Permit

๏ Perintah: <code>{cmd}pmpermit</code> [on atau off]
◉ Penjelasan: Untuk menghidupkan atau mematikan antipm

๏ Perintah: <code>{cmd}setmsg</code> [balas atau berikan pesan]
◉ Penjelasan: Untuk mengatur pesan antipm.

๏ Perintah: <code>{cmd}setlimit</code> [angka]
◉ Penjelasan: Untuk mengatur peringatan pesan blokir.

๏ Perintah: <code>{cmd}ok or a</code>
◉ Penjelasan: Untuk menyetujui pesan.

๏ Perintah: <code>{cmd}no or da</code>
◉ Penjelasan: Untuk menolak pesan.
"""
