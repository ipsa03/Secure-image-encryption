from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_image(input_path, output_path):
    with open(input_path, 'rb') as f:
        data = f.read()

    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(output_path, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)

    return key
def decrypt_image(input_path, output_path, key):
    with open(input_path, 'rb') as f:
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)

    with open(output_path, 'wb') as f:
        f.write(data)