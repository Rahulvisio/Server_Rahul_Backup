import spacy
from spacy.language import Language
import regex as re  
import string
import re
import unicodedata

def handle_possessive_names(text):
    # Normalize Unicode and whitespace
    text = unicodedata.normalize('NFKC', text)
    text = text.replace('\u00A0', ' ')  # Replace non-breaking spaces
    text = re.sub(r'\s+', ' ', text).strip()  # Collapse extra spaces

    # Replace or remove specific patterns
    text = text.replace("'s", "")
    text = text.replace("funds", "fund")
    text = text.replace("mutual fund", "fund")
    text = text.replace("my command is", "")
    
    return text


def normalize_duration(text):
    mappings = {
        r'\b(?:per month|every month|each month)\b': 'monthly',
        r'\b(?:every day|everyday|per day|each day)\b': 'daily',
        r'\b(?:per week|every week|each week)\b': 'weekly',
        r'\b(?:semi annual|semi-annual|semi annually|semi-annually)\b': 'half yearly',
        r'\b(?:per year|every year|each year|annually)\b': 'yearly',
        r'\b(?:all fund|all list|all schemes|all funds|all scheme)\b': 'all',
        r'\b(?:best returns|good funds|best return|best returning|best fund|good return|good returns|best funds|good fund)\b': 'high return',
        r'\b(?:top returning|top return|top performing|top funds|top rated fund|top rated fund|top fund|top returning)\b': 'high return',
        r'\b(?:etfs|exchange traded fund|exchange-traded Fund)\b': 'etf',
        r'\b(?:fund of funds|fofs|fund-of-funds)\b': 'fof',
        r'\b(?:per day|every day|each day|daily)\b': 'daily',
        r'\b(?:nfos|newest available fund|newest available funds|n f o|new funds|newest fund offering|newest fund offerings)\b': 'nfo',
        r'\b(?:newly launched|newly added)\b': 'new fund',
        r'\b(?:recently released|recently launched)\b': 'recent fund',
        r'\b(?:latest schemes|latest scheme|latest funds)\b': 'latest fund',
        r'\b(?:high to low return|high to low returns|highest return|high returning|high return|high returns|highest returns|high returnings|decent returns|highest returning|highest returnings|most return)\b': 'high return',
        r'\b(?:low to high return|low to high returns|lowest return|low returning|low return|low returns|lowest returns|lowest returning|lowest returnings|least return|less return|zero return)\b': 'low return',
        r'\b(?:low-risk|without risk|risk level|minimal risk|without high risk)\b': 'low risk',
        r'\b(?:high-risk)\b': 'high risk',
        r'\b(?:debit)\b': 'debt',
        r'\b(?:short-term)\b': 'short term',
        r'\b(?:medium-term)\b': 'medium term',
        r'\b(?:long-term)\b': 'long term',
        r'\b(?:moderately risk|midrisk|mid risk|mediumrisk|medium risk)\b': 'moderate risk',
        r'\b(?:small installment|small installments|small amounts|systematic investment|systamatic investment|small amount)\b': 'sip',
        r'\b(?:one time|one shot|lampsang|lumpsom|lamsung|umpsum|lovesum|single deposit|bulk investment|bulk deposit|one-time|lump|lamp mode|oneshot|onego|onetime|a once|one go|at once)\b': 'lumpsum'
    }
    
    for pattern, replacement in mappings.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text
def normalize_scales(text):
    text = re.sub(r'\blakhs\b', 'lakh', text, flags=re.IGNORECASE)
    text = re.sub(r'\bhundreds\b', 'hundred', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthousands\b', 'thousand', text, flags=re.IGNORECASE)
    return text

import re

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

        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for word, scale in scale_mapping.items():
            numwords[word] = (scale, 0)

    ordinal_words = {
        'first': 1, 'second': 2, 'third': 3, 
        'fifth': 5, 'eighth': 8, 'ninth': 9, 'twelfth': 12
    }

    exceptions = ["which one", "this one", "the one", "one time", "only one"]

    
    placeholders = {}
    for idx, phrase in enumerate(exceptions):
        placeholder = f"EXC_{idx}"
        if phrase.lower() in textnum.lower():
            textnum = re.sub(rf"\b{re.escape(phrase)}\b", placeholder, textnum, flags=re.IGNORECASE)
            placeholders[placeholder] = phrase

    textnum = textnum.replace('-', ' ')
    words = textnum.split()

    current = result = 0
    curstring = []
    onnumber = False

    for i, word in enumerate(words):
        word_lower = word.lower()

        if word in placeholders:
            curstring.append(placeholders[word])
            continue

        if word.isdigit():
            num = int(word)
            current = current * 1 + num  
            onnumber = True
            continue

        if word_lower in ordinal_words:
            scale, increment = (1, ordinal_words[word_lower])
            current = current * scale + increment
            onnumber = True
            continue

        if word_lower == "and" and onnumber:
            continue  

        if word_lower in numwords:
            scale, increment = numwords[word_lower]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
            onnumber = True
        else:
            if onnumber:
                curstring.append(str(result + current))
            curstring.append(word)
            result = current = 0
            onnumber = False

    if onnumber:
        curstring.append(str(result + current))

    return " ".join(curstring)


def preprocess_text(text):
    
    text = handle_possessive_names(text)
    
    
    text = text.lower()
    text = re.sub(r'(?<=\w)-(?=\w)', ' ', text)
    text = normalize_duration(text)
    text = normalize_scales(text)
    text = re.sub(r'\b(rs\.?)\s?(\d)', r'\1 \2', text, flags=re.IGNORECASE)
    text = re.sub(r'(?<=\w)-(?=\w)', ' ', text)
    text = re.sub(r'(?<=\d),(?=\d)', '', text)
    text = re.sub(r'[^\w\s.]', '', text)
    text = re.sub(r'(?<!\d)\.(?!\d)', '', text)
    #text = re.sub(r'(?<!\d)\p{P}+(?!\.\d)', '', text)  
    #text = re.sub(r'(?<=\d)\.(?=\d)', '.', text)  
    text = text2int(text)
    return text

@Language.component("text_refiner")
def text_refiner(doc):
    
    refined_text = preprocess_text(doc.text)
    
    
    new_doc = spacy.tokens.Doc(doc.vocab, words=refined_text.split())
    
    
    new_doc.ents = doc.ents
    
    return new_doc

