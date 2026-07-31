import unicodedata
CH_START = "我在读"
CH_END = "这个词"
EN_START = "I say "
EN_END = " again"

def is_english_word(word: str) -> bool:
    return word.isalpha() and word.isascii()

def format_c_phrases(target_words):
    return_list = []
    words = target_words.split("|")
    for word in words:
        if is_english_word(word):
            return_list.append(EN_START + word + EN_END + " ")
        else:
            sentence = CH_START + word + CH_END
            sentence = " ".join(sentence)
            return_list.append(sentence)
    return return_list
