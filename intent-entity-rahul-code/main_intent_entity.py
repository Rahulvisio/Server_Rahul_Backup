
from langchain.schema.runnable import RunnableLambda
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

import audio
import io
import torch
import os
import csv
from flask import send_file
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from flask import Flask, request, jsonify
import time
from Crypto.Cipher import AES
import json
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
app = Flask(__name__)


def decrypt_audio():
    AES_KEY = request.form["key"]
    AES_IV = request.form["iv"]
    isByteArray = request.form.get("isByteArray")
    data = ""
    decryptor = AES.new(AES_KEY.encode("utf-8"), AES.MODE_CBC, AES_IV.encode("utf-8"))
    if isByteArray == "True":
        print("request bytearray")
        base64_bytes = request.form["audio"].encode("utf-8")
        # print("base64 bytes",base64_bytes)
        bytes = b64decode(base64_bytes)
        decrypted_audio = decryptor.decrypt(bytes)
        data = io.BytesIO(decrypted_audio)
        data=audio.decode_audio(data)
    else:
        print("request file")
        decrypted_audio = decryptor.decrypt(request.files["audio"].read())
        data = io.BytesIO(decrypted_audio)
        data=audio.decode_audio(data)
    return data


def encrypt_text(result):
    AES_KEY = request.form["key"]
    AES_IV = request.form["iv"]
    message_bytes = result.encode("utf-8")
    cipher = AES.new(AES_KEY.encode("utf-8"), AES.MODE_CBC, AES_IV.encode("utf-8"))
    padded_message = pad(message_bytes, AES.block_size)
    ciphertext_bytes = cipher.encrypt(padded_message)
    ciphertext = b64encode(ciphertext_bytes).decode("utf-8")
    return ciphertext


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

v_model_id = "openai/whisper-large-v2"

