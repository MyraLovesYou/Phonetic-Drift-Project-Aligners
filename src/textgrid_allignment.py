import wave
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from praatio import textgrid
from praatio.data_classes.interval_tier import Interval


def detect_lang(text):
    """Utility helper: Returns 'zh' if CJK characters are found, else 'en'."""
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return "zh"
    return "en"

def read_transcript(transcript):
    lines = ""
    with open(transcript, "r", encoding="utf-8") as file:
        lines = file.read().splitlines()
    return lines

def align_speech_text(speech_timestamps, transcript_chunks):
    if len(speech_timestamps) != len(transcript_chunks):
        print("Warning possible mismatch between Silero and transcript")
    segments = []
    for i, vad_chunk in enumerate(speech_timestamps):
        start_time = vad_chunk['start']
        end_time = vad_chunk['end']
        text = transcript_chunks[i]
        

        lang = detect_lang(text) 
        
        segments.append((start_time, end_time, text, lang))
    return segments

def create_split_textgrids(base_name, segments, total_duration):
    en_intervals = []
    zh_intervals = []

    for start, end, text, lang in segments:
        # Cap interval boundaries safely within [0, total_duration]
        start_time = max(0.0, start)
        end_time = min(total_duration, end)

        if lang == "en":
            en_intervals.append(Interval(start_time, end_time, text))
        elif lang == "zh":
            zh_intervals.append(Interval(start_time, end_time, text))


    tg_en = textgrid.Textgrid(minTimestamp=0.0, maxTimestamp=total_duration)
    tier_en_1 = textgrid.IntervalTier("English", en_intervals, 0.0, total_duration)
    tier_zh_empty = textgrid.IntervalTier("Mandarin", [], 0.0, total_duration)
    tg_en.addTier(tier_en_1)
    tg_en.addTier(tier_zh_empty)
    tg_en.save(f"data/test/test_P01/corpus_english/{base_name}.TextGrid", includeBlankSpaces=True, format="short_textgrid")


    tg_zh = textgrid.Textgrid(minTimestamp=0.0, maxTimestamp=total_duration)
    tier_en_empty = textgrid.IntervalTier("English", [], 0.0, total_duration)
    tier_zh_2 = textgrid.IntervalTier("Mandarin", zh_intervals, 0.0, total_duration)
    tg_zh.addTier(tier_en_empty)
    tg_zh.addTier(tier_zh_2)
    tg_zh.save(f"data/test/test_P01/corpus_mandarin/{base_name}.TextGrid", includeBlankSpaces=True, format="short_textgrid")

