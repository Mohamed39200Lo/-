import telebot
import re
import time
import logging
import json
from telebot import types
from urllib.parse import urlparse

from server import server
import threading
def load_data():
    try:
        with open('bot_data.json', 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:

        return {
            "forbidden_words": ["عييييلل", 'كلممة6', 'كلمممة4'],
            "warnings_count": {},  # Added line
            "allowed_admins": [111110,5565868245,6688304706],
            "qa_dict": {
                "السلام عليكم": "وعليكم السلام",
                "كيف حالك": "أنا بخير، شكراً!",
                "ما هو اسمك": "أنا بوت محادثة تمثيلي."
            },
            "forwarded_warnings": {},
            "members_warnings": {}
        }

def save_data(data):
    with open('bot_data.json', 'w') as file:
        json.dump(data, file)

bot_data = load_data()

# Load data
bot_data = load_data()
forbidden_words = bot_data["forbidden_words"]
warnings_count = bot_data["warnings_count"]
allowed_admins = bot_data["allowed_admins"]
qa_dict = bot_data["qa_dict"]
forwarded_warnings = bot_data.get("forwarded_warnings", {})
members_warnings = bot_data.get("members_warnings", {})



warnings_count = bot_data.get("warnings_count", {})


logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

bot_token = "6751478105:AAHbzdQam6OiGoPcFsh6cye7eSoo89mN6ao"
bot = telebot.TeleBot(bot_token)

...

@bot.message_handler(commands=['control'])
def control_command(message):
    if message.from_user.id in allowed_admins:

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        add_admins_button = types.InlineKeyboardButton("اضافة مشرفين للبوت", callback_data='add_admins')
        add_forbidden_words_button = types.InlineKeyboardButton("إضافة كلمات محظورة", callback_data='add_forbidden_words')
        qa_button = types.InlineKeyboardButton("اضافة الردود على الاسئلة", callback_data='manage_qa')

        keyboard.add(add_admins_button, add_forbidden_words_button, qa_button)

        bot.send_message(message.chat.id, "اختر الإجراء:", reply_markup=keyboard)
    else:
        bot.reply_to(message, "أنت ليس لديك صلاحيات لتنفيذ هذا الأمر.")

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.from_user.id in allowed_admins:
        if call.data == 'add_admins':
            bot.send_message(call.message.chat.id, "أرسل معرف المشرف الذي تريد إضافته:")
            bot.register_next_step_handler(call.message, process_admin_input)
        elif call.data == 'add_forbidden_words':
            bot.send_message(call.message.chat.id, "أرسل الكلمات المحظورة بفاصلة:")
            bot.register_next_step_handler(call.message, process_forbidden_words_input)
        elif call.data == 'manage_qa':
            bot.send_message(call.message.chat.id, "إدارة الأسئلة والأجوبة\nأدخل السؤال:")
            bot.register_next_step_handler(call.message, process_question_input)

# Function to process QA input
def process_question_input(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in allowed_admins:
        question = message.text
        bot.send_message(chat_id, f"تم استلام السؤال: {question}\nأدخل الإجابة على هذا السؤال:")
        bot.register_next_step_handler(message, lambda m: process_answer_input(m, question))

        save_data(bot_data)

def process_answer_input(message, question):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in allowed_admins:
        answer = message.text
        qa_dict[question] = answer
        bot.send_message(chat_id, f"تمت إضافة السؤال والإجابة بنجاح.")

        bot_data["warnings_count"] = warnings_count
        save_data(bot_data)

def show_qa_menu(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for question in qa_dict.keys():
        button = types.InlineKeyboardButton(question, callback_data=f'qa_{question}')
        keyboard.add(button)

    back_button = types.InlineKeyboardButton("رجوع", callback_data='back_to_main')
    keyboard.add(back_button)

    bot.send_message(message.chat.id, "اختر سؤالًا للإدارة:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('qa_'))
def handle_qa_buttons(call):
    question = call.data.replace('qa_', '')
    bot.send_message(call.message.chat.id, f"السؤال: {question}\nالإجابة: {qa_dict.get(question, 'لم يتم تعيين إجابة')}")

def process_admin_input(message):
    try:
        admin_id = int(message.text)
        allowed_admins.append(admin_id)
        bot.send_message(message.chat.id, f"تمت إضافة المشرف {admin_id} بنجاح.")

        save_data(bot_data)
    except ValueError:
        bot.send_message(message.chat.id, "خطأ! يرجى إرسال معرف المشرف كرقم.")

def process_forbidden_words_input(message):
    words_list = message.text.split(',')
    forbidden_words.extend(words_list)
    bot.send_message(message.chat.id, "تمت إضافة الكلمات المحظورة بنجاح.")

    save_data(bot_data)

def is_administrator(chat_id, user_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        if "user not found" in str(e):
            return False
        else:
            raise

def contains_inline_url(text):
    parsed_url = urlparse(text)
    return bool(parsed_url.scheme)

channel_id = -1001899111230
"""
def check_subscription(message):
    user_id = message.from_user.id

    try:

        chat_member = bot.get_chat_member(channel_id, user_id)


        is_subscribed = chat_member.status in ['member', 'administrator', 'creator']
        is_allowed_admin = user_id in allowed_admins


        if not is_subscribed and not is_allowed_admin:

            reply_message = bot.reply_to(message, "يجب عليك الاشتراك في القناة للسماح لك بإرسال الرسائل هنا @layth_forix7")
            time.sleep(1)
            bot.delete_message(message.chat.id, message.message_id)


            threading.Timer(90, delete_message, args=[message.chat.id, reply_message.message_id]).start()

    except Exception as e:

        print(f"An error occurred: {e}")
"""        
def check_telegram_caption(message):
    if message.caption:
        caption = message.caption
        if "@" in caption or "t.me/" in caption or "https://t.me/" in caption:
            try:

                if message.from_user.id not in allowed_admins:
                    bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time()) + 604800)
                    reply_message = bot.reply_to(message, f"تم تقييدك لمدة أسبوع بسبب ارسال الروابط.\nID العضو: {message.from_user.id}")

                    threading.Timer(100, delete_message, args=[message.chat.id, reply_message.message_id]).start()
                    bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:

                print(f"An error occurred: {e}")


def delete_message(chat_id, message_id):
    bot.delete_message(chat_id, message_id)


def check_inline_urls_in_caption(message):
    if message.caption:
        entities = message.caption_entities
        if entities:
            for entity in entities:
                if entity.type == 'text_link':
                    try:

                        if message.from_user.id not in allowed_admins:

                            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=int(time.time()) + 604800)

                            bot.reply_to(message, f"تم تقييدك لمدة أسبوع بسبب وجود روابط الرسالة.\nID العضو: {message.from_user.id}")

                            bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:

                        print(f"An error occurred: {e}")




@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio'])

def check(message):
    global warnings_count
    global forwarded_warnings
    global members_warnings
    #check_subscription(message)
    check_telegram_caption(message)
    check_inline_urls_in_caption(message)

    try:
        if message.reply_to_message and "ازعاج" in message.text.lower():
            replied_user_id = message.reply_to_message.from_user.id
            replier_user_id = message.from_user.id

            if replied_user_id not in members_warnings:
                members_warnings[replied_user_id] = [replier_user_id]
            else:
                members_warnings[replied_user_id].append(replier_user_id)

            if len(set(members_warnings[replied_user_id])) >= 5:
                members_warnings[replied_user_id] = []


                bot.restrict_chat_member(message.chat.id, replied_user_id, until_date=int(time.time()) + 604800)
                bot.reply_to(message.reply_to_message, f"تم تقييد العضو {replied_user_id} لمدة أسبوع بسبب التكرار في الازعاج.")


            bot_data["members_warnings"] = members_warnings
            save_data(bot_data)


        if message.forward_from_chat and not message.forward_from_chat.id in allowed_admins:
            if message.from_user.id not in allowed_admins:
                unique_identifier = f"{message.from_user.id}_{message.chat.id}"
                user_id = message.from_user.id


                forwarded_warnings[unique_identifier] = forwarded_warnings.get(unique_identifier, 0) + 1

                if forwarded_warnings.get(unique_identifier, 0) == 1:
                    warning_message = f"المعرف: {user_id}\n"
                    warning_message += "تحذير تحويل الرسائل غير مسموح به اذا تكرر الامر سيتم حظرك"
                    bot.reply_to(message, warning_message)

                    bot.delete_message(message.chat.id, message.message_id)


                elif forwarded_warnings.get(unique_identifier, 0) >= 2:
                    bot.delete_message(message.chat.id, message.message_id)

                    bot.kick_chat_member(message.chat.id, message.from_user.id)
                    bot.send_message(message.chat.id, f"تم حظر العضو بمعرف {message.from_user.id} بسبب تكرار إعادة إرسال الرسائل.")

                    forwarded_warnings[unique_identifier] = 0

                bot_data["forwarded_warnings"] = forwarded_warnings
                save_data(bot_data)

                return

        if message.text:
            user_id = message.from_user.id
            chat_id = message.chat.id

            unique_identifier = f"{user_id}_{chat_id}"

            if message.from_user.id in allowed_admins and message.reply_to_message:
                if "انذار" in message.text.lower():
                    user_id = message.reply_to_message.from_user.id
                    warnings_count[unique_identifier] = warnings_count.get(unique_identifier, 0) + 1

                    warning_message = f"تم اضافة تحذير \n"
                    warning_message += f"لديك الآن {warnings_count.get(unique_identifier, 0)} تحذيرات."
                    bot.reply_to(message.reply_to_message, warning_message)
                    #threading.Thread(target=delete_warning_message, args=(warning_reply,)).start()

                    if warnings_count.get(unique_identifier, 0) >= 2:
                        warnings_count[unique_identifier] = 0
                        bot.restrict_chat_member(message.chat.id, user_id, until_date=int(time.time()) +172800)

                        bot.reply_to(message.reply_to_message, f"تم تقييدك لمدة يومين بسبب تجاوز عدد التحذيرات.")
                        warnings_count[unique_identifier] = 0

                    bot_data["warnings_count"] = warnings_count
                    save_data(bot_data)

                elif "طرد" in message.text.lower():
                    user_id_to_ban = message.reply_to_message.from_user.id
                    if not is_administrator(message.chat.id, user_id_to_ban):
                        bot.kick_chat_member(message.chat.id, user_id_to_ban)
                        bot.reply_to(message.reply_to_message, f"تم حظر العضو {user_id_to_ban}")
                    else:
                        bot.reply_to(message, "لا يمكن حظر المشرفين.")

                elif "تقييد" in message.text.lower():
                    user_to_restrict_id = message.reply_to_message.from_user.id
                    if not is_administrator(message.chat.id, user_to_restrict_id):
                        bot.restrict_chat_member(message.chat.id, user_to_restrict_id, until_date=int(time.time()) + 604800)
                        bot.reply_to(message.reply_to_message, f"تم تقييد العضو {user_to_restrict_id} لمدة اسبوع بواسطة المشرف")
                    else:
                        bot.reply_to(message, "لا يمكن تقييد المشرفين.")


            elif "@" in message.text:
                username_match = re.search(r"@(\w+)", message.text)
                if username_match:
                    username = username_match.group(0)
                    try:
                        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
                        if chat_member.status not in ['administrator', 'creator']:
                            chat_info = bot.get_chat(username)

                            if chat_info.type in ['group', 'supergroup', 'channel']:
                                warnings_count[unique_identifier] = warnings_count.get(unique_identifier, 0) + 1

                                warning_message = f"عدد التحذيرات: {warnings_count.get(unique_identifier, 0)}\n"
                                warning_message += f"المعرف: {user_id}\n"
                                warning_message += "إذا تكرر الأمر سيتم حظرك، يمنع إرسال الروابط والمعرفات في المجموعة."
                                warning_reply=bot.reply_to(message, warning_message)

                                bot.delete_message(message.chat.id, message.message_id)
                                threading.Thread(target=delete_warning_message, args=(warning_reply,)).start()

                                if warnings_count.get(unique_identifier, 0) >= 2:

                                    warnings_count[unique_identifier] = 0

                                    bot.kick_chat_member(message.chat.id, user_id)
                                    #warnings_count[unique_identifier] = 0


                                    warning_reply = bot.send_message(message.chat.id, f"تم طرد العضو بسبب تكرار إرسال المعرفات\n"
                                                  f"ID العضو: {user_id}")

                                    threading.Thread(target=delete_warning_message, args=(warning_reply,)).start()

                                    bot_data["warnings_count"] = warnings_count
                                    save_data(bot_data)

                    except telebot.apihelper.ApiTelegramException as e:
                        if "chat not found" in str(e):
                            pass
                        else:
                            raise

            if message.from_user.id not in allowed_admins:
                if "t.me/" in message.text or "https://t.me/" in message.text:
                    # Check if the sender is an administrator
                    chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
                    if chat_member.status not in ['administrator', 'creator']:

                        user_id = message.from_user.id
                        warnings_count[unique_identifier] = warnings_count.get(unique_identifier, 0) + 1

                        warning_message = f"عدد التحذيرات: {warnings_count.get(unique_identifier, 0)}\n"
                        warning_message += f"المعرف: {user_id}\n"
                        warning_message += "إذا تكرر الأمر سيتم حظرك، يمنع إرسال الروابط والمعرفات في المجموعة."
                        warning_reply=bot.reply_to(message, warning_message)

                        bot.delete_message(message.chat.id, message.message_id)
                        threading.Thread(target=delete_warning_message, args=(warning_reply,)).start()




                        if warnings_count.get(unique_identifier, 0) >= 2:


                            bot.kick_chat_member(message.chat.id, user_id)

                            warnings_count[unique_identifier] = 0  #

                            warning_reply = bot.send_message(message.chat.id, f"تم طرد العضو بسبب تكرار إرسال المعرفات\n"
                                                  f"ID العضو: {user_id}")

                            threading.Thread(target=delete_warning_message, args=(warning_reply,)).start()
                        bot_data["warnings_count"] = warnings_count
                        save_data(bot_data)
                        return
                if message.entities:
                    for entity in message.entities:
                        if entity.type == 'text_link' or (entity.type == 'url' and not contains_inline_url(message.text)):
                            bot.delete_message(message.chat.id, message.message_id)
                            break



            if any(word in message.text for word in forbidden_words):
                bot.delete_message(message.chat.id, message.message_id)



        if message.forward_from_chat and not message.forward_from_chat.id in allowed_admins:
            if message.from_user.id not in allowed_admins:
                bot.delete_message(message.chat.id, message.message_id)
        else:
          respond_to_message(message)


    except Exception as e:
        logging.error(f"Error in check_forbidden_words function: {e}")

def delete_warning_message(message):
    time.sleep(60)
    bot.delete_message(message.chat.id, message.message_id)


def respond_to_message(message):
    user_first_name = message.from_user.first_name


    if message.text.lower() in qa_dict:
        response = qa_dict[message.text.lower()]
        bot.reply_to(message, response)
    else:

        pass
server()
while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        logging.error(f"Error in main polling loop: {e}")

        time.sleep(2)
