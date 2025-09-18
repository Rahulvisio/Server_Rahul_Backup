import warnings
import os
warnings.filterwarnings("ignore")
os.environ['HF_HOME'] = '.dxtymnZ1000'
import sys
import requests
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, AutoConfig
from transformers.utils import is_flash_attn_2_available
import base64
import ast

from Crypto.Cipher import AES
import json
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

import os
import time
from flask import Flask, request,jsonify,render_template
from flask_cors import CORS, cross_origin
import io
import json 
import datetime  
import time

import utility as ed



app = Flask(__name__)

def lits(obfuscated_integer, custom_value):

    large_integer = obfuscated_integer // custom_value

    num_bytes = (large_integer.bit_length() + 7) // 8
    encoded_bytes = large_integer.to_bytes(num_bytes, byteorder='big')

    decoded_bytes = base64.b64decode(encoded_bytes)

    original_string = decoded_bytes.decode()
    return original_string


def decrypt_audio(key,iv,audio_bytes,isbytearray):
    aes_key=key
    aes_iv=iv
    
    decryptor = AES.new(aes_key.encode("utf-8"), AES.MODE_CBC, aes_iv.encode("utf-8"))
    if isbytearray=="True":
       aud_bytes = base64.b64decode(audio_bytes)
       decrypted_audio = decryptor.decrypt(aud_bytes)
    else:
       aud_bytes=audio_bytes.encode('latin1')
       decrypted_audio = decryptor.decrypt(aud_bytes)
    return decrypted_audio

a=b'abcdefghi'
b=b'\x96\xb8C\x1c\xbd\xd1\xcf\\1\x1f\xea\x97\xb2Q\x16\xfc'

def encrypt_text(key,iv,result):
    aes_key =key
    aes_iv = iv
    

    message_bytes = result.encode("utf-8")
    cipher = AES.new(aes_key.encode("utf-8"), AES.MODE_CBC, aes_iv.encode("utf-8"))
    padded_message = pad(message_bytes, AES.block_size)
    ciphertext_bytes = cipher.encrypt(padded_message)
    ciphertext = base64.b64encode(ciphertext_bytes).decode("utf-8")
    return ciphertext


def decrypt_text(aes_key, aes_iv,text):

    raw = b64decode(text)

    cipher = AES.new(aes_key.encode("utf-8"), AES.MODE_CBC,aes_iv.encode("utf-8"))

    return unpad(cipher.decrypt(raw[:]),AES.block_size).decode('utf-8')

# def get_key():
#     return "w}E0pYHqQw$y5^Fz@Nv8JdU#%hG4v&x["
# def get_iv():
#     return "9uP*3s7w@1RqK!2Z"
def get_key():

    res=lits(86178185228051269391038704612614327934321553677992104111909690760931028234042556698914233086148135983173048, 24)
    return res

def get_iv():
    
    res=  lits(46692849224675304715853648976984477706049710399103238520248, 24)
    return res

def enc_aut_token():
    return "DU5oBdWDgZIAhiwL2KUrdK8kUbrn7m+tPbyU0p76u9w="

device="cuda"

torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32



improvement=5
token=[(65, 70), (86, 91), (53, 58), (110, 115), (113, 118), (116, 121), (55, 60), (57, 62), (81, 86), (103, 108), (51, 56), (119, 124), (57, 62), (116, 121), (56, 61), (56, 61), (102, 107), (106, 111), (76, 81), (117, 122), (50, 55), (81, 86), (122, 127), (117, 122), (78, 83), (114, 119), (115, 120), (117, 122), (49, 54), (97, 102), (108, 113), (109, 114), (103, 108), (67, 72), (111, 116), (74, 79), (102, 107), (75, 80), (51, 56), (103, 108), (89, 94), (78, 83), (103, 108), (61, 66)]

def ds(encoded, improvement):
    d = ""
    for a, b in encoded:
        orl = b - improvement
        d += chr(orl)
    return d


a1=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (49, 73), (46, 70), (101, 125), (110, 134), (99, 123)]
a2=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (50, 74), (46, 70), (101, 125), (110, 134), (99, 123)]
a3=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (51, 75), (46, 70), (101, 125), (110, 134), (99, 123)]
a4=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (52, 76), (46, 70), (101, 125), (110, 134), (99, 123)]
a5=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (53, 77), (46, 70), (101, 125), (110, 134), (99, 123)]
a6=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (56, 80), (46, 70), (101, 125), (110, 134), (99, 123)]
a7=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (57, 81), (46, 70), (101, 125), (110, 134), (99, 123)]
a8=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (101, 125), (109, 133), (112, 136), (49, 73), (48, 72), (46, 70), (101, 125), (110, 134), (99, 123)]


