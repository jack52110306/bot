# -*- coding: utf-8 -*-

#載入LineBot所需要的套件
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('d63c55b9cfbd93b271d1864de01dd4a3')
# 必須放上自己的Channel Secret
handler = WebhookHandler('+oN9bXS7DwKraQgB4wUd2ZTg4dg3kZUyP0nx+dQR31vVV/sikPAWrfDkk4epvjH+RSnkeBV+22N7hebj1hS1k7PZBBPX71dWnglgZTHM4cc+tKVF8EzdmaYm7bkze4aBM6YeOx0n3YZJXCvnsndfswdB04t89/1O/w1cDnyilFU=')

line_bot_api.push_message('U262565b00a73c456ebba11b0bd1e7762', TextSendMessage(text='你可以開始了'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token,message)

#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)