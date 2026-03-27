# The code for the server

# The code below will import code libraries. These libraries will allow us to use code that is not available in the vanilla python.
# This means we do more within python without relying on other software

# Import socket programming library.
# This libarary will allow us to make a virtual socket in which server can use and client can connect to
import socket

# Import thread module
# This libary allows us to to run sevral instances of python at the same time. Allowing us to multitask
from _thread import *
import threading

# Import Cryptography library
# This allows is to use up to update encryption techniques that secures our program
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
import base64

# Import pickle
# A python library that allows us turn arrays into bytes that can be sent in data tranmissions
import pickle

# This is the main client thread function.
# This function will be threaded. That means it will be running parallel to the main thread
def mainThread(conn,addr,id):
    print("Device "+str(id)+ " has connected. It has ip address of "+str(addr[0]))
    sendPublicKeyServer(conn)
    writeFile(conn,addr,id)

# This function will allow the server to send the publick key to the client which they can use for encryption
def sendPublicKeyServer(conn):
    f=open("PublicKeyServer.txt","rb")
    importPBK=f.read()
    conn.sendall(importPBK)
    f.close()

# This function will get the stored private key (used for decryption) that is in string form and turn it into something that the Crypto library can use
def importPrivateKeyServer():
    f=open("PrivateKeyServer.txt","r")
    importPK=f.read()
    f.close()
    privateKey=RSA.importKey(importPK)
    return privateKey

# This function will receive the data that the client is sending. The data being sent has three parts
# The sensor data, the digital signature of the sensor data and the publick key of the device
# As the data is received the program will use praivate key to decrypt the data
# Then digital signature will used to check the validty of the data. Making sure the data was being sent from the correct place. If data is not an error will be printed
# Once the data sent is validated the data is written into a file that is unique identifiable to the device using its IP  address
def writeFile(conn,addr,id):

    privateKey=importPrivateKeyServer() # This will get the privare key of the server
    cipher=PKCS1_OAEP.new(privateKey)# This creates a cipher which can be used for encryption or decryption. In this case decryption

    while 1: # This while 1 means that this thread will wait for new that is sent forever
        try:
            data=conn.recv(8192) # Recive data. The number indicates the max amount of bytes that can be received
            dataDeB=cipher.decrypt(data) # Decrypts data
            dataDe=pickle.loads(dataDeB) # Bytes are turned into lists
            dataF=dataDe[0] # Sensor data
            signature=dataDe[1] # Signature
            hashD=SHA512.new(pickle.dumps(dataF)) # A hash is created for data validation
            publicKeyPi=RSA.importKey(dataDe[2]) # The publickey of the device is made usable

            verifier = PKCS1_v1_5.new(publicKeyPi) # An object which uses the public key to valid data if given a hash of the data and signature which was made on the client side

            if (verifier.verify(hashD,signature)): # Verifies the data. If data is valid then data will be writted into a file. If not then the data is ignored and then it awaits for new data
                f=open("TempData "+str(addr[0])+".csv","a")
                for elem in dataF:
                    f.write(elem)
                    f.write(",")
                f.write("\n")
                f.close()
                #print(str(id) + " written" )
            else:
                print("The data that device "+str(id)+" sent is not valid")
        except Exception as error:
            if error=="Ciphertext with incorrect length.":
                print("Cipher error")
                break

# This is the main function. Initally a file called Connections.csv is wiped. Then itial variables are made. For example the what the host IP and port is.
# A socket is created that the server wil use. A couple of statements are printed out to show the the state of the server
# The socket will then listen for any new connections. When a new connection is made it will check Connections.csv if the the connection was made before. If it has it will be assigned the device id it had before.
# If the device is new it will given a device id and its ip address is written into Connections.csv. Once all the checks are done it will start a new thread.
# This new thread will be run alonf the main thread. The main thread will accepting new connections will each new thread created will cator a specfic device
def main():
    f=open("Connections.csv","w")
    f.close()
    newDCounter=0
    sameCounter=False
    hostIP="192.168.0.105"
    port = 7800

    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((hostIP, port))
    print("A socket is binded to the IP address "+ str(hostIP)+ " with the port " +str(port))

    sock.listen(5)
    print("The socket is listening for connections")

    while 1:

        conn, addr = sock.accept()
        sameCounter=False
        f=open("Connections.csv","r")
        row=f.readlines()
        #print(row)
        f.close()

        if row !=[]:
            for column in row:
                column=column.split(",")
                column[1]=column[1].strip()
                #print(addr[0]) # Was used for testing
                #print(type(addr[0]))
                #print(column[1])
                #print(type(column[1]))
                if addr[0] == column[1]:
                    #print("Here")
                    tempC=newDCounter
                    newDCounter=int(column[0])
                    sameCounter=True

            if sameCounter==False:
                #print("Write Connections")
                newDCounter+=1
                f=open("Connections.csv","a")
                f.write(str(newDCounter))
                f.write(",")
                f.write(addr[0])
                f.write("\n")
                f.close()

        else:
            newDCounter+=1
            f=open("Connections.csv","a")
            f.write(str(newDCounter))
            f.write(",")
            f.write(addr[0])
            f.write("\n")
            f.close()



        start_new_thread(mainThread, (conn, addr,newDCounter,))

        sameCounter=False
        try:
            newDCounter=tempC
        except:
            pass
    sock.close()

# This find whether the code is being run from its source or from another python file. If its the former then this program will run.
if __name__ == '__main__':
    main()
