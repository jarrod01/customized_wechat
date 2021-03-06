from aip import *
import json, os, subprocess

user_path = os.path.expanduser("~")
api_key_file = os.path.join(user_path, 'api_key.json')
try:
    with open(api_key_file, encoding='utf-8') as f:
        api_key = json.load(f)
        APP_ID = api_key['BAIDU_APP_ID']
        API_KEY = api_key['BAIDU_API_KEY']
        SECRET_KEY = api_key['BAIDU_SECRET_KEY']
        ocr_client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        sr_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
except FileNotFoundError:
    print('api_key_file not found!')
    api_key = {}

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def do_ocr_file(filePath):
    image = get_file_content(filePath)
    result = ocr_client.basicGeneral(image)
    return result

def do_ocr(pic_data):
    result = ocr_client.basicGeneral(pic_data)
    return result


ffmpeg_path = 'D:\\jarrod\\Desktop\\小工具\\ffmpeg\\bin\\ffmpeg'
def mp3topcm(mp3_path, pcm_path):
    path, name = os.path.split(mp3_path)
    if name.split('.')[-1] != 'mp3':
        print('not a mp3 file')
        return 0
    if pcm_path is None or pcm_path.split('.')[-1] != 'pcm':
        mp3_path = os.path.join(path, name.split('.')[0] + 'pcm')
    error = subprocess.call([ffmpeg_path, '-i', mp3_path, pcm_path])
    print(error)
    if error:
        return 0
    print('success')
    return pcm_path

def do_sr(file_path):
    audio = get_file_content(file_path)
    result = sr_client.asr(audio, 'pcm', 16000, {'dev_id':1536})
    return result

if __name__ == '__main__':
    # result = do_ocr_file('D:\jarrod\Desktop\下载.jpg')
    result = do_sr('D:\\jarrod\\Desktop\\bai.wav')
    print(result)