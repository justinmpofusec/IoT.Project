import signal
import threading
import time
from socket import *
import re
import json
import os
from datetime import datetime
import pathlib
import logging
import logging.config
import uuid
import fcntl
import pyDH
import base64
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import (padding, utils)
from cryptography import x509
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from dotenv import dotenv_values

with open('client_conf.json', 'r') as conf:
    param = json.loads(conf.read())

SERVER_IP = param['SERVER_IP']
PORT = param['PORT']
UUID_CLIENT = param['UUID_CLIENT']
SENSOR_LIST = param['SENSOR_LIST']
NAME = re.sub('[^A-Za-z0-9 _ .-/]', '_', param['NAME'])
NAME = re.sub(' ', '_', NAME)
logging.config.fileConfig("clientLog.conf")
# Setup for cipher communication
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

config = dotenv_values(".env")  # password for private key decryption
with open('./CA/client-key.pem', 'rb') as f: pem_data = f.read()
with open('./CA/server-cert.pem', 'rb') as f: server_cert = f.read()
with open('./CA/client-cert.pem', 'rb') as f: public_data = f.read()


class Client:
    """
        Definition of the Client class which can send data from a file row by row to the server
    """

    def __init__(self):
        self.lockReceivedData = threading.Lock()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.ip = SERVER_IP
        self.port = PORT
        self.mainPath = str(pathlib.Path(__file__).parent.absolute())
        self.pathData = self.mainPath + os.sep + 'data' + os.sep
        self.receivedData = b''
        self.running = True
        self.rowToSend = ''
        self.pyName = NAME + ':' + ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        self.key = None
        self.keyPem = load_pem_private_key(pem_data, password=config["PASS"].encode('utf-8'), backend=default_backend())
        self.keyServ = x509.load_pem_x509_certificate(server_cert, backend=default_backend()).public_key()

    def encrypt(self, plain_text):
        private_key = hashlib.sha256(self.key.encode("utf-8")).digest()
        plain_text = pad(plain_text.decode("utf-8"))
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(plain_text.encode("utf-8")))

    def decrypt(self, cipher_text):
        private_key = hashlib.sha256(self.key.encode("utf-8")).digest()
        cipher_text = base64.b64decode(cipher_text)
        iv = cipher_text[:16]
        cipher = AES.new(private_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(cipher_text[16:]))

    def generate_signature(self, data):
        prehashed_msg = hashlib.sha256(data).digest()
        signature = self.keyPem.sign(prehashed_msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), utils.Prehashed(hashes.SHA256()))
        return signature

    def verify_signature(self, key, data, signature):
        prehashed_msg = hashlib.sha256(data).digest()
        try:
            key.verify(signature, prehashed_msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), utils.Prehashed(hashes.SHA256()))
        except Exception as e:
            logging.error('the signature is invalid', e)
            return False
        return True

    def sendingRoutine(self, tempMsg):
        try:
            sig = self.generate_signature(tempMsg)
            msg = self.encrypt(tempMsg + b'|' + base64.b64encode(sig))
            self.sock.send((msg + b'\n'))
            data = self.getServerRecv(True, True)
            return data == b'Ok'
        except Exception as e:
            print('sending error', e)

    def receivingRoutine(self):
        temp = self.getServerRecv(True, True)
        plain = temp[:temp.index(b'|')]
        tempSig = temp[temp.index(b'|') + 1:]
        sig = base64.b64decode(tempSig)
        if self.verify_signature(self.keyServ, plain, sig):
            self.sock.send(self.encrypt(b'Ok') + b'\n')
            return plain
        else:
            logging.error('Error in signature')
            self.sock.send('NOT OK'.encode('utf-8'))

    def parallelRecv(self):
        """
              Function to listen answer from the server without blocking the main process using daemon threads

              :return: nothing
        """
        while self.running:
            with self.lockReceivedData:
                self.receivedData = self.sock.recv(2048)
                try:
                    self.receivedData = self.receivedData[:self.receivedData.index(b'|')]
                except:
                    pass
                if self.receivedData == b'QUIT':
                    logging.info('Connection closed by the server')
                    self.sendingRoutine('QUIT'.encode('utf-8'))
                    logging.info('Server say ' + self.sock.recv(2048).decode('utf-8'))
                    self.sock.close()
                    self.running = False
                    os.kill(os.getpid(), signal.SIGINT)
                elif self.receivedData == b'':
                    logging.error('Server timeout')
                    self.sock.close()
                    self.running = False
                    os.kill(os.getpid(), signal.SIGINT)
            time.sleep(.2)

    def getServerRecv(self, needLock, encrypted=False):
        """
            Function to receive data from the server with or without using a lock

            :type needLock: bool
            :param needLock: True if the function needs to check the lock False otherwise
            :return: the string sent by the server encoded in utf-8
        """
        try:
            if needLock:
                time.sleep(.2)
                with self.lockReceivedData:
                    if encrypted:
                        return self.decrypt(self.receivedData.strip())
                    else:
                        return self.receivedData.strip()

            else:
                if encrypted:
                    return self.decrypt(self.sock.recv(2048).strip())
                else:
                    return self.sock.recv(2048).strip()
        except Exception as e:
            logging.error(e)

    def run(self):
        """
           Run the Client who start the connection to the server and the processes

           :return: None
                    self.sock.close()
        """
        try:
            self.sock.connect((self.ip, self.port))
            self.receivedData = self.sock.recv(2048)
            if self.receivedData == b"CONNECTION ENABLE":
                self.sock.send(('PY NAME = ' + self.pyName + '\n').encode())
                self.receivedData = self.sock.recv(2048)
                if self.receivedData == b'ADDRESS OK':
                    logging.info("Connection has been established with server")
                else:
                    logging.error("Connection has been established with the server but the mac address is invalid")
                    return
            elif self.receivedData == b'CONNECTION REFUSED, TOO MANY CONNECTION':
                logging.error("Connection was not established with the server, reason : too many connections to the server")
                return
            else:
                logging.error("Connection was not established with the server, reason : unknown")
                return
        except ConnectionRefusedError:
            logging.error('Connection refused, server not available')
        else:
            t = threading.Thread(target=self.parallelRecv)
            t.daemon = True
            t.start()
            self.sock.send(b'HANDSHAKE\n')
            d2 = pyDH.DiffieHellman()
            tempMsg = self.getServerRecv(True)

            d1_pubkey = int(tempMsg.decode(), 10)
            d2_pubkey = d2.gen_public_key()
            self.sock.send((str(d2_pubkey) + '\n').encode())
            tempMsg = self.getServerRecv(True)
            if (tempMsg == b'Handshake ok'):
                self.key = d2.gen_shared_key(d1_pubkey)[:16]
                msg = self.encrypt(UUID_CLIENT.encode('utf-8'))
                self.sock.send(msg + b'\n')
            else:
                logging.error("Connection has been declined by the server, reason : invalid uuid")
                return
            tempMsg = self.getServerRecv(True)
            if self.decrypt(tempMsg) == b'Send public certificate':
                print('Send public certificate')
                with open('./CA/client-cert.pem', 'rb') as f:
                    public_data = f.read()
                msg = self.encrypt(public_data) + b"\n"
                self.sock.send(msg)
                tempMsg = self.getServerRecv(True)
                if (tempMsg == b'Ok'):
                    msg = self.encrypt(b'Send signed verification')
                    self.sock.send(msg + b'\n')
                    tempMsg = self.getServerRecv(True, True)
                    tempPlain = tempMsg[:tempMsg.index(b'|')]
                    tempSig = base64.b64decode(tempMsg[tempMsg.index(b'|') + 1:])
                    if not self.verify_signature(self.keyServ, tempPlain, tempSig):
                        logging.error("Connection has been declined by the server, reason : server certificate check went wrong")
                        self.quitConnection()
                        return
                else:
                    logging.error("Connection has been declined by the server, reason : server did not receive the public key")
                    self.quitConnection()
                    return
            else:
                logging.error("Connection has been declined by the server, reason : You are not allowed to connect to this server")
                self.quitConnection()
                return
            try:
                fileName = 'dataCollectedToSend.csv'
                logging.info('send file %s', fileName)
                self.sendFile(fileName)
            except KeyboardInterrupt:
                if self.running:
                    self.quitConnection()
                else:
                    logging.info('Server closed, the client got disconnected')
            except Exception as e:
                logging.error(e)
                return
            else:
                if self.running:
                    self.quitConnection()
                else:
                    logging.info('Server closed, the client got disconnected')

    def quitConnection(self):
        time.sleep(.1)
        self.sock.send('QUIT\n'.encode())
        tmpReceivedData = self.getServerRecv(True, False)
        if tmpReceivedData == b'Goodbye':
            logging.info('Client stopped successfully')
            logging.info('Server say ' + tmpReceivedData.decode('utf-8'))
        else:
            logging.error("An error occurred when closing the connection")
        self.sock.close()

    def sendFile(self, fileName):
        """
             Function used to send CSV file row by row to the server\n
             CSV files needs to be stored in the data folder

            :type fileName: str
            :type needLock: bool
            :param fileName: path from the file in the data folder
            :param needLock: True if the function needs to check the lock False otherwise
            :return: None
        """
        if not os.path.exists(self.pathData + fileName):
            logging.error('File doesn\'t exists in data directory')
            return
        elif re.search('[^A-Za-z0-9 _ .-/]', fileName):
            logging.error('File name forbidden')
            return
        elif not fileName.split(".")[-1] == "csv":
            logging.error('File extension forbidden')
            return
        indexStart = 0
        self.sock.send('SEND\n'.encode())
        tmp = base64.b64decode(self.receivingRoutine())
        if tmp.split(b'|')[0] == b'OPTIONS':
            serverJsonKeys = json.loads(tmp.split(b'|')[1].decode('utf-8'))
            self.sendingRoutine('OK'.encode('utf-8'))
            if self.receivingRoutine() == b'OPTIONS OK, SEND FILE':
                while True:
                    try:
                        data = []
                        try:
                            with open(self.pathData + fileName) as f:
                                rows = f.readlines()
                                for row in rows:
                                    data.append(row)
                        except Exception as e:
                            logging.error(e)
                            return

                        index = 0
                        extract = []
                        found = False
                        for i in range(indexStart, len(data)):
                            rowStr = data[i].split(",")
                            if '0' in rowStr[-2]:
                                extract.append((data[i], i))
                                if not found:
                                    found = True
                                    indexStart = i

                        # isOK = True
                        print('Sending ' + str(len(extract)) + ' lines')
                        nbSendingError = 0
                        while index < len(extract):
                            (row, row_index) = extract[index]
                            self.receivedData = b'tmp'
                            if row[-3] == '0':
                                rowSplit = row.split(',')
                                rowSplit.pop(-2)
                                self.rowToSend = ','.join(rowSplit) + '\n'
                                sendData = self.pyName + "," + datetime.now().isoformat() + ',' + self.rowToSend
                                tabData = sendData.split(',')
                                newTabData = []
                                for i in range(len(serverJsonKeys)):
                                    if serverJsonKeys[i] in SENSOR_LIST:
                                        newTabData.append(tabData[SENSOR_LIST.index(serverJsonKeys[i])])
                                    else:
                                        newTabData.append(None)

                                sending_string = ','.join(newTabData)
                                self.sendingRoutine(sending_string.encode('utf-8'))
                                tmpReceivedData = self.receivingRoutine()
                                if tmpReceivedData == b'OK':
                                    print('Sending... ' + str(round((index + 1) * 100 / (len(extract)), 2)) + '%')
                                    fileWritten = False
                                    while not fileWritten:
                                        try:
                                            with open(self.pathData + fileName, 'r') as f:
                                                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                                                rows_2 = f.readlines()
                                                fcntl.flock(f, fcntl.LOCK_UN)

                                            with open(self.pathData + fileName, 'w') as f:
                                                tabReplace = rows_2[row_index].split(",")
                                                tabReplace[-2] = "1"
                                                rows_2[row_index] = ",".join(tabReplace)
                                                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                                                f.writelines(rows_2)
                                                fcntl.flock(f, fcntl.LOCK_UN)
                                                fileWritten = True
                                        except BlockingIOError:
                                            print('blocking IO Error')
                                            pass
                                        except Exception as e:
                                            logging.error(e)
                                    nbSendingError = 0
                                else:
                                    logging.error('The server was unable to record the line, a retry will be made with the next line block')
                                    if nbSendingError == 5:
                                        logging.error('The server returned too many errors, closing the connection')
                                        try:
                                            print('sending routine finish')
                                            self.sendingRoutine('FINISH'.encode('utf-8'))
                                            tmpReceivedData = self.receivingRoutine()
                                            print('receive result : ', tmpReceivedData)
                                            if tmpReceivedData == b'FINISHED':
                                                logging.info('Request to close connection accepted')
                                            else:
                                                logging.error('An error occurred when requesting to close the connection')
                                        except Exception as e:
                                            logging.error(e)
                                        return
                                    else:
                                        nbSendingError += 1
                                index += 1
                            time.sleep(.1)

                        for subdir, dirs, files in os.walk(self.pathData):
                            if 'Picture' in subdir:
                                for file in files:
                                    filepath = subdir + os.sep + file
                                    if filepath.endswith(".jpg"):
                                        time.sleep(.1)
                                        try:
                                            with open(filepath, "rb") as img_file:
                                                imgBase64 = base64.b64encode(img_file.read()).decode('utf-8')
                                                self.receivedData = b'tmp'
                                                if not imgBase64[-1] == '\n':
                                                    imgBase64 += '\n'
                                                time.sleep(1)
                                                self.sendingRoutine(b'Image_' + base64.b64encode((file + '_' + imgBase64).encode('utf-8')))
                                                tmpReceivedData = self.receivingRoutine()
                                                if tmpReceivedData == b'OK':
                                                    print('Sending image ' + file)
                                                    os.remove(filepath)
                                        except Exception as e:
                                            logging.error(e)
                        print('end')
                        time.sleep(1)
                    except KeyboardInterrupt:
                        print('Sending stopped')
                        break
                    except Exception as e:
                        logging.error(e)

                if self.running:
                    try:
                        print('sending routine finish')
                        self.sendingRoutine('FINISH'.encode('utf-8'))
                        tmpReceivedData = self.receivingRoutine()
                        print('receive result : ', tmpReceivedData)
                        if tmpReceivedData == b'FINISHED':
                            logging.info('Successful upload of the ' + fileName + ' file to the server')
                        else:
                            logging.error('Not successful upload of the ' + fileName + ' file to the server')
                    except Exception as e:
                        logging.error(e)


client = Client()
client.run()
