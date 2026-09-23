from pathlib import Path
import math
import pandas as pd
import parselmouth
from parselmouth.praat import call
from praatio import textgrid
import unicodedata
import re
import sys
root_path = str(Path(__file__).resolve().parent.parent)

# Add it to sys.path so Python knows where to look for 'src'
if root_path not in sys.path:
    sys.path.append(root_path)
from src.structure_sentence import is_english_word
target_sheet = "Seventh"  # The name of the tab you want to append to
TIME = 7
DATA_DIR = Path(r"C:\Users\dolph\Downloads\Combined\Combined\Seventh_checked")  # Directory containing .wav and .TextGrid files
OUTPUT_EXCEL = Path(r"C:\Users\dolph\Downloads\Combined\Combined\ext_formant_data.xlsx")

WORD_TIER_NAME = "words"
PHONE_TIER_NAME = "phones"


TARGET_WORDS = {"劈", "peaches", "pitches", "提", "teaches", "tickle", "皮", "peacock", "pickle", "提", "teases", 
                "tissue", "习","seating", "sitting", "爬", "配", "parses", "passes", "罢", "被", "bargain", 
                "baggage", "哈", "黑","harbor", "hacker", "发","非", "father", "faster"}
TARGET_VOWELS = {"i", "ɪ", "a", "ɑ", "e", "æ"} #not being used
GENDERS = {"P01": 5000.0,
           "P02": 5500.0,
           "P05": 5000.0,
           "P09": 5500.0,
           "P10": 5500.0,
           "P11": 5500.0,
           "P12": 5000.0,
           "P16": 5500.0,
           "P18": 5500.0,
           "P20": 5000.0,
           "P21": 5500.0,
           "P22": 5500.0,
           "P23": 5500.0,
           "P24": 5000.0,
           "P25": 5500.0}
# Formant analysis parameters
# Rule of thumb: 5500 Hz for adult females/children, 5000 Hz for adult males

MAX_FORMANT_CEILING = 5500.0  
MAX_NUM_FORMANTS = 5.0
TIME_STEP = 0.005  # 5 ms
def get_phone_and_neighbors(tier, target_time):
    entries = tier.entries
    
    for i, (start, end, label) in enumerate(entries):
        if start <= target_time < end:
            prev_label = entries[i - 1][2].strip() if i > 0 else None
            curr_label = label.strip()
            
            # Unpack the next entry if it exists
            if i + 1 < len(entries):
                next_start, next_end, raw_next_label = entries[i + 1]
                next_label = raw_next_label.strip()
            else:
                next_start, next_end, next_label = None, None, None

            if i + 2 < len(entries):
                nextnext_start, nextnext_end, raw_nextnext_label = entries[i + 2]
                nextnext_label = raw_nextnext_label.strip()
            else:
                nextnext_start, nextnext_end, nextnext_label = None, None, None
            
            return {
                "prev": prev_label,
                "curr": curr_label,
                "start": round(start, 4),
                "end": round(end, 4),
                "next": next_label,
                "next_start": round(next_start, 4) if next_start is not None else None,
                "next_end": round(next_end, 4) if next_end is not None else None,
                "nextnext": nextnext_label,
                "nextnext_start": round(nextnext_start, 4) if nextnext_start is not None else None,
                "nextnext_end": round(nextnext_end, 4) if nextnext_end is not None else None,
            }
            
    return None  # No interval matched the timestamp
def clean_mandarin_phone(phone_str: str) -> str:
    """
    Strips Chao tone letters (e.g., 'i˧˥' -> 'i'),
    length marks (e.g., 'iː' -> 'i', 'iˑ' -> 'i'),
    tone digits (e.g., 'i35' or 'i2' -> 'i'),
    and standard tone accents (e.g., 'ǐ' -> 'i').
    """
    # 1. Strip Chao tone letters (\u02e5-\u02eb) and IPA length marks (ː \u02d0, ˑ \u02d1, :)
    cleaned = re.sub(r"[\u02e5-\u02eb\u02d0\u02d1:]", "", phone_str.strip())

    # 2. Decompose and strip standard diacritics (combining tone marks/accents)
    decomposed = unicodedata.normalize("NFD", cleaned)
    cleaned = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")

    # 3. Strip any trailing tone numbers (1-5)
    cleaned = re.sub(r"\d+", "", cleaned)

    # 4. Normalize back to standard unicode
    return unicodedata.normalize("NFKC", cleaned).strip()

