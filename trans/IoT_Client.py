# For the file handling for the Pi.

from sense_hat import SenseHat
sense = SenseHat()
import time
import datetime
import socket
import pickle
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
import base64
import datetime

def main ():
    #Define port
    host ='192.168.0.105'

    # Define the port on which you want to connect
    port = 7800

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    # connect to server on local computer
    s.connect((host,port))
    
    getPBK(s)
    privateKey=importPrivateKey()
    durationVar=checkZero()
    sleepCheck = input("Input the interval betwen checking the sensors (seconds): ")
    sleepCheck=check4(sleepCheck)
    
    startDateTime=datetime.datetime.now()
    check=0
    count2=0
    wCount=0
    while check==0:
        checkDateTime=datetime.datetime.now()
        #print(type(checkDateTime))
        dataF, count2=piSensor(sense,sleepCheck,count2)
        wCount=writeFile(dataF,wCount,count2)
        sendFile(dataF,s,privateKey)
        
        
        if durationCheck(startDateTime,checkDateTime,durationVar)==1:
            check=1
    s.close()
    print("DONE ")
    
def checkZero():
    #The line below stores the input of the user as a variable.
    duration =input("Input time in the format Hours-Minutes-S-μS\nEg 1-2-3-0 would be 1 hour 2 minutes 3 second and 0 microseconds\nWhat duration of time would you like the sensors to run for?: ")
    durationS=duration.split("-")# THis will then split he input into 4 differnent elemets in list
    check=0
    retryC=0
    # TThe below code will check if the input given before is in the correct format that can be used.
    while check ==0:
        if len(durationS)==4:

            for i in durationS:
                if i.isdigit() == True:
                    check=1
                else:
                    retryC=1
                    break
        else:
            retryC=1

        if retryC==1:
            print("\nNot valid Try again\n")
            duration = input("Input time in the format Hours-Minutes-S-μS\nEg 1-2-3-0 would be 1 hour 2 minutes 3 second and 0 microseconds\nWhat duration of time would you like the sensors to run for?:")
            durationS = duration.split("-")

    durationVar=datetime.timedelta(hours=int(durationS[0]),minutes=int(durationS[1]),seconds=int(durationS[2]),microseconds=int(durationS[3]))
    return(durationVar)

def check4(sleepCheck):
    # This will check if the interval for checking is an acceptable value 
    count=0
    while count==0:
        if sleepCheck.isdigit() == True:
            count=count+1
        else:
            sleepCheck=input("Time between checking(seconds): ")
    return(int(sleepCheck))

#This obtains the values that sensors pick up
def piSensor(sense,sleepCheck,count2):
    time1=datetime.datetime.now()
    temp1 = sense.get_temperature()
    temp1 = ("%.2f" %temp1)
    press1 = sense.get_pressure()
    press1 = ("%.2f" %press1)
    humid1 = sense.get_humidity()
    humid1 = ("%.2f" %humid1)
    gyro1 = sense.get_gyroscope()
    #gyro1 = ("%.2f" %gyro1)
    accel1 = sense.get_accelerometer_raw()
    #accel1 = ("%.2f" %accel1)
    magn1 = sense.get_compass_raw()
    #magn1 = ("%.2f" %magn1)
    while True:
        count1=0
        #This gets another reading from the sensors to compare with the original values
        temp2 = sense.get_temperature()
        temp2 = ("%.2f" %temp2)
        press2 = sense.get_pressure()
        press2 = ("%.2f" %press2)
        humid2 = sense.get_humidity()
        humid2 = ("%.2f" %humid2)
        gyro2 = sense.get_gyroscope()
        #gyro2 = ("%.2f" %gyro2)
        accel2 = sense.get_accelerometer()
        #accel2 = ("%.2f" %accel2)
        magn2 = sense.get_compass()
        #magn2 = ("%.2f" %magn2)
        
        #This checks if the value1 and value2 are the same or not, if they are not the same then it will move on to check the next piece of data, and once all are checked, then will send the data over.
        if temp1 != temp2:
            temp1 = sense.get_temperature()
            temp1 = ("%.2f" %temp1)
            count1=1
            dataF=[str(datetime.datetime.now().date()),str(datetime.datetime.now().hour),str(datetime.datetime.now().minute),str(datetime.datetime.now().second),str(datetime.datetime.now().microsecond),str(temp2),str(press1),str(humid1),str(gyro1),str(accel1),str(magn1)]
        
        if press1 != press2:
            temp1 = sense.get_temperature()
            temp1 = ("%.2f" %temp1)
            count1=1
            dataF=[str(datetime.datetime.now().date()),str(datetime.datetime.now().hour),str(datetime.datetime.now().minute),str(datetime.datetime.now().second),str(datetime.datetime.now().microsecond),str(temp1),str(press2),str(humid1),str(gyro1),str(accel1),str(magn1)]
        
        if humid1 != humid2:
            humid1 = sense.get_humidity()
            humid1 = ("%.2f" %humid1)
            count1=1
            dataF=[str(datetime.datetime.now().date()),str(datetime.datetime.now().hour),str(datetime.datetime.now().minute),str(datetime.datetime.now().second),str(datetime.datetime.now().microsecond),str(temp1),str(press1),str(humid2),str(gyro1),str(accel1),str(magn1)]
    
        if gyro1 != gyro2:
            gyro1 = sense.get_gyroscope()
            #gyro1 = ("%.2f" %gyro1)
            count1=1
            dataF=[str(datetime.datetime.now().date()),str(datetime.datetime.now().hour),str(datetime.datetime.now().minute),str(datetime.datetime.now().second),str(datetime.datetime.now().microsecond),str(temp1),str(press1),str(humid1),str(gyro2),str(accel1),str(magn1)]
        
        if accel1 != accel2:
            accel1 = sense.get_accelerometer()
            #accesl1 = ("%.2f" %accel1)
            count1=1
            dataF=[str(datetime.datetime.now().date()),str(datetime.datetime.now().hour),str(datetime.datetime.now().minute),str(datetime.datetime.now().second),str(datetime.datetime.now().microsecond),str(temp1),str(press1),str(humid1),str(gyro1),str(accel2),str(magn1)]
        
        if magn1 != magn2:
            magn1 = sense.get_compass()
            magn1 = ("%.2f" %magn1)
            count1=1
            dataF=[str(datetime.datetime.now().date()),str(datetime.datetime.now().hour),str(datetime.datetime.now().minute),str(datetime.datetime.now().second),str(datetime.datetime.now().microsecond),str(temp1),str(press1),str(humid1),str(gyro1),str(accel1),str(magn1)]
        #print(count)
        if count1==1:
            #print("Up")
            count2=count2+1
        time.sleep(sleepCheck)
        try:
            return(dataF,count2)
        except:
            pass
        
