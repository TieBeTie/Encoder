import argparse
import sys
import json
import string

parser = argparse.ArgumentParser(description='Encoder')
subparsers = parser.add_subparsers()

parser_encode = subparsers.add_parser('encode', help='Шифратор')
parser_encode.set_defaults(mode='encode')
parser_encode.add_argument('--cipher', choices=['caesar', 'vignere'],
                           required=True, help='Введите шифр')
parser_encode.add_argument('--key', help='Ключ шифра', required=True)
parser_encode.add_argument('--input-file', help='Путь к входному файлу')
parser_encode.add_argument('--output-file', help='Путь к выходному файлу')

parser_decode = subparsers.add_parser('decode', help='Расшифратор')
parser_decode.set_defaults(mode='decode')
parser_decode.add_argument('--cipher', choices=['caesar', 'vignere'],
                           required=True, help='Введите шифр')
parser_decode.add_argument('--key', help='Ключ шифра', required=True)
parser_decode.add_argument('--input-file', help='Путь к входному файлу')
parser_decode.add_argument('--output-file', help='Путь к выходному файлу')

parser_train = subparsers.add_parser('train', help='Искусственное обучение')
parser_train.set_defaults(mode='train')
parser_train.add_argument('--cipher', choices=['caesar', 'vignere'],
                          required=True, help='Введите шифр')
parser_train.add_argument('--key', help='Ключ шифра', required=True)
parser_train.add_argument('--input-file', help='Путь к входному файлу')
parser_train.add_argument('--output-file', help='Путь к выходному файлу')

parser_hack = subparsers.add_parser('hack', help='Взлом by Vladislav Hacker')
parser_hack.set_defaults(mode='hack')
parser_hack.add_argument('--cipher', choices=['caesar', 'vignere'],
                         required=True, help='Введите шифр')
parser_hack.add_argument('--input-file', help='Путь к входному файлу')
parser_hack.add_argument('--output-file', help='Путь к выходному файлу')
parser_hack.add_argument('--model-file', help='Модель обучения', required=True)

args = parser.parse_args()


def caeser(input_text, key_=0):
    result = ""
    key_ = int(key_)
    lowercase_eng = string.ascii_lowercase
    uppercase_eng = string.ascii_uppercase

    for sym in input_text:
        if sym.islower():
            result += lowercase_eng[(ord(sym) - ord(lowercase_eng[0]) +
                                    key_) % len(lowercase_eng)]
        elif sym.isupper():
            result += uppercase_eng[(ord(sym) - ord(uppercase_eng[0]) +
                                    key_) % len(uppercase_eng)]
        else:
            result += sym
    return result


def make_key_reverse(input_key=''):
    temp_key = input_key
    reversed_key = ''
    lowercase_eng = string.ascii_lowercase
    uppercase_eng = string.ascii_uppercase

    for sym in temp_key:
        tmp_ord = ord(sym) - ord(lowercase_eng[0])
        if sym.islower():
            reversed_key += lowercase_eng[len(lowercase_eng) -
                                          (ord(sym) - ord(lowercase_eng[0]))]
        if sym.isupper():
            reversed_key += uppercase_eng[len(uppercase_eng) -
                                          (ord(sym) - ord(uppercase_eng[0]))]
    return reversed_key


def vignere(input_text, encrypt_key='', encrypt_type='encode'):
    if encrypt_type == 'decode':
        encrypt_key = make_key_reverse(encrypt_key)

    result = ''
    temp_key = encrypt_key.lower()
    key_num = 0
    lowercase_eng = string.ascii_lowercase
    uppercase_eng = string.ascii_uppercase

    for sym in input_text:
        if sym.islower():
            tmp_order = ord(sym) - ord(lowercase_eng[0])
            key_order = ord(temp_key[key_num]) - ord(lowercase_eng[0])
            result += lowercase_eng[(tmp_order + key_order) %
                                    len(lowercase_eng)]
            key_num += 1
        elif sym.isupper():
            tmp_order = ord(sym) - ord(uppercase_eng[0])
            key_order = ord(temp_key[key_num].upper()) - ord(uppercase_eng[0])
            result += uppercase_eng[(tmp_order + key_order) %
                                    len(uppercase_eng)]
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
    alphabet = string.ascii_lowercase
    result = {}
    temp_word = word.lower()
    letter_size = letter_nums(temp_word)
    for letter in alphabet:
        if letter in temp_word:
            result[letter] = temp_word.count(letter) / letter_size
        else:
            result[letter] = 0

    return result


def train(text, model):
    statistics = count_stat(text)
    data_file = open(model, 'w')
    data_file.write(json.dumps(statistics, indent=3))
    data_file.close()


def minus_stats(stats_1, stats_2):
    sum = float(0)
    for x in stats_1.keys():
        sum += abs(stats_1[x] - stats_2[x])
    return sum


def hack_caesar(encoded_text, default_stats_):
    best_index = 27
    best_stats = None

    for i in range(1, 27):
        stats_tmp = count_stat(caeser(str(encoded_text), i))
        difference = minus_stats(default_stats_, stats_tmp)
        if difference < best_stats:
            best_stats = difference
            best_index = i

    result = caeser(encoded_text, best_index)
    return result


input_string = ''
output_string = ''

if args.mode == 'encode' or args.mode == 'decode' or args.mode == 'hack':
    if args.input_file:
        input_file = open(args.input_file, 'r')
        input_string = input_file.read()
        input_file.close()
    else:
        input_string = sys.stdin.read()

if args.cipher == "caesar":
    key = int(args.key)
    if args.mode == "decode":
        key = -key
    output_string = caeser(input_string, key)
if args.cipher == "vignere":
    output_string = vignere(input_string, args.key, args.mode)

if args.mode == "train":
    text = ''
    if args.text_file:
        textFile = open(args.text_file, 'r')
        text = textFile.read()
        textFile.close()
    else:
        text = sys.stdin.read()

    train(text, args.model_file)
elif args.mode == "hack":
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
