# 20240605 Ver 1.2, Make by ue@2fue.com
# GPT-4o 咒語:
# 請幫我用 python 寫一個中文語音轉文字的功能的程式, 並且能夠在打印 log 時加上日期時間, 並且能夠同時透過 Line Notify 同時傳送出去, 最後請幫我把程式加上註解. 謝謝.
# 聽到 Mayday 請幫我另外再打印出來

import speech_recognition as sr
import datetime
import requests
import os
import time

# Line Notify 的 Token (請替換為你的實際 Token)
LINE_NOTIFY_TOKEN = 'LINE_NOTIFY_TOKEN'
AUDIO_FILE = "./audio_record/recorded_audio" #.wav

def send_line_notify(message, file_path=None): #使用 Line Notify 傳送訊息
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }
    payload = {"message": message}
    #files = None
    #if file_path:""
    #    files = {"imageFile": open(file_path, "rb")}
    #    print(file_path);
    #response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=payload, files=files)
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=payload)
    #if files:
    #    files["imageFile"].close()
    return response

def check_emergency_msg(message):
    #定義要檢查的關鍵字
    red_strings = ['mayday', 'emergency', 'sos', '求救', '救命']
    yellow_str = ['help', 'ohca', '歐卡', 'oh卡', '沒有呼吸', '心跳停止']
    # 遍歷關鍵字，檢查字串中是否包含任意關鍵字
    for keyword in red_strings:
        if keyword in message.lower(): # 將字串轉換為小寫，確保檢查時不區分大小寫
            print(f"Red light message detected: {keyword}")
            #break
    for keyword in yellow_str:
        if keyword in message.lower(): # 將字串轉換為小寫，確保檢查時不區分大小寫
            print(f"Yellow light message detected: {keyword}")
            #break

def log_message(message, file_path=None): #打印並記錄帶有日期時間的日誌訊息
    #current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #log = f"[{current_time}-Go] {message}"
    #print(log)
    send_line_notify(message, file_path)
	#check mayday!
    check_emergency_msg(message)

def recognize_speech_from_input(): #(device_index):
    """
    從指定音訊設備捕捉語音並轉換為文字
    """
    r = sr.Recognizer()
    with sr.Microphone() as source: #(device_index=device_index) as source:
        #xxx, log_message("正在從線性輸入孔聆聽...")
        r.adjust_for_ambient_noise(source, duration=1) #噪音控制 (source, duration=1)
        audio = r.listen(source)
    
    #get time stamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存音訊文件
    file_name = f"{AUDIO_FILE}_{timestamp}.wav"
    if len(audio.get_wav_data()) > (800 * 1024):  # 800KB = 700*1024 bytes
        with open(file_name, "wb") as f:
            f.write(audio.get_wav_data())
    
    #xxx, only send img can't audio file?, log_message("Send Audio.", file_name)

    # recognize speech using Google Speech Recognition
    try:
        # 認識語音（這裡預設語言為中文)
        text = r.recognize_google(audio, language="zh-TW")
        message = f"[{timestamp}-Go] {text}"
        print(message)
        log_message(message)
    except sr.RequestError:
        # API 無法使用
        log_message("API 無法使用。")
    except sr.UnknownValueError:
        # 無法辨識語音 #log_message("無法辨識語音。")
        print(f"[{timestamp}]<Local>: 無法辨識語音")
    
    # recognize speech using Google Cloud Speech
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = 'credentials_google_cloud_speech.json' #r"""INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
    try:
        print(f"[{timestamp}]<Local>: Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS))
    except sr.UnknownValueError:
        print(f"[{timestamp}]<Local>: Google Cloud Speech could not understand audio")
    except sr.RequestError as e:
        print(f"[{timestamp}]<Local>: Could not request results from Google Cloud Speech service; {0}".format(e))

def list_audio_devices():
    """
    列出所有音訊輸入設備並返回設備索引
    """
    microphone_list = sr.Microphone.list_microphone_names()
    print("-----------------------")
    for i, microphone_name in enumerate(microphone_list):
        print(f"Device {i}: {microphone_name}")
    print("-----------------------")
    return microphone_list

if __name__ == "__main__":
    devices = list_audio_devices()
    #device_index = int(input("請輸入要使用的音訊設備索引：")) #bypass select only list

    log_message("--- 開始執行中文語音轉文字(Recognize_Google), 版本 1.2 ---")
    while True:
        recognize_speech_from_input() #(device_index)
        # 刪除臨時的音訊文件
        # if os.path.exists(AUDIO_FILE):
        #    os.remove(AUDIO_FILE)
        # 加入一個短暫的延遲，避免無限循環過快
        time.sleep(0.1)
