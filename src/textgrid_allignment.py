from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from praatio import textgrid
from praatio.data_classes.interval_tier import Interval
from pathlib import Path
from collections import defaultdict

def detect_lang(text):
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

def create_split_textgrids(output_dir, base_name, segments, total_duration):
    en_intervals = []
    zh_intervals = []
    en_dir = output_dir + "/corpus_en/" + base_name
    zh_dir = output_dir + "/corpus_zh/" + base_name
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
    tg_en.save(en_dir, includeBlankSpaces=True, format="short_textgrid")


    tg_zh = textgrid.Textgrid(minTimestamp=0.0, maxTimestamp=total_duration)
    tier_en_empty = textgrid.IntervalTier("English", [], 0.0, total_duration)
    tier_zh_2 = textgrid.IntervalTier("Mandarin", zh_intervals, 0.0, total_duration)
    tg_zh.addTier(tier_en_empty)
    tg_zh.addTier(tier_zh_2)
    tg_zh.save(zh_dir, includeBlankSpaces=True, format="short_textgrid")

def merge_all_tiers(english_tg_path, mandarin_tg_path, output_tg_path):
    tg_en = textgrid.openTextgrid(english_tg_path, includeEmptyIntervals=False)
    tg_zh = textgrid.openTextgrid(mandarin_tg_path, includeEmptyIntervals=False)

    min_time = min(tg_en.minTimestamp, tg_zh.minTimestamp)
    max_time = max(tg_en.maxTimestamp, tg_zh.maxTimestamp)
    merged_tg = textgrid.Textgrid(
        minTimestamp=min_time, 
        maxTimestamp=max_time
    )
    
    zh_words = tg_zh._tierDict["words"]
    zh_phones = tg_zh._tierDict["phones"]
    en_words = tg_en._tierDict["words"]
    en_phones = tg_en._tierDict["phones"]
    zh_words.name = "mandarin words"
    zh_phones.name = "mandarin phones"
    en_words.name = "english words"
    en_phones.name = "english phones"

    merged_tg.addTier(zh_words)
    merged_tg.addTier(zh_phones)
    merged_tg.addTier(en_words)
    merged_tg.addTier(en_phones)

        
    merged_tg.save(output_tg_path, includeBlankSpaces=True, format="short_textgrid")

def match_files(fp_wav, fp_txt):
    directories = [
        Path(fp_wav),
        Path(fp_txt),
    ]

    grouped_files = defaultdict(list)

    for dir_path in directories:
        for file_path in dir_path.glob('*'):
            if file_path.is_file():
                # Get the first 3 letters of the filename
                file_id = file_path.name[:3]
                grouped_files[file_id].append(file_path)

    matched_groups = {
        file_id: files
        for file_id, files in grouped_files.items()
        if len(set(f.parent for f in files)) > 1  # Must appear in >1 distinct directory
    }

    for file_id, files in matched_groups.items():
        print(f"\nID Match: [{file_id}]")
        for file_path in files:
            print(f"  - {file_path}")
    return matched_groups