b1=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (97, 121), (100, 124), (100, 124), (101, 125), (100, 124), (95, 119), (116, 140), (111, 135), (107, 131), (101, 125), (110, 134), (115, 139), (46, 70), (106, 130), (115, 139), (111, 135), (110, 134)]
b2=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (110, 134), (111, 135), (114, 138), (109, 133), (97, 121), (108, 132), (105, 129), (122, 146), (101, 125), (114, 138), (46, 70), (106, 130), (115, 139), (111, 135), (110, 134)]
b3=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (116, 140), (111, 135), (107, 131), (101, 125), (110, 134), (105, 129), (122, 146), (101, 125), (114, 138), (46, 70), (106, 130), (115, 139), (111, 135), (110, 134)]
b4=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (46, 70), (106, 130), (115, 139), (111, 135), (110, 134)]
b5=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (112, 136), (114, 138), (101, 125), (112, 136), (114, 138), (111, 135), (99, 123), (101, 125), (115, 139), (115, 139), (111, 135), (114, 138), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (46, 70), (106, 130), (115, 139), (111, 135), (110, 134)]
b6=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (118, 142), (111, 135), (99, 123), (97, 121), (98, 122), (46, 70), (106, 130), (115, 139), (111, 135), (110, 134)]
b7=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (115, 139), (112, 136), (101, 125), (99, 123), (105, 129), (97, 121), (108, 132), (95, 119), (116, 140), (111, 135), (107, 131), (101, 125), (110, 134), (115, 139), (95, 119), (109, 133), (97, 121), (112, 136), (46, 70), (106, 130), (115, 139), (111, 135), (110, 134)]
b8=[(109, 133), (111, 135), (100, 124), (101, 125), (108, 132), (95, 119), (99, 123), (111, 135), (110, 134), (102, 126), (105, 129), (103, 127), (47, 71), (109, 133), (101, 125), (114, 138), (103, 127), (101, 125), (115, 139), (46, 70), (116, 140), (120, 144), (116, 140)]

s=time.time()
ed.gabbar_backward(ds(token, improvement), ds(a1, 24),  ds(b1, 24))
ed.gabbar_backward(ds(token, improvement),  ds(a2, 24),  ds(b2, 24))
ed.gabbar_backward(ds(token, improvement),  ds(a3, 24),  ds(b3, 24))
ed.gabbar_backward(ds(token, improvement),  ds(a4, 24),  ds(b4, 24))
ed.gabbar_backward(ds(token, improvement),  ds(a5, 24),  ds(b5, 24))


ed.gabbar_backward(ds(token, improvement),  ds(a6, 24),  ds(b6, 24))
ed.gabbar_backward(ds(token, improvement),  ds(a7, 24),  ds(b7, 24))
ed.gabbar_backward(ds(token, improvement),  ds(a8, 24),  ds(b8, 24))




mc=[(109, 210), (111, 212), (100, 201), (101, 202), (108, 209), (95, 196), (99, 200), (111, 212), (110, 211), (102, 203), (105, 206), (103, 204), (47, 148)]

def get(mc):

    processor = AutoProcessor.from_pretrained(mc,cache_dir=None,local_files_only=True)
    config=AutoConfig.from_pretrained(mc,cache_dir=None,local_files_only=True)
    return processor,config
processor,config = get(ds(mc,101))

ed.gabbar_forward(ds(token, improvement),ds(b1, 24),ds(a1, 24))
ed.gabbar_forward(ds(token, improvement),ds(b2, 24),ds(a2, 24))
ed.gabbar_forward(ds(token, improvement),ds(b3, 24),ds(a3, 24))
ed.gabbar_forward(ds(token, improvement),ds(b4, 24),ds(a4, 24))
ed.gabbar_forward(ds(token, improvement),ds(b5, 24),ds(a5, 24))


ed.gabbar_forward(ds(token, improvement),ds(b6, 24),ds(a6, 24))
ed.gabbar_forward(ds(token, improvement),ds(b7, 24),ds(a7, 24))
ed.gabbar_forward(ds(token, improvement),ds(b8, 24),ds(a8, 24))



c1=[(103, 326), (97, 320), (98, 321), (98, 321), (97, 320), (114, 337), (95, 318), (109, 332), (111, 334), (100, 323), (101, 324), (108, 331), (47, 270), (116, 339), (101, 324), (109, 332), (112, 335), (55, 278), (46, 269), (101, 324), (110, 333), (99, 322)]
c2=[(103, 326), (97, 320), (98, 321), (98, 321), (97, 320), (114, 337), (95, 318), (109, 332), (111, 334), (100, 323), (101, 324), (108, 331), (47, 270), (116, 339), (101, 324), (109, 332), (112, 335), (49, 272), (49, 272), (46, 269), (101, 324), (110, 333), (99, 322)]
d1=[(103, 326), (97, 320), (98, 321), (98, 321), (97, 320), (114, 337), (95, 318), (109, 332), (111, 334), (100, 323), (101, 324), (108, 331), (47, 270), (103, 326), (101, 324), (110, 333), (101, 324), (114, 337), (97, 320), (116, 339), (105, 328), (111, 334), (110, 333), (95, 318), (99, 322), (111, 334), (110, 333), (102, 325), (105, 328), (103, 326), (46, 269), (106, 329), (115, 338), (111, 334), (110, 333)]
d2=[(103, 326), (97, 320), (98, 321), (98, 321), (97, 320), (114, 337), (95, 318), (109, 332), (111, 334), (100, 323), (101, 324), (108, 331), (47, 270), (112, 335), (121, 344), (116, 339), (111, 334), (114, 337), (99, 322), (104, 327), (95, 318), (109, 332), (111, 334), (100, 323), (101, 324), (108, 331), (46, 269), (98, 321), (105, 328), (110, 333)]
ed.gabbar_backward(ds(token, improvement), ds(c1, 223), ds(d1, 223))
ed.gabbar_backward(ds(token, improvement),ds(c2, 223),ds(d2, 223))
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    "gabbar_model/",config=config,cache_dir=None, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=False,local_files_only=True
)

