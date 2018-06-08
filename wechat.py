from wxpy import *
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from random import randint
from threading import Timer
import os, logging, json, sqlite3, baidu_text_recognize, time

fh = TimedRotatingFileHandler('strategy_log', encoding='utf-8', when='d', interval=1, backupCount=7)
fmt = '%(asctime)s\t%(name)s\t%(levelname)s:\t%(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt)
fh.setFormatter(formatter)
logger_name = 'log'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
logger.addHandler(fh)

fh2 = TimedRotatingFileHandler('wxpy_log', encoding='utf-8', when='d', interval=1, backupCount=7)
logging.basicConfig(handlers=[fh2], level=logging.INFO)




# 创建文件夹
user_path = os.path.expanduser("~")
abs_path = os.path.abspath('.')
file_save_path = abs_path
dir_name = 'saved_files'
wxpy_file_path = os.path.join(file_save_path,dir_name)
if dir_name not in os.listdir(file_save_path):
    os.mkdir(wxpy_file_path)


# 通过config的logged_out控制登出后不再自动更新配置，latest_response_time控制最新连接时间，配合自动给文件助手发送消息防止掉线
config = {'logged_out':False, 'latest_response_time': datetime.now()}
# 更新配置
def load_config():
    with open(os.path.join(os.path.abspath('.'), "config.json"), encoding='utf-8') as f:
        new_config = json.load(f)
    for key in new_config:
        config[key] = new_config[key]
    config['load_time'] = datetime.now()
    # if not config['logged_out']:
    #     t = Timer(config["strategy_auto_update_time"], load_config)
    #     t.start()
    #     print('配置已更新')
    #     logging.info('配置已更新')
    return config
load_config()


# 初始化需要保存的文件的数据库链接
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

def auto_reply_log(msg, reply_message):
    log_message = str(msg) + 'reply_message:' + reply_message + '\n'
    print(myself.name + ':' + reply_message)
    logger.info(log_message)

def response_error_log(error):
    log_message = 'error:' + str(error) + '\n'
    print(error)
    logger.error(log_message)

# 自动回复判断函数
def reply_strategy(message, reply_config):
    reply_messages = []
    matched_keywords = []
    keywords = reply_config.keys()
    for keyword in keywords:
        match_type = reply_config[keyword]["match_type"]
        if match_type:
            if keyword in message:
                print("keyword" + keyword)
                matched_keywords.append(keyword)
                for reply_message in reply_config[keyword]["messages"]:
                    reply_messages.append(reply_message)
                print(reply_messages)
        else:
            if keyword == message:
                matched_keywords.append(keyword)
                for reply_message in reply_config[keyword]["messages"]:
                    reply_messages.append(reply_message)
    return {'reply_messages': reply_messages, 'matched_keywords': matched_keywords}

def do_ocr(msg):
    if baidu_text_recognize.api_key:
        ocr_result = baidu_text_recognize.do_ocr(msg.get_file())
        if ocr_result:
            if ocr_result['words_result_num']:
                message = ','.join([word['words'] for word in ocr_result['words_result']])
                return message
    return ""

