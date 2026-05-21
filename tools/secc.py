import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
import json
import os
import binascii

# --- Base62 转换核心逻辑 ---
# Base62 字符集: 0-9, a-z, A-Z
BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = len(BASE62_CHARS)

def bytes_to_base62(byte_data):
    """将字节序列转换为Base62字符串。"""
    if not byte_data:
        return ""
    
    # 将字节序列视为一个大的整数
    num = int.from_bytes(byte_data, 'big')
    
    # 执行基数转换
    encoded = []
    if num == 0:
        return BASE62_CHARS[0]

    while num > 0:
        num, remainder = divmod(num, BASE)
        encoded.append(BASE62_CHARS[remainder])
    
    # Base62 结果需要反转
    return "".join(reversed(encoded))

def base62_to_bytes(base62_str):
    """将Base62字符串转换回字节序列。"""
    if not base62_str:
        return b''
        
    num = 0
    # Base62 解码
    for char in base62_str:
        index = BASE62_CHARS.find(char)
        if index == -1:
            raise ValueError(f"密文包含无效的字符: {char}")
        num = num * BASE + index
        
    # 将整数转回字节序列
    return num.to_bytes((num.bit_length() + 7) // 8, 'big')

# --- 1. 核心加密/解密逻辑 ---

# 密钥文件路径
KEY_FILE = "cipher_key.txt"

def generate_cipher_map():
    """生成随机的Base62字符替换映射表（字典）。"""
    
    standard_chars = list(BASE62_CHARS)
    cipher_chars = standard_chars[:]
    random.shuffle(cipher_chars)
    
    # 生成加密字典 (Base62标准字符 -> 密文随机字符)
    encrypt_map = dict(zip(standard_chars, cipher_chars))
    # 生成解密字典
    decrypt_map = {v: k for k, v in encrypt_map.items()}
    
    return encrypt_map, decrypt_map

def encrypt_process(text, encrypt_map):
    """
    加密流程：GB2312编码 -> Base62转换 -> 随机替换加密。
    """
    # 1. GB2312 编码
    try:
        encoded_bytes = text.encode('gb2312', errors='strict')
    except UnicodeEncodeError as e:
        messagebox.showerror("编码错误", f"文本包含不支持的字符，请移除！错误：{e}")
        return None
        
    # 2. Base62 转换 (得到可读的字母数字字符串)
    base62_text = bytes_to_base62(encoded_bytes)
    
    # 3. 随机替换加密
    encrypted_message = "".join(encrypt_map.get(char, char) for char in base62_text)
    return encrypted_message

def decrypt_process(cipher_text, decrypt_map):
    """
    解密流程：随机替换解密 -> Base62反转 -> GB2312解码。
    """
    # 1. 随机替换解密 (得到 Base62 字符串)
    base62_text = "".join(decrypt_map.get(char, char) for char in cipher_text)
    
    # 2. Base62 反转 (得到字节序列)
    try:
        decrypted_bytes = base62_to_bytes(base62_text)
    except ValueError as e:
        messagebox.showerror("解密错误", f"解码失败，密钥可能错误或密文被破坏！错误：{e}")
        return None
    
    # 3. GB2312 解码
    try:
        original_text = decrypted_bytes.decode('gb2312', errors='strict')
        return original_text
    except UnicodeDecodeError as e:
        messagebox.showerror("解密错误", f"解码失败，密钥可能错误或密文被破坏！错误：{e}")
        return None

# --- 2. GUI 应用逻辑 (基于可选密钥版本) ---

class CipherApp:
    # ... (保持 __init__ 方法中的样式、标题、布局不变) ...
    def __init__(self, master):
        self.master = master
        master.title("密文工具")
        master.geometry("650x550")
        master.configure(bg='#f0f0f0')
        
        self.key_file = KEY_FILE
        self.encrypt_key = None 
        self.decrypt_key = None
        
        # --- 样式定义 ---
        style = ttk.Style()
        style.configure('TLabel', font=('微软雅黑', 11), background='#f0f0f0', foreground='#333333')
        style.configure('TButton', font=('微软雅黑', 10, 'bold'), padding=8)
        style.configure('Green.TButton', background='#4CAF50', foreground='black')
        style.configure('Red.TButton', background='#F44336', foreground='black')
        
        # 1. 标题
        tk.Label(master, text="加密工具", font=('微软雅黑', 16, 'bold'), 
                 bg='#333333', fg='white', pady=10).pack(fill='x')
        
        # 2. 提示信息
        # ttk.Label(master, text="密文将由 0-9, a-z, A-Z 随机替换组成。").pack(pady=5)
        
        # 3. 输入区域
        ttk.Label(master, text="输入区域 (原始文本 / 密文):").pack(pady=(5, 5))
        self.input_text = tk.Text(master, height=6, width=75, bd=1, relief="sunken", 
                                  font=('Consolas', 10), padx=5, pady=5)
        self.input_text.pack(pady=5, padx=20)
        
        # 4. 按钮区域
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="生成密文 (可选使用现有密钥)", command=self.generate_cipher, style='Green.TButton').pack(side=tk.LEFT, padx=20, ipadx=10)
        ttk.Button(button_frame, text="解密密文 (读取密钥)", command=self.decode_cipher, style='Red.TButton').pack(side=tk.LEFT, padx=20, ipadx=10)
        
        # 5. 输出区域
        ttk.Label(master, text="输出区域 (密文 / 解密文本):").pack(pady=(5, 5))
        self.output_text = tk.Text(master, height=6, width=75, bd=1, relief="sunken", 
                                   font=('Consolas', 10), padx=5, pady=5, state=tk.DISABLED)
        self.output_text.pack(pady=5, padx=20)

        # 6. 密钥文件提示
        tk.Label(master, text=f"密钥文件: {self.key_file} ", 
                 font=('Arial', 9), fg="gray", bg='#f0f0f0').pack(pady=5)
        
        
    def _update_output(self, content):
        """更新输出文本框内容."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, content)
        self.output_text.config(state=tk.DISABLED)

    def _read_existing_key(self):
        """尝试从文件读取现有解密字典密钥。"""
        if not os.path.exists(self.key_file):
            return None
        try:
            with open(self.key_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None 
            
    def _create_encrypt_key(self, decrypt_key):
        """根据解密字典生成加密字典（反转键值对）。"""
        return {v: k for k, v in decrypt_key.items()}


    def generate_cipher(self):
        """处理加密，支持选择使用现有密钥或生成新密钥。"""
        original_message = self.input_text.get(1.0, "end-1c").strip()
        
        if not original_message:
            messagebox.showerror("错误", "请输入需要加密的原始信息！")
            return
        
        # 1. 密钥选择逻辑
        decrypt_key_to_use = None
        existing_decrypt_key = self._read_existing_key()
        save_new_key = False

        if existing_decrypt_key is not None:
            result = messagebox.askyesno(
                "密钥选择",
                "检测到现有随机替换密钥文件。\n\n您想使用现有密钥加密吗？\n\n'是'：使用现有密钥，不覆盖文件。\n'否'：生成新密钥并覆盖文件。"
            )
            
            if result:
                decrypt_key_to_use = existing_decrypt_key
            else:
                self.encrypt_key, decrypt_key_to_use = generate_cipher_map()
                save_new_key = True
        else:
            self.encrypt_key, decrypt_key_to_use = generate_cipher_map()
            save_new_key = True

        # 2. 确保获取了加密密钥
        if not save_new_key:
            self.encrypt_key = self._create_encrypt_key(decrypt_key_to_use)
            
        # 3. 执行加密
        encrypted_message = encrypt_process(original_message, self.encrypt_key)
        
        if encrypted_message is None:
            return # 编码失败
        
        # 4. 决定是否保存密钥
        if save_new_key:
            try:
                with open(self.key_file, 'w', encoding='utf-8') as f:
                    # 保存随机替换字典
                    json.dump(decrypt_key_to_use, f, indent=4, ensure_ascii=True) 
                messagebox.showinfo("成功", f"密文已生成，新随机密钥已保存到 {self.key_file}。")
            except Exception as e:
                messagebox.showerror("密钥保存失败", f"无法保存密钥文件：{e}")
                return
        else:
            messagebox.showinfo("成功", f"密文已生成，使用了现有密钥。")
            
        # 5. 更新输出界面
        self._update_output(encrypted_message)

    def decode_cipher(self):
        """处理解密，从文件读取密钥并反向操作。"""
        cipher_text = self.input_text.get(1.0, "end-1c").strip()
        if not cipher_text:
            messagebox.showerror("错误", "请输入密文！")
            return

        # 1. 读取解密密钥
        decrypt_key = self._read_existing_key()
        if decrypt_key is None:
            messagebox.showerror("错误", f"未找到有效的密钥文件：{self.key_file}。\n请先执行'生成密文'操作或检查文件。")
            return
        
        # 2. 执行解密
        decrypted_message = decrypt_process(cipher_text, decrypt_key)
        
        if decrypted_message is None:
            return # 解密失败
        
        # 3. 更新输出界面
        self._update_output(decrypted_message)


# --- 3. 运行主程序 ---

if __name__ == "__main__":
    random.seed() 
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()