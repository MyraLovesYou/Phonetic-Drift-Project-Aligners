from pathlib import Path
import math
import pandas as pd
import parselmouth
from parselmouth.praat import call
from praatio import textgrid
import unicodedata
import re

DATA_DIR = Path(r"C:\Users\dolph\Downloads\silces\First\P02_firstslices")  # Directory containing .wav and .TextGrid files
OUTPUT_EXCEL = Path(r"C:\Users\dolph\Downloads\silces\First\output.xlsx")

WORD_TIER_NAME = "words"
PHONE_TIER_NAME = "phones"


TARGET_WORDS = {"劈", "peaches", "pitches", "提", "teaches", "tickle", "皮", "peacock", "pickle", "提", "teases", 
                "tissues", "习","seating", "sitting", "爬", "配", "parses", "passes", "罢", "被", "bargain", 
                "baggage", "哈", "黑","harbor", "hacker", "发","非", "father", "faster"}
TARGET_VOWELS = {"i", "ɪ", "a", "ɑ", "e", "æ"}

# Formant analysis parameters
# Rule of thumb: 5500 Hz for adult females/children, 5000 Hz for adult males

MAX_FORMANT_CEILING = 5500.0  
MAX_NUM_FORMANTS = 5.0
TIME_STEP = 0.005  # 5 ms
def get_phone_and_neighbors(tier, target_time):
    entries = tier.entries
    
    for i, (start, end, label) in enumerate(entries):
        if start <= target_time <= end:
            prev_label = entries[i - 1][2].strip() if i > 0 else None
            curr_label = label.strip()
            next_label = entries[i + 1][2].strip() if i + 1 < len(entries) else None
            
            return {
                "prev": prev_label,
                "curr": curr_label,
                "next": next_label,
                "start": start,
                "end": end,
            }
            
    return None
def clean_mandarin_phone(phone_str: str) -> str:
    """
    Strips Chao tone letters (e.g., 'i˧˥' -> 'i'),
    tone digits (e.g., 'i35' or 'i2' -> 'i'),
    and standard tone accents (e.g., 'ǐ' -> 'i').
    """
    # 1. Strip Chao tone letters (Unicode U+02E5 to U+02EB: ˥, ˦, ˧, ˨, ˩)
    cleaned = re.sub(r"[\u02e5-\u02eb]", "", phone_str.strip())

    # 2. Decompose and strip standard diacritics (e.g., combining tone marks)
    decomposed = unicodedata.normalize("NFD", cleaned)
    cleaned = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")

    # 3. Strip any trailing tone numbers (1-5)
    cleaned = re.sub(r"\d+", "", cleaned)

    # 4. Normalize back to standard unicode
    return unicodedata.normalize("NFKC", cleaned).strip()

def extract_formants():
    results = []

    # Find all TextGrids and match with corresponding .wav
    tg_files = list(DATA_DIR.glob("*.TextGrid"))
    if not tg_files:
        print(f"No .TextGrid files found in {DATA_DIR.resolve()}")
        return

    for tg_path in tg_files:
        print(tg_path)
        wav_path = tg_path.with_suffix(".wav")
        if not wav_path.exists():
            print(f"Warning: Missing .wav for {tg_path.name}, skipping.")
            continue
        # Load TextGrid and Praat Sound
        tg = textgrid.openTextgrid(str(tg_path), includeEmptyIntervals=False)
        sound = parselmouth.Sound(str(wav_path))

        # Generate Burg formant object (identical to Praat GUI)
        formant_obj = sound.to_formant_burg(
            time_step=TIME_STEP,
            max_number_of_formants=MAX_NUM_FORMANTS,
            maximum_formant=MAX_FORMANT_CEILING,
            window_length=0.025,
            pre_emphasis_from=50.0,
        )

        word_tier = tg.getTier(WORD_TIER_NAME)
        phone_tier = tg.getTier(PHONE_TIER_NAME)

        for w_start, w_end, word_label in word_tier.entries:
            clean_word = word_label.strip()
            
            # Filter by target words if specified
            if TARGET_WORDS and clean_word.lower() not in {w.lower() for w in TARGET_WORDS}:
                continue

            # Find phone intervals fully or mostly inside the word boundaries
            for p_start, p_end, phone_label in phone_tier.entries:
                raw_phone = phone_label.strip()
                clean_phone = clean_mandarin_phone(raw_phone)
                print(clean_phone)
                # Check if phone falls within the word timeframe
                if p_start >= w_start and p_end <= w_end:
                    print("here1")

                    if clean_phone in TARGET_VOWELS:
                        midpoint = (p_start + p_end) / 2.0

                        # Query Praat Burg object at midpoint
                        f1 = call(formant_obj, "Get value at time", 1, midpoint, "Hertz", "Linear")
                        f2 = call(formant_obj, "Get value at time", 2, midpoint, "Hertz", "Linear")
                        print("here")
                        results.append({
                            "ID": "P02",
                            "word": clean_word,
                            "vowel": clean_phone,
                            "time": "first",
                            "start_time": round(p_start, 4),
                            "end_time": round(p_end, 4),
                            "duration_ms": round((p_end - p_start) * 1000, 2),
                            "midpoint_time": round(midpoint, 4),
                            "f1_hz": round(f1, 2) if not math.isnan(f1) else None,
                            "f2_hz": round(f2, 2) if not math.isnan(f2) else None,
                        })



    # Save to Excel
    df = pd.DataFrame(results)
    df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"Extraction complete! Extracted {len(df)} tokens -> {OUTPUT_EXCEL.resolve()}")


if __name__ == "__main__":
    extract_formants()