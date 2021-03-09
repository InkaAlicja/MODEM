# MODEM
Encoding and decoding messages to and from binary by applying:  ethernet frame, 4b5b, NRZI.

decodeFromFile.py decodes wav file, usage: decodeFromFile.py --file fileToDecode --tone0 tone0 --tone1 tone1 --len signal_len
defaults: tone0:440 tone1:880 len:0.1

decodeAudio.py decodes audio, usage: --tone0 tone0 --tone1 tone1 --len signal_len
defaults: tone0:4400 tone1:8800 len:0.05


encode.py encodes to wav file, usage: encode.py --file fileToSaveTo --text textToEncode --tone0 tone0 --tone1 tone1 --len dlugosc_sygnalu
defaults: tone0:440 tone1:880 len:0.1
