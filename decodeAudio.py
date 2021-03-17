from bitarray import bitarray
import struct
import numpy as np
import pyaudio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tone0', type=int,  default=4400)
parser.add_argument('--tone1', type=int, default=8800)
parser.add_argument('--len', type=float, default=0.05)
args = parser.parse_args()

def undobtb(p):
    if p == "11110":
        return "0000"
    if p == "01001":
        return "0001"
    if p == "10100":
        return "0010"
    if p == "10101":
        return "0011"
    if p == "01010":
        return "0100"
    if p == "01011":
        return "0101"
    if p == "01110":
        return "0110"
    if p == "01111":
        return "0111"

    if p == "10010":
        return "1000"
    if p == "10011":
        return "1001"
    if p == "10110":
        return "1010"
    if p == "10111":
        return "1011"
    if p == "11010":
        return "1100"
    if p == "11011":
        return "1101"
    if p == "11100":
        return "1110"
    if p == "11101":
        return "1111"


def part(i, A):
    t = ""
    for j in range(0, 5):
        if A[5 * i + j]:
            t += "1"
        else:
            t += "0"
    return t


def de4b5b(code):
    S = ""
    n = len(code)

    for i in range(int(n / 5)):
        p = part(i, code)
        # print(p)
        q = undobtb(p)
        S += q

    return bitarray(S)

framerate = 44000
length = args.len
CHUNK = int(framerate * length)

sample_format = pyaudio.paInt16


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
    elif freq_in_hertz == args.tone1:
        return '1'
    else:
        return 'n'


def findFactor(x):
    x = struct.unpack('{n}h'.format(n=CHUNK), x)
    x = np.array(x)
    coeff = np.fft.fft(x)
    freq = np.fft.fftfreq(len(coeff))
    for i in range(len(coeff)):
        if abs(freq[i] * framerate) == args.tone0:
            position0 = i
        if abs(freq[i] * framerate) == args.tone1:
            position1 = i
    return coeff[position0], coeff[position1]


def findOffset(stream):
    frames = []
    for i in range(20):
        frames.append(stream.read(int(CHUNK/10)))

    best = 0
    bestI = 0
    for i in range(10):
        data = b''.join(frames[i:i+10])
        a,b = findFactor(data)
        diff = abs(a/b)
        if diff > best:
            best = diff
            bestI = i

    return bestI


def decode():

    while(True):
        pa = pyaudio.PyAudio()
        print('Start')
        stream = pa.open(format=sample_format,
                channels=1,
                rate=framerate,
                frames_per_buffer=CHUNK,
                input=True)

        code = ""
        count = 0

        while (True):
            data = isOneOrNot(stream.read(CHUNK))
            if not data == 'n':     
                count = count + 1
                if count < 5:
                    continue

            if not data == 'n':     
                print('Found message')
                t = findOffset(stream)

                for i in range(t):
                    stream.read(int(CHUNK/10))   

                while(True):
                    data = isOneOrNot(stream.read(CHUNK))   
                    if(data == 'n'):
                        break
                    code = code + data
                break

        code = bitarray(code)
        print(code)

        #odcinamy preambule
        prev = 1 - code[0]
        for i in range(64):
            this = code[0]

            if not code[0]:
                code.remove(False)
            else:
                code.remove(True)

            if this == prev:
                print(i)
                break
            prev = this


        print(code)

        preNRZI = ""

        t = True
        for i in range(len(code)):
            if code[i] == t:
                preNRZI = preNRZI + '0'
            else:
                preNRZI = preNRZI + '1'
            t = code[i]

        #print(preNRZI)

        pre4b5b = de4b5b(bitarray(preNRZI))

        # print(pre4b5b)

        suma = ""
        n = len(pre4b5b)
        for i in range(32):
            if pre4b5b[n - 32 + i]:
                suma = suma + '1'
            else:
                suma = suma + '0'

        
        src = ""
        for i in range(48):
            if pre4b5b[i]:
                src = src + '1'
            else:
                src = src + '0'
        src = bitarray(src)
        # print(src)

        # print(int(src.to01(), 2))

        dst = ""
        for i in range(48, 96):
            if pre4b5b[i]:
                dst = dst + '1'
            else:
                dst = dst + '0'
        dst = bitarray(dst)
        #  print(dst)

        # print(int(dst.to01(), 2))

        preSum = ""
        for i in range(112, n - 32):
            if pre4b5b[i]:
                preSum = preSum + '1'
            else:
                preSum = preSum + '0'

        preSum = bitarray(preSum)

        #  print(preSum)

        preSum = preSum.tobytes().decode('utf8')

        print(preSum)


decode()
