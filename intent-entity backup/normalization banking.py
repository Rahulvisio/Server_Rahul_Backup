import spacy
from spacy.language import Language
import regex as re  
import string


def handle_possessive_names(text):
    text = text.replace("'s", "")
    return text

def smart_comma(text: str) -> str:
    # Rule 1: remove commas between digits (e.g. "1, 2, 3" -> "123")
    text = re.sub(r"(?<=\d)\s*,\s*(?=\d)", "", text)
    
    # Rule 2: replace other commas with space
    text = re.sub(r"\s*,\s*", " ", text)
    
    return text.strip()


import re

def currency_to_decimal(text):
    if not re.search(r'\bpaise\b|\bp\.\b', text, re.IGNORECASE):
        return text  

    currency_pattern = re.compile(
        r'(?:(rs\.?|rupees?)\s*)?(\d+)\s*(rs\.?|rupees?)?\s*(?:and|,)?\s*(\d{1,2})\s*(?:paise?|p\.?)',
        re.IGNORECASE
    )

    def repl(match):
        currency_prefix1, rupees, currency_prefix2, paise = match.groups()

        
        if not (currency_prefix1 or currency_prefix2):
            return match.group(0)  

        rupees = int(rupees)
        decimal_value = f"{rupees}.{int(paise):02}"
        
        return f"{decimal_value} rupees"

    return currency_pattern.sub(repl, text)



def replace_word_hyphens_with_space(text):
    return re.sub(r'(?<=\w)[-–—](?=\w)', ' ', text)

def normalize_payment_methods(text):
    mappings = {
        r'\b(?:i am pso|i am psp|i am pierced|impf|imtf|impl|imts|immediate payment service|imps|inps)\b': 'imps',
        r'\b(?:any ft|mesd|nesd|mefd|eft|national electronic fund transfer|any fd|national electronic funds transfer|nefd|nest|nft|n\.e\.f\.t)\b': 'neft',
        r'\b(?:rtjs|real time gross settlement|real time cross settlement|rtts)\b': 'rtgs',
        r'\b(?:payment address|vpa|virtual payment address)\b': 'upi id',
        r'\b(?:pese|paisa)\b': 'paise',
        r'\b(?:upi|u\.p\.i|upie|uti|ubi|upa|upr)\b': 'upi',
        r'\b(?:bhim|beam|bean|bheem)\b': 'bheem'
    }
    for pattern, replacement in mappings.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def normalize_scales(text):
    text = re.sub(r'\blakhs\b', 'lakh', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhundreds\b', 'hundred', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthousands\b', 'thousand', text, flags=re.IGNORECASE)
    text = re.sub(r'\bdatapack\b', 'data pack', text, flags=re.IGNORECASE)
    return text

def fix_mobile_number(text):
    pattern = re.compile(r'\b\d[\d\s]*\d\b')
    currency_match = re.search(r'\b(rs|rupees|paise)\b', text, re.IGNORECASE)
    right_has_digits = False
    if currency_match:
        after_currency = text[currency_match.end():]
        if re.search(r'\d', after_currency):
            right_has_digits = True

    def repl(match):
        number = match.group(0)
        compact = re.sub(r'\s+', '', number)
        if compact.isdigit() and len(compact) == 10:
            return compact
        if currency_match and match.end() <= currency_match.start():
            if right_has_digits:
                return compact  
            else:
                parts = number.split()
                if len(parts) > 1:
                    return "".join(parts[:-1]) + " " + parts[-1]
                return number

        if currency_match and match.start() >= currency_match.end():
            return compact

        return compact

    return pattern.sub(repl, text)

def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        scale_mapping = {
            "hundred":   100,
            "thousand":  1000,
            "lakh":      100000,
            "million":   1000000,
            "billion":   1000000000,
            "trillion":  1000000000000
        }
        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for word, scale in scale_mapping.items():
            numwords[word] = (scale, 0)

    tokens = textnum.replace('-', ' ').split()
    current = result = 0
    curstring = ""
    onnumber = False
    last_was_decimal = False  # Track if the last number was a decimal

    for i, word in enumerate(tokens):
        # Preserve currency words
        if word.lower() in ["rs", "rupees", "rupee", "paise"]:
            if onnumber:
                curstring += str(result + current) + " "
                result = current = 0
                onnumber = False
            curstring += word + " "
            continue

        # If the token is a decimal number
        if re.match(r"^\d+\.\d+$", word):  
            if onnumber:
                curstring += str(result + current) + " "
                result = current = 0
                onnumber = False
            curstring += word + " "
            last_was_decimal = True
            continue

        # If the token is a normal integer number
        if word.isdigit():
            if len(word) >= 9:  # likely phone/ID, keep as is
                if onnumber:
                    curstring += str(result + current) + " "
                    result = current = 0
                    onnumber = False
                curstring += word + " "
                continue

            if i > 0 and tokens[i-1].lower().strip() == "number":
                if onnumber:
                    curstring += str(result + current) + " "
                    result = current = 0
                    onnumber = False
                curstring += word + " "
                continue

            num = int(word)
            if last_was_decimal:
                curstring += str(num) + " "
                last_was_decimal = False
                continue

            current = current * 1 + num
            onnumber = True
            continue

        # Handle number words
        if word in numwords:
            scale, increment = numwords[word]

            if last_was_decimal:
                curstring += str(result + current) + " "  
                result = current = 0
                last_was_decimal = False

            if scale >= 100:  # thousand, lakh, million...
                if current == 0:   # handle "thousand" without "one"
                    current = 1
                current *= scale
                result += current
                current = 0
            else:  # units, tens, hundred
                current = current * scale + increment

            onnumber = True
            continue

        # Unknown word → flush current number
        if onnumber:
            curstring += str(result + current) + " "
        curstring += word + " "
        result = current = 0
        onnumber = False
        last_was_decimal = False

    # Finalize last number
    if onnumber:
        curstring += str(result + current)

    return curstring.strip()




def preprocess_text(text):
    
    text = handle_possessive_names(text)
    
    
    text = text.lower()
    text = replace_word_hyphens_with_space(text)
    text = smart_comma(text)
    text = normalize_scales(text)
    text = normalize_payment_methods(text)
    text = re.sub(r'\b(rs\.?)\s?(\d)', r'\1 \2', text, flags=re.IGNORECASE)
    text = re.sub(r'(?<=\d),(?=\d)', '', text)
    text = re.sub(r'[^\w\s.]', '', text)
    text = re.sub(r'(?<!\d)\.(?!\d)', '', text)
    #text = re.sub(r'(?<!\d)\p{P}+(?!\.\d)', '', text)  
    #text = re.sub(r'(?<=\d)\.(?=\d)', '.', text)  
    text = fix_mobile_number(text)
    text = text2int(text)
    text= currency_to_decimal(text)
    return text

@Language.component("text_refiner")
def text_refiner(doc):
    
    refined_text = preprocess_text(doc.text)
    
    
    new_doc = spacy.tokens.Doc(doc.vocab, words=refined_text.split())
    
    
    new_doc.ents = doc.ents
    
    return new_doc
    
    