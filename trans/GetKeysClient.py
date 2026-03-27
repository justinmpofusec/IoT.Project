import pickle
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import base64

def rsakeys():  
     length=1024
     privatekey = RSA.generate(length, Random.new().read)  
     publickey = privatekey.publickey()  
     return privatekey, publickey

def main():
    privatekey, publickey = rsakeys()
    
    exportPK=privatekey.exportKey("PEM")
    f=open("PrivateKeyPi.txt", "w")
    f.write(exportPK.decode("UTF-8"))
    f.close()
    
    exportPBK=publickey.exportKey("PEM")
    f=open("PublicKeyPi.txt", "w")
    f.write(exportPBK.decode("UTF-8"))
    f.close()
    
    print("DONE")
    
if __name__ == "__main__":
   main()