def auto_reply_messages(msg):
    config_key = 'auto_reply_' + msg.type.lower()
    auto_reply_config = config[config_key]
    if msg.type == "Recording":
        message = ''
    elif msg.type == "Picture":
        message = do_ocr(msg)
    elif msg.type == 'Video':
        message = ''
    else:
        message = msg.text
    strategy_result = reply_strategy(message, auto_reply_config)
    reply_messages = strategy_result['reply_messages']
    print("124strategy_result\n" + strategy_result)
    if reply_messages:
        config['latest_response_time'] = datetime.now()
        # 回复消息函数
        def try_reply(user, message):
            # delay = randint(2,10)
            # time.sleep(delay)
            try:
                if msg.member:
                    msg.reply('@' + msg.member.name + ' ' + message)
                else:
                    user.send(message)
                auto_reply_log(msg, reply_message)
            except ResponseError as e:
                response_error_log(e)
        print(msg)
        for reply_message in reply_messages:
            if msg.type == 'Friends':
                try:
                    new_friend = bot.accept_friend(msg.card)
                    auto_reply_log(msg, '自动接受了好友申请')
                    if strategy_result['matched_keywords']:
                        matched_keyword = strategy_result['matched_keywords'][0]
                        try:
                            remark_name = config['auto_reply_friends'][matched_keyword]['remark_name']
                            remark_name_friends = bot.search(remark_name)
                            if remark_name_friends:
                                new_remark_name = remark_name + len(remark_name_friends)
                            else:
                                new_remark_name = remark_name
                            new_friend.set_remark_name(new_remark_name)
                            auto_reply_log(msg, '设置备注名为：'+remark_name)
                        except KeyError:
                            pass
                    try_reply(new_friend,reply_message)
                except ResponseError as e:
                    response_error_log(e)
            elif msg.type == 'Card':
                try:
                    bot.add_friend(msg.card.user_name, verify_content=config['verigy_content'])
                except ResponseError as e:
                    response_error_log(e)
            elif msg.type == 'Note':
                print(strategy_result)
                if strategy_result['matched_keywords']:
                    matched_keyword = strategy_result['matched_keywords'][0]
                    print("matched_keyword\n" + matched_keyword)
                    try:
                        remark_name = config['auto_reply_friends'][matched_keyword]['remark_name']
                        remark_name_friends = bot.search(remark_name)
                        if remark_name_friends:
                            new_remark_name = remark_name + len(remark_name_friends)
                        else:
                            new_remark_name = remark_name
                        print('remark_name: ' + new_remark_name)
                        msg.sender.set_remark_name(new_remark_name)
                        print('设置备注名成功')
                        auto_reply_log(msg, '设置备注名为：' + remark_name)
                    except KeyError:
                        print('备注名设置有问题')
                    except ResponseError:
                        print('自动设置备注失败')

                    try_reply(msg.sender, reply_message)
            else:
                try_reply(msg.sender, reply_message)
    elif config['tuling_bot']:
        if baidu_text_recognize.api_key:
            config['latest_response_time'] = datetime.now()
            delay = randint(2, 10)
            time.sleep(delay)
            try:
                tuling_api_key = baidu_text_recognize.api_key['TULING_API_KEY']
                tuling = Tuling(api_key=tuling_api_key)
                print(myself.name + '： ' + tuling.do_reply(msg))
            except:
                pass

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

# 自动加群，还没写完，经常加群失败，尤其是40人以上的群，还未找到原因
def auto_add_group(msg):
    auto_reply_config = config["auto_add_group"]
    if msg.type == 'Picture':
        message = do_ocr(msg)
    else:
        message = msg.text
    strategy_result = reply_strategy(message, auto_reply_config)
    group_name = strategy_result['reply_messages'][0]
    group_search_result = bot.groups().search(group_name)


def send_to_file_helper_repeatedly():
    now = datetime.now()
    if (now-config['latest_response_time']).seconds>=1800:
        bot.file_helper.send("I'm still here, haha!")
        config['latest_response_time'] = now
    # 顺便更新一下配置文件
    load_config()
    t = Timer(1800, send_to_file_helper_repeatedly)
    t.start()

def log_out_response():
    cursor.close()
    conn.close()
    config['logged_out'] = True

def log_in_response():
    print('成功登录了！')

bot = Bot(cache_path=os.path.join(wxpy_file_path, 'wxpy_cache.pkl'),
          qr_path=os.path.join(wxpy_file_path, 'QR_code.png'),
          logout_callback=log_out_response, login_callback=log_in_response)
bot.enable_puid(path=os.path.join(wxpy_file_path, 'wxpy_puid.pkl'))
myself = bot.self
send_to_file_helper_repeatedly()
@bot.register()
def auto_reply(msg):
    print(msg)
    # 接受到消息后定时更新配置
    # now = datetime.now()
    # if (now - config['load_time']).seconds > config["strategy_auto_update_time"]:
    #     load_config()
    if msg.type in config['auto_reply_type']:
        auto_reply_messages(msg)
    if msg.type in config['auto_save_type']:
        auto_save_file(msg)
    # if config["auto_add_group"] and msg.type == 'Picture':
    #    auto_add_group(msg)

bot.join()