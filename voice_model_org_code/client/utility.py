from cryptography.fernet import Fernet
import struct
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import scrypt
import base64
import datetime



def gabbar_forward(key, fin, fout, block = 1  << 19):
    if os.path.exists(os.path.join(fout)) and not os.path.exists(os.path.join(fin)) :
 
        return 0
    
    fernet =  Fernet(key)
    with  open(fin, 'rb') as fi, open(fout, 'wb')  as fo:
        while True:
            chunk = fi.read(block)
            if  len(chunk) == 0:
                break

            enc = fernet.encrypt(chunk)

            fo.write(struct.pack('<I',  len(enc)))
            fo.write(enc)
            if len(chunk) < block:
                break
    os.remove(fin)

def gabbar_backward(key, fin,  fout):
    if os.path.exists(os.path.join(fout)) and not os.path.exists(os.path.join(fin)) :

        return 0
   
    fernet =  Fernet(key)
    with  open(fin, 'rb') as fi, open(fout, 'wb')  as fo:
        while True:
            size_data = fi.read(4)
            if  len(size_data) == 0:
                 break
            chunk =  fi.read(struct.unpack('<I',  size_data)[0])
            dec =  fernet.decrypt(chunk)
            fo.write(dec)
    os.remove(fin)




def verify_license_key(password, license_key, salt, key_len=32, N=2**14, r=8, p=1):
    parts = license_key.split(".")
    if len(parts) != 3:
        return False

    ciphertext_b64, tag_b64, iv = parts
    ciphertext = base64.urlsafe_b64decode(ciphertext_b64 + "==")
    tag = base64.urlsafe_b64decode(tag_b64 + "==")

    key = scrypt(password, salt, key_len=key_len, N=N, r=r, p=p)  
    cipher = AES.new(key, AES.MODE_GCM, nonce=base64.urlsafe_b64decode(iv + "=="))

    try:
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        expiration_date = decrypted_data.decode()
        current_date = datetime.date.today()
        expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d").date()
        return current_date <= expiration_date
    except (ValueError, KeyError):
        return False
