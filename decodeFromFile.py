from bitarray import bitarray
import wave
import struct
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--file', default="file.wav")
parser.add_argument('--tone0', type=int,  default=440)
parser.add_argument('--tone1', type=int, default=880)
parser.add_argument('--len', type=float, default=0.1)
args = parser.parse_args()


def undobtb(p):
    
    if p=="11110" :
        return "0000"
    if p=="01001" :
        return "0001"
    if p=="10100" :
        return "0010"
    if p=="10101" :
        return "0011"
    if p=="01010" :
        return "0100"
    if p=="01011" :
        return "0101"
    if p=="01110" :
        return "0110"
    if p=="01111" :
        return "0111"

    if p=="10010" :
        return "1000"
    if p=="10011" :
        return "1001"
    if p=="10110" :
        return "1010"
    if p=="10111" :
        return "1011"
    if p=="11010" :
        return "1100"
    if p=="11011" :
        return "1101"
    if p=="11100" :
        return "1110"
    if p=="11101" :
        return "1111"

def part(i,A):
    t=""
    for j in range(0,5):
        if A[5*i+j]:
            t+="1"
        else:
            t+="0"
    return t

def de4b5b(code):
    S=""
    n=len(code)

    for i in range(int(n/5)):
        p=part(i,code)
        #print(p)
        q=undobtb(p)
        S+=q
    
    return bitarray(S)
    

framerate = 44000
length = args.len
CHUNK = int(framerate * length)


def isOneOrNot(x):
    x = struct.unpack('{n}h'.format(n=CHUNK), x)
    x = np.array(x)
    coeff = np.fft.fft(x)
    freq = np.fft.fftfreq(len(coeff))
    i = np.argmax(np.abs(coeff))
    freq = freq[i]
    freq_in_hertz = abs(freq * framerate)
    if freq_in_hertz == args.tone0:
        return '0'
    else:
        return '1'


def decode(file):
    wf = wave.open(file, 'rb')

    code=""

    while(True):
        data = wf.readframes(CHUNK)
        if not data:
            break
        code = code + isOneOrNot(data)
        

    code=bitarray(code)
    print(code)

    for i in range(64):
        if not code[0]:
            code.remove(False)
        else:
            code.remove(True)

    print(code)


    preNRZI=""

    t=True
    for i in range(len(code)):
        if code[i]==t:
            preNRZI = preNRZI + '0'
        else:
            preNRZI = preNRZI + '1'
        t=code[i]
        

    #print(preNRZI)

    pre4b5b = de4b5b(bitarray(preNRZI))

   # print(pre4b5b)

    suma=""
    n=len(pre4b5b)
    for i in range(32):
        if pre4b5b[n-32+i]:
            suma = suma + '1'
        else: 
            suma = suma + '0'

    #
    #tu by moglo byc odpalenie funkcji division i sprawdzenie czy sie zgadza suma kontrolna
    #
    src=""
    for i in range(48):
        if pre4b5b[i]:
            src= src + '1'
        else:
            src = src + '0'
    src=bitarray(src)
   # print(src)
   
    #print(int(src.to01(),2))

    dst=""
    for i in range(48,96):
        if pre4b5b[i]:
            dst= dst + '1'
        else:
            dst = dst + '0'
    dst=bitarray(dst)
    #print(dst)
   
    #print(int(dst.to01(),2))
    
    preSum=""
    for i in range(112,n-32):
        if pre4b5b[i]:
            preSum = preSum + '1'
        else:
            preSum = preSum + '0'

    preSum = bitarray(preSum)

   # print(preSum)

    preSum=preSum.tobytes().decode('utf8')

    print(preSum)


decode(args.file)
