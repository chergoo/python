import speech_recognition as sr
#pip install speechrecognition transformers torch gtts pydub
#pip install pyAudio
#pip install setuptools
import torch


#使用 speech_recognition 库将语音转换为文本：
def recognize_speech():
    # recognizer = sr.Recognizer()
    # with sr.Microphone() as source:
    #     print("请说话...")
    #     audio = recognizer.listen(source)
    #     try:
    #         text = recognizer.recognize_google(audio, language="zh-CN")
    #         print("你说的是: " + text)
    #         return text
    #     except sr.UnknownValueError:
    #         print("无法识别语音")
    #     except sr.RequestError:
    #         print("无法连接到语音识别服务")
    # return None
    text = "你好"
    return text

# from transformers import pipeline
# #使用 transformers 库和一个预训练的模型来生成回应。这里我们使用 chatbot 模型来进行对话：
# # 加载对话模型
# chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")
# from transformers import AutoModelForCausalLM, AutoTokenizer
# #使用 transformers 库和一个预训练的模型来生成回应。这里我们使用 chatbot 模型来进行对话：
# # model_name = "THUDM/chatglm-6b" #更适合中文对话的模型
# model_name = "google-bert/bert-base-chinese"
# # model_name = "microsoft/DialoGPT-small"    #主y要为英文训练
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)
#CUDA 设备：确保你有一块支持 CUDA 的 GPU，并且 CUDA 驱动和库已正确安装。代码中的 .half().cuda() 将模型加载到 GPU 上，并将其转换为半精度，以节省内存和计算资源。如果你没有 GPU，去掉 .half().cuda() 并使用 .float() 将模型加载到 CPU 上，但这会显著降低性能。
# model = AutoModel.from_pretrained(model_name, trust_remote_code=True).half().cuda()
# model = AutoModel.from_pretrained(model_name, trust_remote_code=True).float()
# model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True).float()

from transformers import AutoTokenizer, AutoModelForMaskedLM
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
model = AutoModelForMaskedLM.from_pretrained("bert-base-chinese")

def get_response(text):
    # print(text)
    # response = chatbot(text)
    # print(response)
    # return response
    # 定义聊天上下文
    chat_history_ids = None
    user_input = text
    eos_token = "<EOS>"  # 自定义的结束标记
    new_input_ids = tokenizer.encode(user_input + eos_token, return_tensors='pt')
    print("human",user_input)
    # new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

# 更新聊天历史
    chat_history_ids = new_input_ids if chat_history_ids is None else torch.cat([chat_history_ids, new_input_ids], dim=-1)

# 生成模型响应
    outputs = model.generate(chat_history_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    # 解码并打印模型响应
    response = tokenizer.decode(outputs[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)
    # print(response)
    return response

#使用 gtts 库将文本转换为语音，并使用 pydub 库播放音频：
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

def speak(response):
    tts = gTTS(text=response, lang='zh')
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