model.to(device)

def get_pipeline(model):
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model, 
        torch_dtype=torch.float16,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,

        device="cuda:0", 
        model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )
    return pipe
gabbar_generator=get_pipeline(model)
def gabbar_batch_process(gabbar_generator, audio_bytes, batch_size=8, language='english',task='transcribe'):
    return gabbar_generator(
            audio_bytes,
            chunk_length_s=30,
            batch_size=batch_size,
            return_timestamps=False,
            generate_kwargs={"language":language,"task":task}
        )

ed.gabbar_forward(ds(token, improvement),ds(d1, 223),ds(c1, 223))
ed.gabbar_forward(ds(token, improvement),ds(d2, 223),ds(c2, 223))




print("model loaded")

 

@app.route("/" ,methods=["GET"])
def hello():

    return "hello"




@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:

        s=time.time()
        transcriptions_result_list = []
        audio_files = request.get_json()


        audio_files=json.loads(audio_files['data'])

        audio_bytes = []
        audio_ids = []

        audio_iv=[]
        audio_key=[]
        for audio_file in audio_files:


            license_key=audio_file['LCK']
            if  license_key == "None":
               return jsonify([{"error":"Inavalid Access"}])
            if not license_key:
               return jsonify([{"error":"Inavalid Access"}])

            if not ed.verify_license_key(a, license_key, b):
               return jsonify([{"error": "Invalid or expired"}])
            text=audio_file['text']
            decrypted_key = ast.literal_eval(decrypt_text(get_key(), get_iv(),text))
            aud_bytes=decrypt_audio(decrypted_key['key'],decrypted_key['iv'],audio_file['audio'],audio_file['isByteArray']) 
            audio_bytes.append(aud_bytes)
            audio_ids.append(audio_file['id'])


            audio_iv.append(decrypted_key['iv'])
            audio_key.append(decrypted_key['key'])

       
        outputs=gabbar_batch_process(gabbar_generator,audio_bytes)
        outputs = [encrypt_text(audio_key[i],audio_iv[i],outputs[i]['text']) for i in range(len(outputs))]
        

        e = time.time()

        transcriptions_result_list = [{"num_audio":len(audio_files),"duration":round(time.time()-s,3),"uid":audio_ids[i],"text":outputs[i]} for i in range(len(outputs))]

        dur = e - s

        return jsonify(transcriptions_result_list)
    except Exception as e:
        print(e)
        return str(e)

@app.route("/translate", methods=["POST"])
def translate_audio():
    try:

        s=time.time()
        transcriptions_result_list = []
        audio_files = request.get_json()


        audio_files=json.loads(audio_files['data'])

        audio_bytes = []
        audio_ids = []

        audio_iv=[]
        audio_key=[]
        audio_task=[]
        language="en"
        for audio_file in audio_files:


            license_key=audio_file['LCK']
            if  license_key == "None":
               return jsonify([{"error":"Inavalid Access"}])
            if not license_key:
               return jsonify([{"error":"Inavalid Access"}])

            if not ed.verify_license_key(a, license_key, b):
               return jsonify([{"error": "Invalid or expired"}])
            text=audio_file['text']
            language=audio_file['lang']
            decrypted_key = ast.literal_eval(decrypt_text(get_key(), get_iv(),text))
            aud_bytes=decrypt_audio(decrypted_key['key'],decrypted_key['iv'],audio_file['audio'],audio_file['isByteArray']) 
            audio_bytes.append(aud_bytes)
            audio_ids.append(audio_file['id'])
            audio_task.append(audio_file['task'])


            audio_iv.append(decrypted_key['iv'])
            audio_key.append(decrypted_key['key'])

       
        outputs=gabbar_batch_process(gabbar_generator,audio_bytes,task='translate',language=language)
        outputs = [encrypt_text(audio_key[i],audio_iv[i],outputs[i]['text']) for i in range(len(outputs))]
        

        e = time.time()

        transcriptions_result_list = [{"num_audio":len(audio_files),"duration":round(time.time()-s,3),"uid":audio_ids[i],"text":outputs[i]} for i in range(len(outputs))]



        return jsonify(transcriptions_result_list)
    except Exception as e:
        print(e)
        return str(e)






    
if __name__ == "__main__":
    app.run(debug=False)
