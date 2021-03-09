from bitarray import bitarray
import wave
import struct
import numpy as np
import pyaudio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--text', default="Hello World!")
parser.add_argument('--file', default="file.wav")
parser.add_argument('--tone0', type=int, default=440)
parser.add_argument('--tone1', type=int, default=880)
parser.add_argument('--len', type=float, default=0.1)
args = parser.parse_args()

def part(i,A):
    t=""
    for j in range(0,4):
        if A[4*i+j]:
            t+="1"
        else:
            t+="0"
    return t

def btb(p):
    
    if p=="0000" :
        return "11110"
    if p=="0001" :
        return "01001"
    if p=="0010" :
        return "10100"
    if p=="0011" :
        return "10101"
    if p=="0100" :
        return "01010"
    if p=="0101" :
        return "01011"
    if p=="0110" :
        return "01110"
    if p=="0111" :
        return "01111"

    if p=="1000" :
        return "10010"
    if p=="1001" :
        return "10011"
    if p=="1010" :
        return "10110"
    if p=="1011" :
        return "10111"
    if p=="1100" :
        return "11010"
    if p=="1101" :
        return "11011"
    if p=="1110" :
        return "11100"
    if p=="1111" :
        return "11101"
    


def f(s):

    A = s

    n=len(A)

    S=""

    for i in range(int(n/4)):
        p=part(i,A)
        q=btb(p)
        S+=q

    B = bitarray(S)

    print("pre NRZI")
    print(B)
    
    m=len(B)

    tf=1
    for i in range(0,m):
        if B[i]==True:
            tf=not tf
        B[i]=tf


    return(B)


class Poly:

    def __init__(self,poly):
        if(isinstance(poly,bitarray)):
            self.P=poly
        else:
            self.P=bitarray(poly)
        self.n=len(self.P)
    
    def divide(self,other):
        r=""
        for i in  range(self.n-other.n+1):
            
            if self.P[i]:
                r+='1'
            else:
                r+='0'
                continue
            
            for j in range(other.n):
                self.P[i+j]^=other.P[j]

        self.P=removeZeros(self.P)
        self.P=evenTheEnd(self.P)
        return Poly(r),self

def cut(bArr):
    result = bitarray()
    n = len(bArr)

    for i in range(32):
        result.append(bArr[n-32+i])
    
    return result

def removeZeros(x):
    while not x[0]:
        x.remove('')
        if len(x)==0:
            break
        
    return x

def evenTheEnd(A):
    while len(A)<32:
        A = bitarray([0])+A
    return A


def division(poly1,poly2):

    S=""

    for i in range(len(poly1)):
        if poly1[i]:
            S= S +'1'
        else: 
            S= S +'0'

    for i in range(32):
        S= S +'0'

    P1 = Poly(S)
    P2 = Poly(poly2)
    
    n=len(P1.P)
    m=len(P2.P)

    if(m>n):
       # print("quotient  :",0)
       # print("remainder : ", P1)
        return P1


    A,B=P1.divide(P2)
   # print(A.P)
    #print(B.P)
    #result = cut(B.P)
    result = B.P
    return (result)

def encode(src, dst, msg):

    if(isinstance(src,int)):
        src=struct.pack('!LH',src//(2**15),src%(2**15))

    if(isinstance(dst,int)):
        dst=struct.pack('!LH',dst//(2**15),dst%(2**15))

    if isinstance(msg, str):
        msg = bytes(msg, 'utf8')
    

    ramka = dst + src + struct.pack('!H',len(msg)) + msg

    RAM = bitarray()
    RAM.frombytes(ramka)

    print(RAM)

    suma = division(RAM,'100000100110000010001110110110111')
    print(suma)

    RAM = RAM + suma

    pream= '10101010' *7 + '10101011'
    PREAM = bitarray(pream)

    bity = PREAM + f(RAM) 

    print("post NRZI")
    print(f(RAM))

    print(bity)

    glosnik(bity)


def glosnik(bity):
    pa = pyaudio.PyAudio()

    amplitude = 0.1
    framerate = 44000

    #length = 0.1
    #freq1  = 440
    #freq2  = 880
        #length = 0.05
        #freq1 = 4400
        #freq2 = 8800
    length = args.len
    freq1 = args.tone0
    freq2 = args.tone1

    points = np.round(framerate*length)

    tone1 = np.sin(np.arange(points)/points*2*np.pi*freq1*length)
    tone2 = np.sin(np.arange(points)/points*2*np.pi*freq2*length)

    bytes1 = b''.join([struct.pack('h', int(e * (2**15) * amplitude)) for e in np.array(tone1)])
    bytes2 = b''.join([struct.pack('h', int(e * (2**15) * amplitude)) for e in np.array(tone2)])

    frames = b''.join([])

    for i in range(len(bity)):
        if bity[i]==True:
            frames = frames + bytes2
        else:
            frames = frames + bytes1

    wf = wave.open(args.file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(framerate)
    wf.writeframes(frames)
    wf.close()

    pa.terminate()



encode(1,2,args.text)