def writeFile(dataF,wCount,count):
    fileD = open("TempData.csv", "a") #This opens the file that the data from the sensor is going to.
    for i in dataF:# This section will write the senor data into a file 
        fileD.write(i)
        fileD.write(",")
        
    wCount= wCount + 1
    print("Written "+str(wCount))
    print("Count is : "+str(count))
    #fileD.write("\n")
    fileD.close()
    return(wCount)

def timeWrite(time3):
    fileD = open("TempData.csv", "a")
    fileD.write(str(time3))
    fileD.write("\n")
    fileD.close()

def sendFile(dataF,s,privateKey): #This sends the file and the digital signature, and also any new data coming in, to the server.
    time1=datetime.datetime.now()
    #The line below imports the public key of the server and stores it as a variable
    publicKeyS=importPublicKeyS()# Both the devices and the server's public keys are imported
    publicKey=importPublicKey()
    hash=SHA512.new(pickle.dumps(dataF)) # A hash is made 
    signer = PKCS1_v1_5.new(privateKey) 
    signature=signer.sign(hash) # A signature is made 
    data=[dataF,signature,publicKey] # All data that needs to be sent is stored into a list
    dataB=pickle.dumps(data) # The list is turened into butes
    cipher=PKCS1_OAEP.new(publicKeyS) # A cipher is created 
    dataBEn=cipher.encrypt(dataB) # THe data is encrypted 
    time2=datetime.datetime.now()
    time3=time2-time1
    #The line of code below prints out the time taken to create the digital signature
    print("Time to for securing process: ",time3,"seconds")
    timeFile = open("write time SHA512.csv","a")
    timeFile.write(str(time3))
    timeFile.write("\n")
    timeFile.close()

    s.send(dataBEn) # Data is sent
    timeWrite(time3)


def durationCheck(sT,cT,durationTime): # This fucntion keep on checking if the duration that the sensor checking is up or not
    if cT>=(sT+durationTime):
        return 1
    
def importPublicKeyS():# Get the public key of the server in a usable format
    f=open("PublicKeyServer.txt","r")
    importPBK=f.read()
    #print(importPBK)
    f.close()
    publicKey=RSA.importKey(importPBK)
    #print(publicKey)
    return publicKey

def getPBK(s):
    f= open ("PublicKeyServer.txt", "wb") #Get the public key of the server from the server
    datas= s.recv(16384)
    f.write(datas)
    f.close()
    print ("Received Public Key From Server")

def importPrivateKey():#Get the private key of the device in a usable format
    f=open("PrivateKeyPi.txt","r")
    importPK=f.read()
    f.close()
    privateKey=RSA.importKey(importPK)
    #print(publicKey)
    return privateKey

def importPublicKey():# Get the public key of the device in a usable format
    f=open("PublicKeyPi.txt","r")
    importPBK=f.read()
    f.close()
    #print(publicKey)
    return importPBK
        
main()


