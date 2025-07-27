# ui.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from transcriber import transcribe_audio

# === UI 回调函数 ===
def process_audio():
    audio_path = filedialog.askopenfilename(filetypes=[("音频文件", "*.wav *.mp3 *.m4a *.flac")])
    if not audio_path:
        return
    try:
        result = transcribe_audio(audio_path)
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, result)
    except Exception as e:
        messagebox.showerror("错误", f"处理音频时出错：\n{e}")

def export_text_to_file():
    text = output_textbox.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("提示", "无文本可导出")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("成功", f"文本已导出至：\n{file_path}")

# === 界面构建 ===
root = tk.Tk()
root.title("语音转文字工具 V1.0")
root.geometry("800x600")

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

upload_btn = tk.Button(btn_frame, text="选择音频并转写", command=process_audio, height=2, width=25)
upload_btn.pack(side=tk.LEFT, padx=10)

export_btn = tk.Button(btn_frame, text="导出文本", command=export_text_to_file, height=2, width=20)
export_btn.pack(side=tk.LEFT, padx=10)

output_textbox = scrolledtext.ScrolledText(root, font=("微软雅黑", 12), wrap=tk.WORD)
output_textbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

root.mainloop()