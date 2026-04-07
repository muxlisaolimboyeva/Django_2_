from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    InputMediaPhoto, LabeledPrice
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, ConversationHandler, \
    CallbackQueryHandler, PreCheckoutQueryHandler
import db

TOKEN = "8543377457:AAEyTb2mJDJAjTtXRDcPsUrYGiXfiDUvQRg"
PROVIDER_TOKEN = "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"

(
    NAME,
    PHONE,
    LOCATION,
    MAIN_MENU,
    EDIT_NAME,
    EDIT_PHONE,
    SETTINGS_MENU,
    FOOD_MENU
) = range(8)


def start(update: Update, context: CallbackContext):
    user = db.get_user(update.effective_user.id)

    if user:
        return main_menu(update, context)

    update.message.reply_text("👤 Ism familyangizni kiriting: ")
    return NAME


def get_name(update, context):
    context.user_data["name"] = update.message.text
    update.message.reply_text("📞 Telefon raqamingizni yuboring: ",
                              reply_markup=ReplyKeyboardMarkup(
                                  [[KeyboardButton("Raqami yuborish 📱", request_contact=True)]],
                                  resize_keyboard=True
                              ))
    return PHONE


def get_phone(update, context):
    context.user_data["phone"] = update.message.contact.phone_number
    update.message.reply_text("📍 Maznizlingizni kirting: ",
                              reply_markup=ReplyKeyboardMarkup(
                                  [[KeyboardButton("📍 Manzili kiriting", request_location=True)]],
                                  resize_keyboard=True
                              ))
    return LOCATION


def get_location(update, context):
    loc = update.message.location

    db.add_user(
        update.effective_user.id,
        context.user_data["name"],
        context.user_data["phone"],
        loc.latitude,
        loc.longitude
    )

    update.message.reply_text("Ro'yhatdan o'tdingiz ✅")
    return main_menu(update, context)


def main_menu(update, context):
    update.message.reply_text(
        "Asosiy menu: ",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["📋 Menyu", "🛒 Savat"],
                ["⚙️ Sozlamalar", ],
                ["💬 Izoh qoldirish"]
            ],
            resize_keyboard=True
        )
    )
    return MAIN_MENU


def main_menu_select(update, context):
    text = update.message.text

    if text == "🛒 Savat":
        return show_cart(update, context)
    if text == "📋 Menyu":
        return food_menu(update, context)
    if text == "⚙️ Sozlamalar":
        return settings_menu(update, context)
    if text == "💬 Izoh qoldirish":
        update.message.reply_text("Izpj yozishingiz mumkin, lekin hozr ishlamaydi !")
        return MAIN_MENU


def food_menu(update, context):
    update.message.reply_text(
        "Menyulardan birini tanlang: ",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["Lavashlar 🌯", "Burgerlar 🍔"],
                ["Shashliklar 🍡", "Sushilar 🍣"],
                ["⬅️ Orqaga"],
            ],
            resize_keyboard=True
        )
    )
    return FOOD_MENU


# 1 - chi bo'lib | food_menu_select ni o‘zgartiramiz
def food_menu_select(update, context):
    text = update.message.text

    if update.message.text == "Lavashlar 🌯":
        products = db.get_products_by_category("lavash")

        keyboard = [
            [InlineKeyboardButton(p[1], callback_data=f"product_{p[0]}")]
            for p in products
        ]

        update.message.reply_text(
            "Lavash tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return FOOD_MENU

    if text == "⬅️ Orqaga":
        return main_menu(update, context)


# 2 - chi
def product_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # eski mahsulot kartasini o‘chiramiz
    old_msg_id = context.user_data.get("product_message_id")
    if old_msg_id:
        try:
            context.bot.delete_message(
                chat_id=query.message.chat_id,
                message_id=old_msg_id
            )
        except:
            pass

    product_id = int(query.data.split("_")[1])
    product = db.get_products(product_id)

    context.user_data["current_product"] = {
        "id": product[0],
        "name": product[1],
        "price": product[2],
        "desc": product[3],
        "image": product[4]
    }
    context.user_data["qty"] = 1

    msg = query.message.reply_photo(
        photo=open("rasm.png", "rb"),
        caption=(
            f"*{product[1]}*\n\n"
            f"💰 Narx: {product[2]} so‘m\n"
            f"📦 Miqdor: 1\n\n"
            f"📝 {product[3]}"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➖", callback_data="qty_minus"),
                InlineKeyboardButton("1", callback_data="noop"),
                InlineKeyboardButton("➕", callback_data="qty_plus"),
            ],
            [InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_to_cart")]
        ])
    )

    context.user_data["product_message_id"] = msg.message_id


