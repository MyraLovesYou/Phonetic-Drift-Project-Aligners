from langdetect import detect
CH_START = "我在读"
CH_END = "这个词"
EN_START = "I say "
EN_END = " again"

def format_c_phrases(target_words):
    return_string = ""
