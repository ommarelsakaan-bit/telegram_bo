from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

CHOOSING, PHOTO, NAME, PHONE, ADDRESS = range(5)
ADMIN_ID = 6835389176
orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["شراء من الجروب"], ["التحدث مع شخص"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("اهلا بيك! اختار من الخيارات 👇", reply_markup=reply_markup)
    return CHOOSING

async def choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "التحدث مع شخص":
        await update.message.reply_text("تقدر تتواصل معانا على: 01500686879 أو +20 10 67065609")
        return ConversationHandler.END

    elif text == "شراء من الجروب":
        orders[user_id] = {}
        await update.message.reply_text("من فضلك ابعت صورة الحاجة اللي عايز تشتريها 📸")
        return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_id = update.message.photo[-1].file_id
    orders[user_id]["photo"] = photo_id
    await update.message.reply_text("تمام ✅ ابعت اسمك ثلاثي ✍️")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    orders[user_id]["name"] = update.message.text
    await update.message.reply_text("ابعت رقم موبايلك 📞")
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    orders[user_id]["phone"] = update.message.text
    await update.message.reply_text("ابعت عنوانك بالتفصيل 🏠")
    return ADDRESS

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    orders[user_id]["address"] = update.message.text

    name = orders[user_id]["name"]
    phone = orders[user_id]["phone"]
    address = orders[user_id]["address"]

    # رسالة للعميل
    await update.message.reply_text("تم استلام بياناتك ✅ سيتم مراجعة الطلب والتواصل معاك قريباً.")

    # زرار تأكيد الأوردر
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تأكيد الأوردر", callback_data=f"confirm_{user_id}")]
    ])

    # رسالة ليك انت (الأدمن)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📦 طلب جديد من عميل\n\n"
             f"👤 الاسم: {name}\n"
             f"📞 التليفون: {phone}\n"
             f"🏠 العنوان: {address}\n\n"
             f"ID: {user_id}",
        reply_markup=keyboard
    )
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=orders[user_id]["photo"])

    return ConversationHandler.END

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("🚫 الأمر ده للمشرف فقط")
        return

    user_id = int(query.data.split("_")[1])
    await context.bot.send_message(
        chat_id=user_id,
        text="✅ تم تأكيد الأوردر\nنتمنى لك الاستمتاع بالمنتج 🎉"
    )
    await query.edit_message_text("تم إرسال رسالة التأكيد للعميل ✅")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية ❌")
    return ConversationHandler.END

def main():
    app = Application.builder().token("8154389079:AAFE2cGvXvYvr-k_IVrVOATyfszMEz4v3BY").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(confirm_order, pattern="^confirm_"))

    app.run_polling()

if __name__ == "__main__":
    main()