# 3 - chi
def send_product_card_first(query, context):
    product = context.user_data["current_product"]
    qty = context.user_data["qty"]

    keyboard = [
        [
            InlineKeyboardButton("➖", callback_data="qty_minus"),
            InlineKeyboardButton(str(qty), callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="qty_plus"),
        ],
        [
            InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_to_cart")
        ]
    ]

    caption = (
        f"*{product['name']}*\n\n"
        f"💰 Narx: {product['price']} so‘m\n"
        f"📦 Miqdor: {qty}\n\n"
        f"📝 {product['desc']}"
    )

    query.message.reply_photo(
        photo=open("rasm.png", "rb"),
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def send_product_card_update(query, context):
    # 🛡️ Agar bu xabarda rasm bo‘lmasa — chiqib ketamiz
    if not query.message.photo:
        return

    product = context.user_data.get("current_product")
    qty = context.user_data.get("qty", 1)

    if not product:
        return

    keyboard = [
        [
            InlineKeyboardButton("➖", callback_data="qty_minus"),
            InlineKeyboardButton(str(qty), callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="qty_plus"),
        ],
        [
            InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_to_cart")
        ]
    ]

    caption = (
        f"*{product['name']}*\n\n"
        f"💰 Narx: {product['price']} so‘m\n"
        f"📦 Miqdor: {qty}\n\n"
        f"📝 {product['desc']}"
    )

    query.edit_message_caption(
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 4 - chi
def cart_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if not query.message.photo:
        return

    product = context.user_data.get("current_product")
    if not product:
        return

    qty = context.user_data.get("qty", 1)

    if query.data == "qty_plus":
        qty += 1

    elif query.data == "qty_minus":
        if qty > 1:
            qty -= 1

    elif query.data == "add_to_cart":
        context.user_data.setdefault("cart", []).append({
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "qty": qty
        })
        query.message.reply_text("✅ Mahsulot savatga qo‘shildi")
        return

    # yangilangan qty ni saqlaymiz
    context.user_data["qty"] = qty

    # 🔥 YANGI keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖", callback_data="qty_minus"),
            InlineKeyboardButton(str(qty), callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="qty_plus"),
        ],
        [
            InlineKeyboardButton("🛒 Savatga qo‘shish", callback_data="add_to_cart")
        ]
    ])

    # 🔥 faqat caption + keyboard yangilanadi
    query.edit_message_caption(
        caption=(
            f"*{product['name']}*\n\n"
            f"💰 Narx: {product['price']} so‘m\n"
            f"📦 Miqdor: {qty}\n\n"
            f"📝 {product['desc']}"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


def settings_menu(update, context):
    update.message.reply_text("Ma'lumotlarni tahrirlash: ",
                              reply_markup=ReplyKeyboardMarkup(
                                  [
                                      ["✏️ Ism familya"],
                                      ["📞 Telefon raqam"],
                                      ["⬅️ Orqaga"]
                                  ],
                                  resize_keyboard=True
                              ))
    return SETTINGS_MENU


def settings_select(update, context):
    text = update.message.text

    if text == "✏️ Ism familya":
        update.message.reply_text("Yangi Ism fmailyani kiriting: ")
        return EDIT_NAME

    if text == "📞 Telefon raqam":
        update.message.reply_text("📞Yangi telefon raqam yuoring: ",
                                  reply_markup=ReplyKeyboardMarkup(
                                      [[KeyboardButton("📱 Raqam yuborish", request_contact=True)]],
                                      resize_keyboard=True
                                  )
                                  )
        return EDIT_PHONE

    if text == "⬅️ Orqaga":
        return main_menu(update, context)


def edit_name(update, context):
    db.update_name(update.effective_user.id, update.message.text)
    update.message.reply_text("Ism Familya muvofaqiyatli o'zgartirildi ✅")
    return main_menu(update, context)


def edit_phone(update, context):
    db.update_phone(update.effective_user.id, update.message.contact.phone_number)
    update.message.reply_text("Telefon raqam muvofaqiyatli o'zgartirildi ✅")
    return main_menu(update, context)


def show_cart(update, context):
    cart = context.user_data.get("cart")

    if not cart:
        update.message.reply_text("🛒 Savat bo‘sh")
        return MAIN_MENU

    text = "🛒 Savatingiz:\n\n"
    total = 0

    for item in cart:
        summa = item["price"] * item["qty"]
        total += summa
        text += f"{item['name']} x {item['qty']} = {summa} so'm\n"

    text += f"\n💰 Jami: {total} so'm"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Buyurtma berish", callback_data="order_confirm"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="order_cancel")
        ]
    ])

    update.message.reply_text(text, reply_markup=keyboard)
    return MAIN_MENU


