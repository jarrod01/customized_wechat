from aip import *
import json

baidu_key_file = 'D:\\Users\\ghbxl\\Desktop\\baiduapi.json'
with open(baidu_key_file, encoding='utf-8') as f:
    baidu_api_key = json.load(f)
    APP_ID = baidu_api_key['APP_ID']
    API_KEY = baidu_api_key['API_KEY']
    SECRET_KEY = baidu_api_key['SECRET_KEY']
ocr_client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
sr_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def do_ocr(filePath):
    image = get_file_content(filePath)
    result = ocr_client.basicGeneral(image)
    return result

