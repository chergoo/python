import speech_recognition as sr
#pip install speechrecognition transformers torch gtts pydub
#pip install pyAudio
#pip install setuptools

#使用 speech_recognition 库将语音转换为文本：
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("请说话...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language="zh-CN")
            print("你说的是: " + text)
            return text
        except sr.UnknownValueError:
            print("无法识别语音")
        except sr.RequestError:
            print("无法连接到语音识别服务")
    return None

from transformers import pipeline
#使用 transformers 库和一个预训练的模型来生成回应。这里我们使用 chatbot 模型来进行对话：
# 加载对话模型
chatbot = pipeline("table-question-answering", model="microsoft/DialoGPT-medium")

def get_response(text):
    response = chatbot(text)
    return response[0]['generated_text']

#使用 gtts 库将文本转换为语音，并使用 pydub 库播放音频：
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

def speak(text):
    tts = gTTS(text=text, lang='zh')
    tts.save("response.mp3")
    audio = AudioSegment.from_mp3("response.mp3")
    play(audio)

#将所有部分组合起来，实现一个完整的语音聊天机器人：
def chat():
    while True:
        user_input = recognize_speech()
        if user_input:
            response = get_response(user_input)
            print("机器人: " + response)
            speak(response)

if __name__ == "__main__":
    chat()
