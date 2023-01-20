from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from base64 import b64encode
from base64 import b64decode

users = ["Hasan","Elif","Cem","iris","Utku"]
passw = "12345"

SALT_SIZE = 16

outFile = open("1users.txt","w")

for i in range(len(users)):
	salt = b64encode(get_random_bytes(SALT_SIZE)).decode("utf-8")
	hashh = SHA256.new((passw+salt).encode("utf-8")).hexdigest()
	outFile.write(users[i] + "\t" + salt + "\t" + hashh + "\n")
outFile.close()
