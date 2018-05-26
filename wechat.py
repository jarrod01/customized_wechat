from wxpy import *
import os

user_path = os.path.expanduser("~")
wxpy_file_path = os.path.join(user_path, 'wxpy_file')
if wxpy_file_path not in os.listdir(user_path):
    os.mkdir(wxpy_file_path)

bot = Bot(cache_path=os.path.join(wxpy_file_path, 'wxpy_cache.pkl'),
          qr_path=os.path.join(wxpy_file_path, 'QR_code.png'))
bot.enable_puid(path=os.path.join(wxpy_file_path, 'wxpy_puid.pkl'))
myself = bot.self