v_model = AutoModelForSpeechSeq2Seq.from_pretrained(
    v_model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
hi_v_model = AutoModelForSpeechSeq2Seq.from_pretrained(
    v_model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
# v_model.to(device)

v_processor = AutoProcessor.from_pretrained(v_model_id)
'''
gabbar_generator = pipeline(
    "automatic-speech-recognition",
    model=v_model,
    tokenizer=v_processor.tokenizer,
    feature_extractor=v_processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    ignore_warning=True
)
'''
print("voice model loaded")

import re
def update_entities(data):
    text = data.get('text', '').lower()
    entities = data.get('entities', {})
    intent = data.get('intent', '').lower()

    if intent != 'payment':
        return data  # Apply only for Payment intent

    pronouns = {'another','other','another linked account'}
    if entities.get('PER') and entities['PER'].lower() in pronouns:
        entities['PER'] = None
        if  entities.get('MODE') == 'Bank':
            entities['MODE'] = 'Self'
    # 1. If PER exists and mode='Self', change to 'Bank'
    elif entities.get('PER') and entities.get('MODE') == 'Self':
        entities['MODE'] = 'Bank'

    # 2. If PER is pronoun-like words, remove it
    pronouns = {'him', 'her', 'my', 'me', 'myself', 'i', 'mine', 'our', 'us'}
    if entities.get('PER') and entities['PER'].lower() in pronouns:
        entities['PER'] = None

    # 3. Detect if user is transferring to their own account → mode='Self'


    # 4. Detect if user is sending from their account → mode='Bank'
    from_my_account_phrases = [
        "from my account", "from my bank", "from my own account"
    ]
    if any(phrase in text for phrase in from_my_account_phrases):
        print("phrase matched for from my account",entities)
        # If mode already set to Self (due to previous rule), keep Self
        if entities.get('MODE') == 'Self':
            entities['MODE'] = 'Bank'
    
    self_transfer_phrases = [
        "to my account", "into my account", "in my account", "to my saving account","to my linked account","to my other account","to my another account","to my bank"
    ]
    if any(phrase in text for phrase in self_transfer_phrases):
        
        entities['MODE'] = 'Self'

    # 6. Validate MOBILE → only digits allowed
    if entities.get('MOBILE') and not entities['MOBILE'].isdigit():
        entities['MOBILE'] = None
    data['entities'] = entities
    return data


def clean_entities(data):
    text = data.get('text', '').lower()
    entities = data.get('entities', {})
    intent = data.get('intent', '').lower()
    number_pattern = r'\d+'
    if intent == 'checkbalance':
        bool_number = re.search(number_pattern, text) is not None
        if bool_number:
            
            data['intent'] = 'Random'
        return data


    elif entities.get('AMT')  and  intent == 'checkbalance':
            data['intent'] = 'Random'
    if intent != 'payment':
        return data  # Apply only for Payment intent

    # 1. If PER exists and MODE = 'Self', change it to 'Bank'

    pronouns = {'another','other','another linked account'}
    if entities.get('PER') and entities['PER'].lower() in pronouns:
        entities['PER'] = None
        # if  entities.get('MODE') == 'Bank':
        #     entities['MODE'] = 'Self'

    # 2. Remove PER if it is a pronoun
    pronouns = {'him', 'her', 'my', 'me', 'myself', 'i', 'mine', 'our', 'us'}
    if entities.get('PER') is not None and entities['PER'].strip().lower() in pronouns:
        entities['PER'] = None
    from_pattern = r"from\s+my\s+([a-z]+\s+)?account"
    if re.search(from_pattern, text):
        # Do not override if already set to Self
        if entities.get('MODE') == 'Self':
            entities['MODE'] = 'Bank'
    # 3. Detect transfer TO user's own account → MODE = 'Self'
    # Pattern: "to/on/in/into my (saving|current|loan|...)? account" OR "to my <bank name> account"
    self_pattern = r"(to|on|in|into|for)\s+(my|other|another|current)\s+([a-z]+\s+)?account"
    if re.search(self_pattern, text):
        entities['MODE'] = 'Self'
    self_pattern = r"(to|on|in|into|for)\s+ my\s+([a-z]+\s+)?account"
    if re.search(self_pattern, text):
        entities['MODE'] = 'Self'
    self_pattern = r"cell?transfer"
    if re.search(self_pattern, text):
        entities['MODE'] = 'Self'
    # 4. Detect transfer FROM user's account → MODE = 'Bank'
    # Pattern: "from my account" OR "from my (own|saving|current) account"

    if entities.get('BANK_NAME') and  entities.get('MODE') == 'Bank':
            entities['MODE'] = 'Self'
    if entities.get('PER') and entities.get('MODE') == 'Self':
        entities['MODE'] = 'Bank'
    # 5. Validate MOBILE → only digits allowed
    if entities.get('AMT') and entities.get('MOBILE'):
        entities['MODE'] = 'UPI'


    if entities.get('MOBILE') and not entities['MOBILE'].isdigit():
        entities['MOBILE'] = None
    data['entities'] = entities
    return data
def remove_nulls(obj):
    if isinstance(obj, dict):
        return {k: remove_nulls(v) for k, v in obj.items() if v is not None and v != "null"}
    elif isinstance(obj, list):
        return [remove_nulls(i) for i in obj if i is not None and i != "null"]
    else:
        return obj
torch.random.manual_seed(0)
# model_path = "microsoft/Phi-4-mini-instruct"
model_path = "Qwen/Qwen3-4B-Instruct-2507"

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="cuda",
    torch_dtype=torch.float16,
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_path)
pipe=pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
)

generation_args = {
    "max_new_tokens": 150,
    "return_full_text": False,
    "temperature": 0.0,
    "do_sample": False,
}

def custom_llm(input):
    messages=[{"content": input.text, "role": "user"}]
    output = pipe(messages, **generation_args)
    return output[0]["generated_text"]

