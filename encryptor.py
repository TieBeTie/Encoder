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
parser_train.add_argument('--model-file', help='Модель', required=True)
parser_train.add_argument('--text-file', help='Путь')

parser_hack = subparsers.add_parser('hack', help='Взлом by Vladislav Hacker')
parser_hack.set_defaults(mode='hack')
parser_hack.add_argument('--input-file', help='Путь к входному файлу')
parser_hack.add_argument('--output-file', help='Путь к выходному файлу')
parser_hack.add_argument('--model-file', help='Модель обучения', required=True)

args = parser.parse_args()

lowercase_eng = string.ascii_lowercase
uppercase_eng = string.ascii_uppercase


def caesar(input_text, key=0):
    key = lowercase_eng[key % len(lowercase_eng)]
    return vigenere(input_text, key)


def vigenere(input_text, encrypt_key='', encrypt_type='encode'):
    base = 1
    if encrypt_type == 'decode':
        base = -1

    result = []
    iteration = 0
    alphabet = ''
    key_sym = ''

    for sym in input_text:
        if sym.islower():
            alphabet = lowercase_eng
            key_sym = encrypt_key[iteration].lower()

        elif sym.isupper():
            alphabet = uppercase_eng
            key_sym = encrypt_key[iteration].upper()

        if sym in alphabet:
            key_index = alphabet.index(key_sym)
            result_letter = alphabet[(alphabet.index(sym) +
                                      base * key_index) % len(alphabet)]
            iteration += 1
        else:
            result_letter = sym

        if iteration == len(encrypt_key):
            iteration = 0

        result.append(result_letter)

    return ''.join(result)


def letter_nums(word):
    size = 0
    for x in word:
        if x.isalpha():
            size += 1
    return size


def count_stat(word):
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


def minus_stats(stats, shifted_stats, shift_stat):
    total = 0.
    for x in lowercase_eng:
        shifted_x = lowercase_eng[(lowercase_eng.index(x) +
                                   shift_stat) % len(stats)]

        if x in stats and shifted_x in shifted_stats:
            total += abs(stats[x] - shifted_stats[shifted_x])
    return total


def hack_caesar(encoded_text, default_stats):
    first_stats = count_stat(caesar(encoded_text, 0))
    best_stats = minus_stats(default_stats, first_stats, 0)
    min_index = 0

    for i in range(1, len(lowercase_eng)):
        difference = minus_stats(default_stats, first_stats, i)
        if difference < best_stats:
            best_stats = difference
            min_index = i

    result = caesar(encoded_text, -min_index)
    return result


def main():
    global args
    input_string = ''
    output_string = ''

    if args.mode == "train":
        args.input_file = args.text_file

    if args.input_file:
        input_file = open(args.input_file, 'r')
        input_string = input_file.read()
        input_file.close()
    else:
        input_string = sys.stdin.read()

    if args.mode == "train":
        text = input_string
        train(text, args.model_file)
        return

    if args.mode == 'encode' or args.mode == 'decode':
        if args.cipher == "caesar":
            key = int(args.key)

            if args.mode == "decode":
                key = -key
            output_string = caesar(input_string, key, )

        elif args.cipher == "vigenere":
            output_string = vigenere(input_string, args.key, args.mode)

    if args.mode == "hack":
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
