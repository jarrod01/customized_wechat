"auto_reply_type": 在列表里的消息类型会被自动处理，具体规则见下
"auto_save_type": 在列表里的类型会被自动保存，具体规则见下
"auto_reply_text": 自动回复文字消息，关键词以及回复的内容,key值为关键词(空字符串代表所有的都回复)，match_type:0--完全匹配，1--不完全匹配，包含即可；注意由前到后匹配，匹配到多个会依次回复。，messages为回复的消息列表
"auto_reply_friends": 自动接受好友设置：如果不想自动接受，auto_reply_type去掉就可以；如果全部自动接受，字典key值设置为空字符串就可以；如果非空字符串那么必须申请信息里包含关键词才可以
"auto_reply_picture": 自动回复的关键词以及回复的内容，为空表示是图片就会自动回复，key值如果包含关键词，须进行OCR识别后匹配
"auto_reply_recording": 自动回复的关键词以及回复的内容，为空表示是语音就会自动回复，key值如果包含关键词，须进行语义识别后匹配
"auto_reply_card": 自动添加名片中的人为好友，关键词（key值）为空表示任何人都添加
"auto_reply_attachment": 表示收到文件是否自动回复
"notify_friends": 有问题需要通知的好友