model=RunnableLambda( lambda x :custom_llm(x))
print("llm loaded")
from pydantic import BaseModel, Field
from typing import List
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class IntentEntities(BaseModel):
    intent: str = Field(
        description="The detected intent of the user query."
    )
    entities: Dict[str, str] = Field(
        description=(
            "Key-value pairs of extracted entities. "
            "Use null if entity is not applicable."
        )
    )

# Step 2: Create parser
parser = PydanticOutputParser(pydantic_object=IntentEntities)

# Step 3: Prompt template
template = PromptTemplate(
    template=(
        """
You are an AI assistant for banking and telecom tasks. Analyze the user query in 4 stages:

---

### Stage 1: Extract Entities
- AMT: Numeric amount in digits only.Numeric amount in digits only.only Convert amount to decimal format if paisa or paise term exist for Indian rupee:
399 plan -> 399 (plan is equivalent to rupees)
70 rupees 50 paise → 70.50
1 rupee 10 paisa → 1.10
rupees 250 -> 250

but If only rupees mentioned, use integer (e.g., 50 rupees → 50).Amount can be dollar as well $3.99 -> 3.99, 50 dollars -> 50 .Give 20 -> 20.
- Operator: Telecom provider name (Jio, Airtel, Vodafone, BSNL). Must NOT be a person name.
- PAY M: Explicit payment method (UPI, debit card, Mobile, credit card, RTGS, NEFT, IMPS). Do not assume.
- MOBILE: can be any of number of digit  number without spaces or symbols.
- PER: Human name in the query ,Human name can not be "another" or "other" etc
- MODE : It tells mode of payment on basis of if Intent found 'Payment' and based on pay mode found like 'neft','rtgs',imps' -> MODE='Bank', if 'upi' -> MODE='UPI' otherwise MODE='null'
- BANK_NAME: If only Bank like sbi ,upi,axis,federal,hdfc,sib,nippon etc present

Rules:
- Correct obvious misspellings (e.g., 'ubi' → 'UPI', 'nft','naft','any FT','FT','any FD','FD' → 'NEFT' , 'ims' -> 'IMPS').
- If entity is not present, keep it `null`.
- Do NOT hallucinate.
- when converting word to number in case of mobile number insure double five means 55 not 52 and same for similar case like triple 5 is 555 not 53 or 55
- If sentence strt with any FD,any FT it means NEFT is there
- In Intent='Payment' there can't be any entity Operator
- If Text contain Person entity only Intent can't be 'CheckBalance','TransactionHistory','ScanAndPay'
- Person name can not be "another" or "other" or "another linked account" etc in that case put PER=null
---

### Stage 2: Determine Intent
Choose one:
   - CheckBalance: User wants to know their current account or wallet balance.
   - TransactionHistory: User asks for a list of past transactions, debits, or credits.
   - Payment: User wants to make a payment or give rs x.x.x or move money to a person, service provider, or biller. This includes any digital payments (UPI, wallet, Mobile) as well> - ScanAndPay: User intends to scan a QR code or barcode to pay a merchant.
   - Recharge: User wants to recharge/prepay a mobile number, DTH, or data pack.
   - LastRecharge: User wants details about the most recent recharge done and says "repeat my recharge" or "last" or "previous" or "previous pack" or "last plan".
   - Modify: User wants to edit or change a previously given field like name, amount, etc.
   - Cancel: User intends to cancel their request.
   - Random: Use this if the query does not match any of the above intents.


Rules:
- If recharge or top up, prepaid etc mentioned → Recharge.
- If QR or scan mentioned → ScanAndPay.
- If amount or PER or MOBILE present → Payment.
- If query asks balance → CheckBalance.
- If past recharge or last recharge → LastRecharge.
- If modify/edit/change → Modify.
- If cancel,dont't → Cancel.
- If unclear → Random.
- Rupees variations are -> rs. ,rupees, rs

---

### Stage 3: Extract Entities
- MODE : It tells mode of payment on basis of if Intent found 'Payment' and based on pay mode found like 'neft','rtgs',imps' -> MODE='Bank', if 'upi' -> MODE='UPI' otherwise MODE='null'
MODE should be one of:
- 'UPI' → if explicitly mentioned or QR/scan or MOBILE number present.
- 'Bank' → if NEFT, RTGS, IMPS, or words like 'account' or 'bank' appear in user input.
- 'Self' → if user says "my" or "send to me" or "my account" or "my other account" or "my another account" or "my saving account"   and no PER.
- Else → `null`.
Rules:
- IF only AMT(amount) and PER(person name) enity extracted then MODE=='null',IF PER(person name) only found then MODE=='null' but if sentnec contain freinds'account or 'Jyoti's bank/account' then MODE='Bank' sure.
- 'Operator' entity can not be come when Intent is 'Payment'
- If PAY M='IMPS' ,MODE must be 'BANK' Not "UPI"
- For AMT exists ,Intent can not be CheckBalance for sure. If sentence contain only " Rs. 10,000." like sentence then extract AMT -> 10000 and Intent='Random'
- For MODE='Self' some variation words in user input are cell transfer,etc

### Stage 4:correct Entities
- If user input contain words like another,other ,account ,linked etc .It can not be PER(person name) entity so put PER=null
- For user input like this "Make a transfer to my Friend" here Friend is PER entity but MODE='null' not 'Bank' because account or bank sense not found.
- For user input like this Transfer money  to my other account from my account intent is 'Payment',MODE='Self' not 'Modify'
- For user input like wire 200 -> AMT=200,MODE='null' because no pay mode found
- For user input like this recharge on Jyoti's number 350 rupees. ,Intent is 'Recharge' sure ,PER='Jyoti',AMT=350,MOBILE='null' not same as amount

---
### Output
- The output must strictly follow the provided JSON schema.


"""
        "\n"
        "User query: {user_input}\n"
        "{format_instructions}"
    ),
    input_variables=["user_input"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# print(template.partial_variables)
chain = template | model
CSV_FILE='data.csv'
FIELDS=['text','intent','entities']
# final_result = chain.invoke({'user_input':"How much money i have left"})

import json
def get_pipeline(model):
    pipe = pipeline(
        "automatic-speech-recognition",
        model=v_model, 
        torch_dtype=torch.float16,
        tokenizer=v_processor.tokenizer,
        feature_extractor=v_processor.feature_extractor,

        device="cuda:0", 
    )
    return pipe
def gabbar_batch_process(gabbar_generator, audio_files, batch_size=8, language='english', task = 'transcribe'):

    return gabbar_generator(
            audio_files,
            chunk_length_s=30,
            batch_size=batch_size,
            return_timestamps=False,
            generate_kwargs={"language":language,"task":task},
           
        )
gabbar_generator=get_pipeline(v_model)
hi_gabbar_generator=get_pipeline(hi_v_model)
def get_suppressed_tokens(tokenizer):
    bad_tokens_str = [
        r"0", r"1", r"2", r"3", r"4", r"5", r"6", r"7", r"8", r"9", "$", "£"
    ]
    tokens_dict = {}
    result = []

    for token_num in range(tokenizer.vocab_size):
        token_str = tokenizer.decode([token_num]).strip()
        for bad_token in bad_tokens_str:
            if bad_token not in tokens_dict:
                tokens_dict[bad_token] = [False, [], []]

            if not tokens_dict[bad_token][0]:
                if bad_token in token_str:
                    tokens_dict[bad_token][1].append(token_num)
                    tokens_dict[bad_token][2].append(token_str)

    for k, v in tokens_dict.items():
        tokens_dict[k][0] = True
        if k in bad_tokens_str:
            result += v[1]

    return list(set(result))
v_tokenizer = v_processor.tokenizer
suppressed_tokens=get_suppressed_tokens(v_tokenizer)
#hi_gabbar_generator.model.generation_config.suppress_tokens+=suppressed_tokens
#hi_gabbar_generator.model.generation_config.suppress_tokens+=[21643,502,568,805,1017,1025,1386,1614,1649,1722,16513,31877]

@app.route("/intent" ,methods=["POST"])
def intent():
    try:
        print('req came')
        s=time.monotonic()
        text = request.form['text']

  
        final_result = chain.invoke({'user_input':text})
        print("-->",final_result)
        final_result=final_result.replace("```json","")
        final_result=final_result.replace("```","")
        final_result=json.loads(final_result)

        final_result['text']=text

        final_result=remove_nulls(final_result)
        final_result=clean_entities(final_result)
        
        res=json.dumps(final_result)
        # print("llm inference time",time.monotonic()-e1)

        print(res)
        # text=encrypt_text(res)

        return {"duration":time.monotonic()-s,"text":text,"result":res}
    except Exception as e:
         print("Error::", str(e))
#         # logger.error(f"Error:: \n{e}")
         return str(e)

@app.route("/transcribe" ,methods=["POST"])
def transcribe():
    try:
        print('req came transcribe')
        s=time.monotonic()
        lang = request.form.get('lang','en')

        data=decrypt_audio()
        # forced_decoder_ids = processor.get_decoder_prompt_ids(language=lang, task="transcribe")
        result = gabbar_batch_process(gabbar_generator,data, task = 'transcribe',language=lang)
        print("voice inference time",time.monotonic()-s)
        e1=time.monotonic()
        final_result = chain.invoke({'user_input':result['text']})
        #print("-->",final_result)
        final_result=final_result.replace("```json","")
        final_result=final_result.replace("```","")
        print("llm inference time",time.monotonic()-e1)
        final_result=json.loads(final_result)
        final_result['text']=result['text']
        final_result=remove_nulls(final_result)
        final_result=clean_entities(final_result)

        res=json.dumps(final_result)

        file_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if not file_exists:
               writer.writeheader()
            writer.writerow({"text": final_result["text"], "intent": final_result["intent"],"entities":final_result["entities"]})
        print(res)
        text=encrypt_text(res)

        return {"duration":time.monotonic()-s,"text":text,"model_time":e1-s,"llm_time":time.monotonic()-e1}
    except Exception as e:
         print("Error::", str(e))
#         # logger.error(f"Error:: \n{e}")
         return str(e)

@app.route("/translate" ,methods=["POST"])
def translatet():
    try:
        print('req came translate')
        s=time.time()
        lang = request.form.get('lang','en')
        data=decrypt_audio()
        # forced_decoder_ids = processor.get_decoder_prompt_ids(language=lang, task="transcribe")
        result = gabbar_batch_process(hi_gabbar_generator,data, task = 'transcribe',language='en')
        print("voice inference time",time.monotonic()-s)
        e1=time.monotonic()
#        final_result = chain.invoke({'user_input':result['text']})
        print("llm inference time",time.monotonic()-e1)
 #       final_result=json.loads(final_result)
  #      final_result['text']=result['text']
   #     res=json.dumps(final_result)
        res=result['text']
        print(res)
        text=encrypt_text(res)
       # return {"duration":time.monotonic()-s,"text":text,"model_time":e1-s,"llm_time":time.monotonic()-e1}
        return {"duration":time.monotonic()-s,"text":text}
    except Exception as e:
         print("Error::", str(e))
#         # logger.error(f"Error:: \n{e}")
         return str(e)

@app.route("/view", methods=["GET"])
def view_csv():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "CSV file not found"}), 404

    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    return jsonify(rows)

# --- Download CSV file ---
@app.route("/download", methods=["GET"])
def download_csv():
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "CSV file not found"}), 404

    return send_file(CSV_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
