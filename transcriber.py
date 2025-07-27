# transcriber.py
import os
import wave
import json
import re
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

# 设置 Vosk 模型路径（使用绝对路径）
model_path = r"G:\PycharmData\ChineseLanguageTool\vosk-model-cn-0.22\vosk-model-cn-0.22"
model = Model(model_path)

# 设置 ffmpeg 路径，确保 pydub 可以调用
AudioSegment.converter = r"G:\PycharmData\ChineseLanguageTool\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"


def convert_audio(input_path, output_path):
    """音频格式转换函数"""
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(output_path, format="wav")
        return True
    except Exception as e:
        print(f"音频转换失败: {e}")
        return False


def format_chinese_text(raw_text):
    """
    优化中文文本格式：
    1. 去除所有多余空格
    2. 智能添加标点符号
    3. 符合中文书面表达习惯
    """
    if not raw_text:
        return ""

    # 第一步：基础清理
    text = raw_text.replace(" ", "").replace("。。", "。").replace("，，", "，")

    # 第二步：智能断句（基于语义和语气词）
    sentence_rules = [
        (r"(虽然|尽管|即使)", "，\\1"),  # 在转折词前加逗号
        (r"(但是|然而|不过|所以|因此)", "。\\1"),  # 在强烈转折词前加句号
        (r"([^。！？])([我们|你们|他们|它们|她们|大家])", "\\1。\\2"),  # 人称代词前断句
        (r"([呢吗吧啊呀嘛哟了])([^。！？’”])", "\\1。\\2"),  # 语气词后断句
    ]

    for pattern, replacement in sentence_rules:
        text = re.sub(pattern, replacement, text)

    # 第三步：处理特殊情况
    text = re.sub(r"([。！？，、；])+", r"\1", text)  # 去除重复标点
    text = re.sub(r"([^。！？])([一二三四五六七八九十]+、)", r"\1。\2", text)  # 列表项前断句

    # 第四步：规范化标点
    text = text.replace(",", "，").replace(":", "：").replace(";", "；")
    text = re.sub(r'"([^"]+)"', r"「\1」", text)  # 中文引号

    # 第五步：确保以句号结尾
    if text and text[-1] not in "。！？":
        text += "。"

    return text.strip()


def transcribe_audio(audio_path):
    """转录主函数"""
    temp_path = os.path.splitext(audio_path)[0] + "_converted.wav"
    if not convert_audio(audio_path, temp_path):
        raise Exception("音频格式转换失败")

    try:
        results = []

        with wave.open(temp_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    part_result = json.loads(rec.Result())
                    results.append(part_result.get("text", ""))

            final_result = json.loads(rec.FinalResult())
            results.append(final_result.get("text", ""))

        raw_text = ''.join(results)
        return format_chinese_text(raw_text)

    except Exception as e:
        raise Exception(f"转录过程中出错: {e}")
    finally:
        # 在关闭文件之后再尝试删除临时文件
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                print(f"临时文件无法删除：{temp_path}")
