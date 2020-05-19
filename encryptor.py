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


def ind_lowercase(letter):
    return lowercase_eng.find(letter)


def ind_uppercase(letter):
    return uppercase_eng.find(letter)


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


def step(result, sym, ind, iteration):
    result.append(shift_letter(sym, ind))
    iteration += 1


def vigenere(input_text, encrypt_key='', encrypt_type='encode'):
    if encrypt_type == 'decode':
        encrypt_key = make_key_reverse(encrypt_key)

    result = []
    iteration = 0

    for sym in input_text:
        if sym.islower():
            key_order = ind_lowercase(encrypt_key[iteration].lower())
            step(result, sym, key_order, iteration)

        elif sym.isupper():
            key_order = ind_uppercase(encrypt_key[iteration].upper())
            step(result, sym, key_order, iteration)

        else:
            result.apppend(sym)

        if iteration == len(encrypt_key):
            iteration = 0

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
    for x in stats:
        total += abs(stats[x] - shifted_stats[lowercase_eng[
            (ind_lowercase(x) + shift_stat) % len(stats)]])
    return total


def hack_caesar(encoded_text, default_stats):
    first_stats = count_stat(caesar(encoded_text, 1))
    best_stats = minus_stats(default_stats, first_stats, 0)
    num_of_iters = len(lowercase_eng) + 1
    min_index = 1

    for i in range(1, num_of_iters):
        difference = minus_stats(default_stats, first_stats, i)
        if difference < best_stats:
            best_stats = difference
            min_index = i

    result = caesar(encoded_text, min_index)
    return result


def main():
    global args
    input_string = ''
    output_string = ''

    if args.mode == 'encode' or args.mode == 'decode' or args.mode == 'hack':
        if args.input_file:
            input_file = open(args.input_file, 'r')
            input_string = input_file.read()
            input_file.close()
        else:
            input_string = sys.stdin.read()

    if args.mode == 'encode' or args.mode == 'decode':
        if args.cipher == "caesar":
            key = int(args.key)

            if args.mode == "decode":
                key = -key
            output_string = caesar(input_string, key)

        elif args.cipher == "vigenere":
            output_string = vigenere(input_string, args.key, args.mode)

    if args.mode == "hack":
        json_file = open(args.model_file, 'r')
        default_stats = json.load(json_file)
        json_file.close()
        output_string = hack_caesar(input_string, default_stats)

    if args.mode == 'encode' or args.mode == 'decode' or args.mode == 'hack':
        if args.output_file:
            output_file = open(args.output_file, 'w')
            output_file.write(output_string)
            output_file.close()
        else:
            print(output_string)
        return

    if args.mode == "train":
        if args.text_file:
            text_file = open(args.text_file, 'r')
            text = text_file.read()
            text_file.close()
        else:
            text = sys.stdin.read()
        train(text, args.model_file)


if __name__ == "__main__":
    main()