def extract_formants(folder, id, max_formant):
    results = []

    # Find all TextGrids and match with corresponding .wav
    tg_files = list(folder.glob("*.TextGrid"))
    if not tg_files:
        print(f"No .TextGrid files found in {folder.resolve()}")
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
            maximum_formant=max_formant,
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

            left_phones = get_phone_and_neighbors(phone_tier, w_start)
           
            if left_phones == None:
                print(f"issue with target vowel on file {tg_path.stem}")
                continue
            target = left_phones.get("next")
           
            if target == None:
                print(f"issue with target vowel on file {tg_path.stem}")
                continue
            raw_phone = target.strip()
            clean_phone = clean_mandarin_phone(raw_phone)
            p_start = left_phones.get("next_start")
            p_end = left_phones.get("next_end")
            fraction = 0.50
            if clean_phone == "ej":
                fraction = 0.20
            elif clean_phone == "ɑ" and left_phones.get("nextnext") == "ɹ" and (p_end - p_start) > (left_phones.get("nextnext_end") - left_phones.get("nextnext_start")):
                # this long if is just looking for ar and comparing their lengths
                fraction = 0.60
            elif clean_phone == "ɑ" and left_phones.get("nextnext") == "ɹ":
                p_end = left_phones.get("nextnext_end")
            target_time = p_start + fraction * (p_end - p_start)
            # midpoint = (p_start + p_end) / 2.0
            # Query Praat Burg object at midpoint
            f1 = call(formant_obj, "Get value at time", 1, target_time, "Hertz", "Linear")
            f2 = call(formant_obj, "Get value at time", 2, target_time, "Hertz", "Linear")
            language = "CN"
            if is_english_word(word_label):
                language = "EN"
            results.append({
                "ID": id,
                "language": language,
                "word": re.sub(r'\d+', '', tg_path.stem),
                "vowel": clean_phone,
                "time": TIME,
                "start_time": round(p_start, 4),
                "end_time": round(p_end, 4),
                "duration_ms": round((p_end - p_start) * 1000, 2),
                "target_time": round(target_time, 4),
                "f1_hz": round(f1, 2) if not math.isnan(f1) else None,
                "f2_hz": round(f2, 2) if not math.isnan(f2) else None,
            })




    new_df = pd.DataFrame(results)


    if OUTPUT_EXCEL.exists():
        excel_file = pd.ExcelFile(OUTPUT_EXCEL)
        
        # Check if this specific sheet already exists in the workbook
        if target_sheet in excel_file.sheet_names:
            existing_df = pd.read_excel(OUTPUT_EXCEL, sheet_name=target_sheet)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            # Sheet doesn't exist yet in the file
            combined_df = new_df

        # Write back into the specific sheet without touching other sheets
        with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            combined_df.to_excel(writer, sheet_name=target_sheet, index=False)
            
        print(f"Appended {len(new_df)} rows to sheet '{target_sheet}'. Total in sheet: {len(combined_df)}")

    else:
        # If the Excel file doesn't exist at all, create it fresh
        with pd.ExcelWriter(OUTPUT_EXCEL, engine="openpyxl") as writer:
            new_df.to_excel(writer, sheet_name=target_sheet, index=False)
        print(f"Created new file and sheet '{target_sheet}' with {len(new_df)} rows.")


if __name__ == "__main__":
    for subfolder in DATA_DIR.rglob('*'):
        if subfolder.is_dir():
            
            extract_formants(subfolder, subfolder.name[:3], GENDERS.get(subfolder.name[:3], 5500.0))