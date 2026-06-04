import re
import unicodedata


PUNCT_PATTERN = r"[\,\.\!\?\:\;\(\)\[\]\{\}\"“”‘’…]"


VI_NUMBER_NORMALIZATION = {
    "một": "1",
    "hai": "2",
    "ba": "3",
    "bốn": "4",
    "năm": "5",
    "sáu": "6",
    "bảy": "7",
    "tám": "8",
    "chín": "9",
    "mười": "10",
}


UNIT_NORMALIZATION = {
    "miligam": "mg",
    "mi li gam": "mg",
    "milligram": "mg",
    "độ c": "độ",
}


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def normalize_basic(text: str) -> str:
    text = normalize_unicode(text)
    text = text.lower().strip()
    text = re.sub(PUNCT_PATTERN, " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_medical_units(text: str) -> str:
    text = text.replace("500mg", "500 mg")
    text = text.replace("500 mg", "500 mg")
    text = text.replace("năm trăm miligam", "500 mg")
    text = text.replace("năm trăm mi li gam", "500 mg")
    text = text.replace("ba mươi bảy độ tám", "37.8 độ")
    text = text.replace("ba mươi bảy phẩy tám", "37.8")
    return text


def normalize_for_wer(text: str) -> str:
    text = normalize_basic(text)
    text = normalize_medical_units(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_for_medical_term_check(text: str) -> str:
    return normalize_for_wer(text)