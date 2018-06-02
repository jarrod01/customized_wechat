# 自动保存消息

> auto_save_type：在列表里的类型会被自动保存，数据存储在saved_files/data.db，对应的附件保存在相应文件夹里

# 自动回复消息

* auto_reply_type 在列表里的消息类型会被自动处理
## 关键词策略：
每种类型的key值代表要识别的关键词，如auto_reply_text字典的key值代表收到文本消息后检测的自动回复的关键词

所有的关键词都会进行匹配，如果匹配到多个关键词，则会自动回复这些关键词对应的所有消息

如果相对某种类型做通用回复，把key配置为空字符串即可

每个关键词对应的字典含义：
* match_type: 1表示包含关键词即可（如果关键词为空字符串，则会所有的消息都自动回复），0表示消息必须完全匹配关键词
* messages： 表示要回复的消息列表（如果匹配到多个关键词，这些关键词对应的列表会叠加）
* remark_name：自动添加好友时的备注名称

## 不同类型的消息匹配策略

* 其中text、attachment、sharing、map、note、system类型根据msg.text（即包含的文本）自动回复对应的文本消息
* 其中图片类消息会先调用[百度OCR识别](https://cloud.baidu.com/doc/OCR/OCR-Python-SDK.html)文字，然后匹配关键词，关键词回复逻辑同上，百度api的配置文件放在主用户目录里的api_key.json文件里
* 其中语音类消息会先调用[百度SR识别](https://cloud.baidu.com/doc/SPEECH/ASR-Online-Python-SDK.html)文字，然后匹配关键词，关键词回复逻辑同上（还没实现）
* 其中视频类目前只能做通用回复（key值配置为空字符串）
* 加好友消息匹配好友的验证信息，如果匹配上关键词策略则自动接受好友申请，同时支持将备注名设置为对应的remark_name，关键词配置为空字符串则表示所有好友消息均自动回复
* 好友推荐消息根据好友名称判断是否自动发送好友请求（貌似没啥用），关键词配置为空字符串则表示所有好友卡片均自动发送好友申请，申请时的验证信息配置在"verify_content"
* notify_friends: 有问题需要通知的好友，貌似只支持备注名搜索，不支持微信id搜索（暂时未开发）
* tuling_bot： 表示是否启用[图灵机器人](http://www.tuling123.com/)进行自动回复

# 其他

strategy_auto_update_time：策略自动更新时间(s)