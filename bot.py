import os
import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, InlineQueryHandler, CommandHandler, ContextTypes, CallbackQueryHandler
from uuid import uuid4

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ⚡ ТОКЕН НАПРЯМУЮ (для Render)
BOT_TOKEN = "8301531662:AAFMpn6fzibGRFiNHC42Ehlk6Cz988Y-zVQ"

private_messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Whisper Bot - Работает на Render!\n\n"
        "💡 Используйте: @whispertelegrammbot сообщение @username",
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Как использовать:\n\n"
        "1. Откройте любой чат\n"
        "2. Напишите: @whispertelegrammbot ваш_текст @username\n"
        "3. Выберите вариант из списка\n"
        "4. Отправьте сообщение!\n\n"
        "🔒 Текст сообщения видит только получатель!",
        parse_mode='HTML'
    )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.inline_query.query
        
        if not query:
            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="🤫 Секретное сообщение",
                    description="Формат: сообщение @username",
                    input_message_content=InputTextMessageContent(
                        "🔒 Секретное сообщение\n\n"
                        "💡 Напишите сообщение и @username получателя\n"
                        "📝 Текст сообщения будет скрыт от других",
                        parse_mode='HTML'
                    )
                )
            ]
            await update.inline_query.answer(results)
            return
        
        parts = query.split('@')
        if len(parts) < 2:
            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="❌ Используйте: сообщение @username",
                    description="Пример: Привет @username", 
                    input_message_content=InputTextMessageContent(
                        "❌ Неверный формат!\n✅ Правильно: сообщение @username"
                    )
                )
            ]
        else:
            message_text = parts[0].strip()
            username = '@' + parts[1].strip().split()[0]
            message_id = str(uuid4())
            
            private_messages[message_id] = {
                'text': message_text,
                'recipient': username.lower(),
                'sender': f"@{update.inline_query.from_user.username}" if update.inline_query.from_user.username else update.inline_query.from_user.first_name
            }
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔐 Прочитать сообщение", callback_data=f"view_{message_id}")
            ]])
            
            results = [
                InlineQueryResultArticle(
                    id=message_id,
                    title=f"🤫 Для {username}",
                    description="Нажмите чтобы отправить",
                    input_message_content=InputTextMessageContent(
                        f"🔒 <b>Секретное сообщение</b>\n\n"
                        f"👤 <b>Для:</b> {username}\n"
                        f"📄 <b>Есть 1 новое сообщение</b>\n\n"
                        f"<i>{username}, нажмите кнопку ниже чтобы прочитать</i>",
                        parse_mode='HTML'
                    ),
                    reply_markup=keyboard
                )
            ]
        
        await update.inline_query.answer(results, cache_time=1)
        
    except Exception as e:
        print(f"❌ Ошибка в inline_query: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith('view_'):
            message_id = query.data[5:]
            
            if message_id not in private_messages:
                await query.answer("❌ Сообщение не найдено", show_alert=True)
                return
            
            msg_data = private_messages[message_id]
            current_user_mention = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name
            
            if current_user_mention.lower() != msg_data['recipient']:
                await query.answer("❌ Это сообщение не для вас!", show_alert=True)
                return
            
            try:
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=f"💌 <b>Секретное сообщение для вас</b>\n\n"
                         f"👤 <b>От:</b> {msg_data['sender']}\n"
                         f"📝 <b>Сообщение:</b> {msg_data['text']}\n\n"
                         f"<i>Это сообщение видите только вы</i>",
                    parse_mode='HTML'
                )
                
                await query.edit_message_text(
                    f"✅ <b>Сообщение доставлено</b>\n\n"
                    f"👤 <b>Для:</b> {msg_data['recipient']}\n"
                    f"📝 <b>Тема:</b> Секретное сообщение\n\n"
                    f"<i>Получатель прочитал сообщение в ЛС</i>",
                    parse_mode='HTML'
                )
                
            except Exception:
                await query.answer("❌ Напишите @whispertelegrammbot в ЛС сначала!", show_alert=True)
                
    except Exception as e:
        print(f"❌ Ошибка в button_handler: {e}")

def main():
    print("🚀 Whisper Bot запускается на Render...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(InlineQueryHandler(inline_query))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Бот успешно запущен на Render!")
        print("👤 Юзернейм: @whispertelegrammbot")
        print("🌐 Бот работает 24/7!")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

    main()
