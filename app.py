#載入LineBot所需要的套件
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,LineBotApiError
)
from linebot.models import *

import requests, json, time, statistics  # import statistics 函式庫

from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests
app = Flask(__name__)

# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('6sOa+OnuPnspMTtDeTPTNPppPkdBfBN/KAuxkFA6/j9yipl6XFxqyh7ZYANJj/+oRSnkeBV+22N7hebj1hS1k7PZBBPX71dWnglgZTHM4ccW+OPt3YV/aH8rpTEopFBfCWYTJY3bVGbjEhfA74OzCQdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('d63c55b9cfbd93b271d1864de01dd4a3')
access_token = '6sOa+OnuPnspMTtDeTPTNPppPkdBfBN/KAuxkFA6/j9yipl6XFxqyh7ZYANJj/+oRSnkeBV+22N7hebj1hS1k7PZBBPX71dWnglgZTHM4ccW+OPt3YV/aH8rpTEopFBfCWYTJY3bVGbjEhfA74OzCQdB04t89/1O/w1cDnyilFU='
line_bot_api.push_message('Uc9435ce72f8d955afdd36a170269f9ed', TextSendMessage(text='你可以開始了'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except LineBotApiError:
        abort(400)
    return 'OK'
cities = ['基隆市','嘉義市','臺北市','嘉義縣','新北市','臺南市','桃園縣','高雄市','新竹市','屏東縣','新竹縣','臺東縣','苗栗縣','花蓮縣','臺中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']
citiess = ['基隆市','嘉義市','台北市','嘉義縣','新北市','台南市','桃園縣','高雄市','新竹市','屏東縣','新竹縣','台東縣','苗栗縣','花蓮縣','台中市','宜蘭縣','彰化縣','澎湖縣','南投縣','金門縣','雲林縣','連江縣']
def scrape(city):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(
            "https://ifoodie.tw/explore/" + str(city) +
            "/list?sortby=popular&opening=true")
        
        if response.status_code != 200:
            return "無法從 iFoodie 網站擷取資料。"

        soup = BeautifulSoup(response.content, "html.parser")

        # 爬取前十筆餐廳卡片資料
        cards = soup.find_all(
            'div', {'class': 'jsx-1309326380 restaurant-info'}, limit=10)

        content = ""
        for card in cards:
            title = card.find(  # 餐廳名稱
                'a', {"class": "jsx-1309326380 title-text"}).getText()
            stars = card.find(  # 餐廳評價
                'div', {"class": "jsx-2373119553 text"}).getText()
            address = card.find(  # 餐廳地址
                'div', {"class": "jsx-1309326380 address-row"}).getText()

            # 將取得的餐廳名稱、評價及地址連結一起，並且指派給content變數
            content += f"{title} \n{stars}顆星 \n{address} \n\n"

        return content




def get(city):
    token = 'CWA-A6AD0826-313E-41D5-AE53-3742E1898790'
    url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url, verify=False)
    Data = json.loads(Data.text)['records']['location'][0]['weatherElement']
    res = [[] , [] , []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    return res

# Message event
@handler.add(MessageEvent)
def handle_message(event):
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text

    if message.lower().startswith('天氣'):
        city = message[3:]
        city = city.replace('台', '臺')
        if not (city in cities):
            line_bot_api.reply_message(reply_token, TextSendMessage(text="查詢格式為:天氣 縣市"))
        else:
            res = get(city)
            first_data = res[0]  # 只取第一個部分
            line_bot_api.reply_message(reply_token, TemplateSendMessage(
                alt_text=city + '未來 36 小時天氣預測',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/RVKPaGy.jpg',
                            title='{} ~ {}'.format(first_data[0]['startTime'][5:-3], first_data[0]['endTime'][5:-3]),
                            text='天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(
                                first_data[0]['parameter']['parameterName'],
                                first_data[2]['parameter']['parameterName'],
                                first_data[4]['parameter']['parameterName'],
                                first_data[1]['parameter']['parameterName']),
                            actions=[
                                URIAction(
                                    label='詳細內容',
                                    uri='https://www.cwb.gov.tw/V8/C/W/County/index.html'
                                )
                            ]
                        )
                    ]
                )
            )
            )     
        pass
    elif message.lower().startswith('美食'):
        city = message[3:]
        if city in citiess:
            foodie_content = scrape(city)
            
            if foodie_content:
                line_bot_api.reply_message(reply_token, TextSendMessage(text=foodie_content))
            else:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="抱歉，找不到相關的美食資訊。"))
        else:
     
            line_bot_api.reply_message(reply_token, TextSendMessage(text="查詢格式為:美食 縣市"))

    elif event.message.text == "預報":
        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='Menu',
                    text='請選擇地區(更多請手動輸入天氣 縣市)',
                    thumbnail_image_url='https://i.imgur.com/gc8tLcp.jpg',
                    actions=[
                        MessageTemplateAction(
                            label='台北市',
                            text='天氣 台北市'
                        ),
                        MessageTemplateAction(
                            label='台中市',
                            text='天氣 台中市'
                        ),
                        MessageTemplateAction(
                            label='高雄市',
                            text='天氣 高雄市'
                        ),
                        MessageTemplateAction(
                            label='台南市',
                            text='天氣 台南市'
                        )
                    ]
                )
            )
        )
    elif event.message.text == "食物":
        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='Menu',
                    text='請選擇地區(更多請手動輸入美食 縣市)',
                    thumbnail_image_url='https://i.imgur.com/p8cSECp.jpg',
                    actions=[
                        MessageTemplateAction(
                            label='台北市',
                            text='美食 台北市'
                        ),
                        MessageTemplateAction(
                            label='台中市',
                            text='美食 台中市'
                        ),
                        MessageTemplateAction(
                            label='高雄市',
                            text='美食 高雄市'
                        ),
                        MessageTemplateAction(
                            label='台南市',
                            text='美食 台南市'
                        )
                    ]
                )
            )
        )
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=message))
    

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)