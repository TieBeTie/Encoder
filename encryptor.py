import argparse
import json
import string
import sys

parser = argparse.ArgumentParser(description='Encoder')
subparsers = parser.add_subparsers()

parser_encode = subparsers.add_parser('encode', help='Шифратор')
parser_encode.set_defaults(mode='encode')
parser_encode.add_argument('--cipher', choices=['caesar', 'vigenere'],
                           required=True, help='Введите шифр')
parser_encode.add_argument('--key', help='Ключ шифра', required=True)
parser_encode.add_argument('--input-file', help='Путь к входному файлу')
parser_encode.add_argument('--output-file', help='Путь к выходному файлу')

parser_decode = subparsers.add_parser('decode', help='Расшифратор')
parser_decode.set_defaults(mode='decode')
parser_decode.add_argument('--cipher', choices=['caesar', 'vigenere'],
                           required=True, help='Введите шифр')
parser_decode.add_argument('--key', help='Ключ шифра', required=True)
parser_decode.add_argument('--input-file', help='Путь к входному файлу')
parser_decode.add_argument('--output-file', help='Путь к выходному файлу')

parser_train = subparsers.add_parser('train', help='Искусственное обучение')
parser_train.set_defaults(mode='train')
parser_train.add_argument('--cipher', choices=['caesar', 'vigenere'],
                          required=True, help='Введите шифр')
parser_train.add_argument('--key', help='Ключ шифра', required=True)
parser_train.add_argument('--input-file', help='Путь к входному файлу')
parser_train.add_argument('--output-file', help='Путь к выfходному файлу')

parser_hack = subparsers.add_parser('hack', help='Взлом by Vladislav Hacker')
parser_hack.set_defaults(mode='hack')
parser_hack.add_argument('--cipher', choices=['caesar', 'vigenere'],
                         required=True, help='Введите шифр')
parser_hack.add_argument('--input-file', help='Путь к входному файлу')
parser_hack.add_argument('--output-file', help='Путь к выходному файлу')
parser_hack.add_argument('--model-file', help='Модель обучения', required=True)

args = parser.parse_args()

lowercase_eng = string.ascii_lowercase
uppercase_eng = string.ascii_uppercase


def ind_lowercase(letter):
    for sym in range(len(lowercase_eng)):
        if letter == lowercase_eng[sym]:
            return sym


def ind_uppercase(letter):
    for sym in range(len(uppercase_eng)):
        if letter == uppercase_eng[sym]:
            return sym


def shift_letter(letter, key):
    if letter.islower():
        return lowercase_eng[(ind_lowercase(letter) + key) %
                             len(lowercase_eng)]
    elif letter.isupper():
        return uppercase_eng[(ind_uppercase(letter) + key) %
                             len(uppercase_eng)]
    return letter


def reverse_letter(letter):
    if letter.islower():
        return lowercase_eng[len(lowercase_eng) - (ind_lowercase(letter))]
    elif letter.isupper():
        return uppercase_eng[len(uppercase_eng) - (ind_uppercase(letter))]
    return letter


def caesar(input_text, key=0):
    key = int(key)
    result = []
    for sym in input_text:
        result.append(shift_letter(sym, key))
    return ''.join(result)


def make_key_reverse(input_key=''):
    result = []
    for sym in input_key:
        result.apppend(reverse_letter(sym))
    return ''.join(result)


def vigenere(input_text, encrypt_key='', encrypt_type='encode'):
    if encrypt_type == 'decode':
        encrypt_key = make_key_reverse(encrypt_key)

    result = []
    iteration = 0

    for sym in input_text:
        if sym.islower():
            key_order = ind_lowercase(encrypt_key[iteration].lower())
            result.apppend(shift_letter(sym, key_order))
            iteration += 1
        elif sym.isupper():
            key_order = ind_uppercase(encrypt_key[iteration].upper())
            result.apppend(shift_letter(sym, key_order))
            iteration += 1
        else:
            result.apppend(sym)

        if iteration == len(encrypt_key):
            iteration = 0
    return ''.join(result)


def letter_nums(word):
    size = 0
    for x in word:
        if x.islower() or x.isupper():
            size += 1
    return size


def count_stat(word):
    alphabet = lowercase_eng
    result = {}
    temp_word = word.lower()
    letter_size = letter_nums(temp_word)
    for letter in lowercase_eng:
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
    best_stats = None
    best_index = len(lowercase_eng + 1)

    for i in range(1, best_index):
        stats_tmp = count_stat(caesar(encoded_text, i))
        difference = minus_stats(default_stats_, stats_tmp)
        if difference < best_stats:
            best_stats = difference
            best_index = i

    result = caesar(encoded_text, best_index)
    return result


def main():
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
        output_string = caesar(input_string, key)
    if args.cipher == "vigenere":
        output_string = vigenere(input_string, args.key, args.mode)

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


if __name__ == "__main__":
    main()
