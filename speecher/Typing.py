import tkinter as tk  # 使用Tkinter前需要先导入
import torch


# 第1步，实例化object，建立窗口window
window = tk.Tk()
 
# 第2步，给窗口的可视化起名字
window.title('My Window')
 
# 第3步，设定窗口的大小(长 * 宽)
window.geometry('500x300')  # 这里的乘是小x


L1 =tk.Label(window,text ="输入")
L1.pack()

E1 = tk.Entry(window, bd =5,)
E1.pack()

# inputw = ""


from transformers import pipeline,AutoModelForCausalLM, AutoTokenizer
#使用 transformers 库和一个预训练的模型来生成回应。这里我们使用 chatbot 模型来进行对话：
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# from transformers import AutoTokenizer, AutoModelForMaskedLM
# tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
# model = AutoModelForMaskedLM.from_pretrained("bert-base-chinese")



# 开始对话

# new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

# # 更新聊天历史
# chat_history_ids = new_input_ids if chat_history_ids is None else torch.cat([chat_history_ids, new_input_ids], dim=-1)

# # 生成模型响应
# outputs = model.generate(chat_history_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)


def get_response():
    # 定义聊天上下文
    chat_history_ids = None
    user_input = E1.get()
    print("human",user_input)
    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
    # eos_token = "<EOS>"  # 自定义的结束标记
    # new_input_ids = tokenizer.encode(user_input + eos_token, return_tensors='pt')

# 更新聊天历史
    chat_history_ids = new_input_ids if chat_history_ids is None else torch.cat([chat_history_ids, new_input_ids], dim=-1)

# 生成模型响应
    outputs = model.generate(chat_history_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    # 解码并打印模型响应
    response = tokenizer.decode(outputs[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)
    # print(response)
    return response
 

#将所有部分组合起来，实现一个完整的语音聊天机器人：
def chat():
    # while True:
        # user_input = E1.get()
        # print(user_input)
        # if user_input:
            # print("开始询问"+inputw)
            response = get_response()
            print("机器人: " + response)    
# if __name__ == "__main__":
#     chat()
          
def helloCallBack():
    print("准备对话")
    chat()
    L2 =tk.Label(window,text =get_response())
    L2.pack()
B = tk.Button(window, text ="Typing", command = helloCallBack)
B.pack()

window.mainloop()