import argparse
import sys
import json

parser = argparse.ArgumentParser(description='Encoder')
parser.add_argument("coder",
                    help='Выберите действие  encode/decode/train/hack')
parser.add_argument('--cipher',
                    help='Какой шифр хотите использовать caesar|vigenere')
parser.add_argument('--key',
                    help='Какой ключ хотите использовать <number>|<word>')
parser.add_argument('--input-file',
                    help='Путь к входному файлу')
parser.add_argument('--output-file',
                    help='Путь к выходному файлу')
parser.add_argument('--model-file',
                    help='Путь к модели')
parser.add_argument('--text-file',
                    help='Путь к взламываемому файлу')
args = parser.parse_args()


def ceaser(input_text, key_=0):
    result = ""
    key_ = int(key_)
    for sym in input_text:
        if sym.islower():
            tmp_order = ord(sym) - ord('a')
            result += chr((tmp_order + key_) % 26 + ord('a'))
        elif sym.isupper():
            tmp_order = ord(sym) - ord('A')
            result += chr((tmp_order + key_) % 26 + ord('A'))
        else:
            result += sym
    return result


def make_key_reverse(input_key=''):
    temp_key = input_key
    reversed_key = ''
    for x in temp_key:
        if x.islower():
            tmp_ord = ord(x) - ord('a')
            reversed_key += chr((26 - tmp_ord) % 26 + ord('a'))
        if x.isupper():
            tmp_ord = ord(x) - ord('A')
            reversed_key += chr((26 - tmp_ord) % 26 + ord('A'))
    return reversed_key


def vignere(input_text, encrypt_key='', encrypt_type='encode'):
    if encrypt_type == 'decode':
        encrypt_key = make_key_reverse(encrypt_key)

    result = ''
    temp_key = encrypt_key.lower()
    key_num = 0
    for sym in input_text:
        if sym.isupper():
            tmp_order = ord(sym) - ord('A')
            key_order = ord(temp_key[key_num].upper()) - ord('A')
            result += chr((tmp_order + key_order) % 26 + ord('A'))
            key_num += 1
        elif sym.islower():
            tmp_order = ord(sym) - ord('a')
            key_order = ord(temp_key[key_num]) - ord('a')
            result += chr((tmp_order + key_order) % 26 + ord('a'))
            key_num += 1
        else:
            result += sym
        if key_num == len(encrypt_key):
            key_num = 0
    return result


def letter_nums(word):
    size = 0
    for x in word:
        if x.islower() or x.isupper():
            size += 1
    return size


def count_stat(word):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    result = {}
    temp_word = word.lower()
    letter_size = letter_nums(temp_word)
    for letter in alphabet:
        if letter in temp_word:
            result[letter] = temp_word.count(letter) / letter_size
        else:
            result[letter] = 0

    return result


def train(text, json_file):
    statistics = count_stat(text)
    data_file = open(json_file, 'w')
    data_file.write(json.dumps(statistics, indent=3))
    data_file.close()


def minus_stats(stats_1, stats_2):
    summa = float(0)
    for x in stats_1.keys():
        summa += abs(stats_1[x] - stats_2[x])
    return summa


def hack_caesar(encoded_text, default_stats_):
    best_index = 27
    best_stats = 20000000000000

    for i in range(1, 27):
        stats_tmp = count_stat(ceaser(str(encoded_text), i))
        difference = minus_stats(default_stats_, stats_tmp)
        if difference < best_stats:
            best_stats = difference
            best_index = i

    result = ceaser(encoded_text, best_index)
    return result

input_string = ''
output_string = ''

if args.coder == 'encode' or args.coder == 'decode' or args.coder == 'hack':
    if args.input_file:
        input_file = open(args.input_file, 'r')
        input_string = input_file.read()
        input_file.close()
    else:
        input_string = sys.stdin.read()

if args.cipher == "caesar":
    key = int(args.key)
    if args.coder == "decode":
        key = -key
    output_string = ceaser(input_string, key)
if args.cipher == "vigenere":
    output_string = vignere(input_string, args.key, args.coder)

if args.coder == "train":
    text = ''
    if args.text_file:
        textFile = open(args.text_file, 'r')
        text = textFile.read()
        textFile.close()
    else:
        text = sys.stdin.read()

    train(text, args.model_file)
elif args.coder == "hack":
    json_file = open(args.model_file, 'r')
    default_stats = json.load(json_file)
    json_file.close()
    output_string = hack_caesar(input_string, default_stats)

if args.output_file:
    output_file = open(args.output_file, 'w')
    output_file.write(output_string)
    output_file.close()
else:
    print(output_string)
