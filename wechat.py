from wxpy import *
from datetime import datetime
import os, logging, json

logging.basicConfig(filename='logger.log', level=logging.INFO)

# 创建文件夹
user_path = os.path.expanduser("~")
wxpy_file_path = os.path.join(user_path, 'wxpy_file_2')
if "wxpy_file_2" not in os.listdir(user_path):
    os.mkdir(wxpy_file_path)

# 载入配置
with open(os.path.join(os.path.abspath('.'), "config.json"), encoding='utf-8') as f:
    config = json.load(f)
auto_reply_type = config['auto_reply_type']
auto_save_type = config['auto_save_type']
if auto_save_type:
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_file = open(os.path.join(wxpy_file_path,'messages-'+now+'.txt'), 'w', encoding='utf-8')



# 自动回复判断函数
def reply_or_not(message, reply_config):
    keywords = reply_config.keys()
    for keyword in keywords:
        match_type = reply_config[keyword]["match_type"]
        if match_type:
            if keyword in message:
                return reply_config[keyword]["messages"]
        else:
            if keyword == message:
                return reply_config[keyword]["messages"]
    return []

def auto_reply_messages(msg):
    config_key = 'auto_reply_' + msg.type.lower()
    auto_reply_config = config[config_key]
    if msg.type in ["Recording", "Picture", "Attachment", "Video"]:
        message = ''
    else:
        message = msg.text
    reply_messages = reply_or_not(message, auto_reply_config)
    if reply_messages:
        def try_reply(user, message):
            try:
                if msg.member:
                    msg.reply('@' + msg.member.name + ' ' + message)
                else:
                    user.send(message)
                auto_reply_log(msg, reply_message)
            except ResponseError as e:
                response_error_log(e)
        for reply_message in reply_messages:
            if msg.type == 'Friends':
                try:
                    new_friend = bot.accept_friend(msg.card)
                    try_reply(new_friend,reply_message)
                except ResponseError as e:
                    response_error_log(e)
            elif msg.type == 'Card':
                try:
                    bot.add_friend(msg.card.user_name, verify_content=config['verigy_content'])
                except ResponseError as e:
                    response_error_log(e)
            else:
                try_reply(msg.sender, reply_message)

def auto_save_file(msg):
    message_type = msg.type
    message_id = msg.id
    message_text = msg.text
    message_file_name = msg.file_name
    message_sender = msg.sender
    message_time = msg.receive_time
    message_json = {'message_id': str(message_id), 'message_time':str(message_time),'message_type': str(message_type),
                    "message_sender": str(message_sender), 'message_text': message_text,
                    'message_file_name': str(message_file_name)}
    saved_file.write(json.dumps(message_json))
    if message_type in ["Recording", "Picture", "Attachment", "Video"]:
        msg.get_file(save_path=os.path.join(wxpy_file_path, msg.file_name))

def auto_reply_log(msg, reply_message):
    now = datetime.now().strftime("%Y-%m-%d %X")
    log_message = now + '  ' + str(msg) + '  reply_message:' + reply_message + '\n'
    logging.info(log_message)

def response_error_log(error):
    now = datetime.now().strftime("%Y-%m-%d %X")
    log_message = now + '  error:' + str(error) + '\n'
    logging.error(log_message)

bot = Bot(cache_path=os.path.join(wxpy_file_path, 'wxpy_cache.pkl'),
          qr_path=os.path.join(wxpy_file_path, 'QR_code.png'))
bot.enable_puid(path=os.path.join(wxpy_file_path, 'wxpy_puid.pkl'))
myself = bot.self
@bot.register()
def auto_reply(msg):
    print(msg)
    if msg.type in auto_reply_type:
        auto_reply_messages(msg)
    if msg.type in auto_save_type:
        auto_save_file(msg)
bot.join()