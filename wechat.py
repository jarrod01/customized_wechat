from wxpy import *
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from random import randint
import os, logging, json, sqlite3, baidu_text_recognize, time

fh = TimedRotatingFileHandler('strategy_log', encoding='utf-8', when='d', interval=1, backupCount=7)
fh2 = TimedRotatingFileHandler('wxpy_log', encoding='utf-8', when='d', interval=1, backupCount=7)
fmt = '%(asctime)s\t%(name)s\t%(levelname)s:\t%(message)s'
# datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt)
fh.setFormatter(formatter)

logging.basicConfig(handlers=[fh2], level=logging.INFO)

logger_name = 'log'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
logger.addHandler(fh)


# 创建文件夹
user_path = os.path.expanduser("~")
abs_path = os.path.abspath('.')
file_save_path = abs_path
dir_name = 'saved_files'
wxpy_file_path = os.path.join(file_save_path,dir_name)
if dir_name not in os.listdir(file_save_path):
    os.mkdir(wxpy_file_path)


config = {}
# 更新配置
def re_load_config(config):
    with open(os.path.join(os.path.abspath('.'), "config.json"), encoding='utf-8') as f:
        new_config = json.load(f)
    for key in new_config:
        config[key] = new_config[key]
    config['load_time'] = datetime.now()
    return config
re_load_config(config)

#
if config['auto_save_type']:
    # now = datetime.now().strftime("%Y%m%d%H%M%S")
    # saved_file = open(os.path.join(wxpy_file_path,'messages-'+now+'.txt'), 'w', encoding='utf-8')
    conn = sqlite3.connect(os.path.join(wxpy_file_path, 'data.db'), check_same_thread=False)
    cursor = conn.cursor()
    # 如果没有表，建立一个
    tables = cursor.execute('select name from sqlite_master where type="table"').fetchall()
    if 'saved_messages' not in str(tables):
        cursor.execute('''CREATE TABLE saved_messages (
                        id INTEGER PRIMARY KEY autoincrement NOT NULL,
                         message_id char(50), 
                         message_time char(50), 
                         message_type char(20), 
                         message_sender char(100), 
                         message_text text, 
                         message_file_name char(100));''')
        conn.commit()




# 自动回复判断函数
def reply_or_not(message, reply_config):
    reply_messages = []
    keywords = reply_config.keys()
    for keyword in keywords:
        match_type = reply_config[keyword]["match_type"]
        if match_type:
            if keyword in message:
                for reply_message in reply_config[keyword]["messages"]:
                    reply_messages.append(reply_message)
        else:
            if keyword == message:
                for reply_message in reply_config[keyword]["messages"]:
                    reply_messages.append(reply_message)
    return reply_messages

def auto_reply_messages(msg):
    config_key = 'auto_reply_' + msg.type.lower()
    auto_reply_config = config[config_key]
    if msg.type == "Recording":
        message = ''
    elif msg.type == "Picture":
        message = ''
        # temp_file_path = os.path.join(os.path.join(wxpy_file_path, 'temp'), msg.file_name)
        ocr_result = baidu_text_recognize.do_ocr(msg.get_file())
        if ocr_result:
            if ocr_result['words_result_num']:
                message = ','.join([word['words'] for word in ocr_result['words_result']])
    elif msg.type == 'Video':
        message = ''
    else:
        message = msg.text
    reply_messages = reply_or_not(message, auto_reply_config)
    if reply_messages:
        def try_reply(user, message):
            delay = randint(2,30)
            time.sleep(delay)
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
    message_id = str(msg.id)
    message_text = str(msg.text)
    message_file_name = str(msg.file_name)
    message_sender = str(msg.sender)
    message_time = str(msg.receive_time)
    # message_json = {'message_id': str(message_id), 'message_time':str(message_time),'message_type': str(message_type),
    #                 "message_sender": str(message_sender), 'message_text': message_text,
    #                 'message_file_name': str(message_file_name)}
    # saved_file.write(json.dumps(message_json, ensure_ascii=False))
    if message_type in ["Recording", "Picture", "Attachment", "Video"]:
        type_save_path = os.path.join(wxpy_file_path, message_type)
        if message_type not in os.listdir(wxpy_file_path):
            os.mkdir(type_save_path)
        msg.get_file(save_path=os.path.join(type_save_path, msg.file_name))
    cursor.execute(
        'insert into saved_messages (message_id, message_time, message_type, message_sender, message_text, message_file_name) values (?,?,?,?,?,?)', (
        message_id, message_time, message_type, message_sender, message_text,
        message_file_name))
    conn.commit()


def auto_reply_log(msg, reply_message):
    log_message = str(msg) + 'reply_message:' + reply_message + '\n'
    print(myself.name + ':' + reply_message)
    logger.info(log_message)

def response_error_log(error):
    log_message = 'error:' + str(error) + '\n'
    print(error)
    logger.error(log_message)

def log_out_response():
    cursor.close()
    conn.close()

def log_in_response():
    print('成功登录了！')

bot = Bot(cache_path=os.path.join(wxpy_file_path, 'wxpy_cache.pkl'),
          qr_path=os.path.join(wxpy_file_path, 'QR_code.png'),
          logout_callback=log_out_response, login_callback=log_in_response)
bot.enable_puid(path=os.path.join(wxpy_file_path, 'wxpy_puid.pkl'))
myself = bot.self
@bot.register()
def auto_reply(msg):
    print(msg)
    # 接受到消息后定时更新配置
    now = datetime.now()
    last_config_load_time = config['load_time']
    if (now-last_config_load_time).seconds>2:
        re_load_config(config)
    if msg.type in config['auto_reply_type']:
        try:
            auto_reply_messages(msg)
        except:
            pass
    if msg.type in config['auto_save_type']:
        auto_save_file(msg)
bot.join()