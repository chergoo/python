import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
# 加载模型和分词器
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# from transformers import AutoTokenizer, AutoModelForMaskedLM,AutoModelForCausalLM
# tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
# model = AutoModelForCausalLM.from_pretrained("bert-base-chinese",is_decoder=True)
#File "D:\python\Lib\site-packages\transformers\models\bert\modeling_bert.py", line 220, in forward
#     embeddings += position_embeddings
# RuntimeError: output with shape [1, 1, 768] doesn't match the broadcast shape [1, 0, 768]

# 定义聊天上下文
chat_history_ids = None

# 开始对话
user_input = "hello,world"
print(user_input)
new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
# eos_token = "<EOS>"  # 自定义的结束标记
# new_input_ids = tokenizer.encode(user_input + eos_token, return_tensors='pt')

# 更新聊天历史
chat_history_ids = new_input_ids if chat_history_ids is None else torch.cat([chat_history_ids, new_input_ids], dim=-1)

# 生成模型响应
outputs = model.generate(chat_history_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

# 解码并打印模型响应
response = tokenizer.decode(outputs[:, chat_history_ids.shape[-1]:][0], skip_special_tokens=True)
print("DialoGPT: ", response)