def order_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "order_confirm":
        cart = context.user_data.get("cart", [])

        if not cart:
            query.message.reply_text("Savat bo'sh !")
            return

        prices = []
        total = 0

        for item in cart:
            amount = item["price"] * item['qty']
            total += amount
            prices.append(
                LabeledPrice(
                    label=f"{item['name']} x{['qty']}",
                    amount=amount * 100
                ))

        context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title="Buyurtma uchun to'lov",
            description="Buyurta tasdiqlash uchun to'lov amalga oshiring !",
            payload="order_payment_payload",
            provider_token=PROVIDER_TOKEN,
            currency="UZS",
            prices=prices,
            start_parameter="food_order"
        )

    elif query.data == "order_cancel":
        context.user_data["cart"] = []
        query.message.delete()
        query.message.chat.send_message("Buyurtma bekor qilindi ❌")


def precheckout_callback(update: Update, context: CallbackContext):
    update.pre_checkout_query.answer(ok=True)


def successful_payment_callback(update: Update, context: CallbackContext):
    context.user_data["cart"] = []

    update.message.reply_text(
        "To'lov muvofaqiyatli amalga oshirildi !\n"
        "Buyurtma qabul qilindi !"
    )


def main():
    db.create_table()
    db.seed_data()

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(Filters.text, get_name)],
            PHONE: [MessageHandler(Filters.contact, get_phone)],
            LOCATION: [MessageHandler(Filters.location, get_location)],

            MAIN_MENU: [MessageHandler(Filters.text, main_menu_select)],
            SETTINGS_MENU: [MessageHandler(Filters.text, settings_select)],
            FOOD_MENU: [MessageHandler(Filters.text, food_menu_select)],

            EDIT_NAME: [MessageHandler(Filters.text, edit_name)],
            EDIT_PHONE: [MessageHandler(Filters.contact, edit_phone)]
        },
        fallbacks=[],
    )

    dp.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer(), pattern="^noop$"))
    dp.add_handler(CallbackQueryHandler(product_callback, pattern="^product_"))
    dp.add_handler(CallbackQueryHandler(cart_callback, pattern="^(qty_|add_to_cart)"))
    dp.add_handler(CallbackQueryHandler(order_callback, pattern="^order_"))

    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))

    dp.add_handler(conv)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
