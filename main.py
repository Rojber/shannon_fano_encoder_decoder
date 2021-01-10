import json
import sys
from collections import OrderedDict
import tree
import time
import bitstring
import os


def decrypt_data(path):
    file = open(path, 'rb+')
    char_counter = os.path.getsize(path)
    
    json_string = ""
    is_loading_json_dic = True
    while is_loading_json_dic:
        char = file.read(1)
        #print(char)
        json_string += char.decode("utf-8")
        char_counter -= 1
        
        if char.decode("utf-8") == "}":
            is_loading_json_dic = False

    # wczytanie binarnych danych
    bin_array = file.read(char_counter)
    file.close()
    
    # convert back to bin and join to one string
    bitstring = ""
    for i in bin_array:
        bitstring += "{:08b}".format(i, "08b")

    codes_dict = json.loads(json_string)
    print(codes_dict)
    
    get_decoded_string(codes_dict, bitstring)


def get_decoded_string(codes_dict, bitstring):
    # odwrócenie słownika
    new_json = {}
    for k, v in codes_dict.items():
        new_json[v] = k

    decoded_string = ""
    substring = ""
    for bit in bitstring:
        substring += bit
        if is_json_key_present(new_json, substring):
            if new_json[substring] == "_EOT":
                break
            elif new_json[substring] == "_NewLine":
                decoded_string += "\n"
            elif new_json[substring] == "_Space":
                decoded_string += " "
            elif new_json[substring] == "_CurlyCloseB":
                decoded_string += "}"
            else:
                decoded_string += new_json[substring]
                
            substring = ""
    
    # zapisywanie rozkodowanego wyniku
    decoded_string_file = input("Decoded file name: ")
    with open(decoded_string_file + ".txt", 'a') as f:
        f.write(decoded_string)


def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False

    return True


def encrypt_data(filename, encoded_filename):
    char_probability = {}
    char_counter = 0
    start = time.time()

    # wczytanie tekstu z pliku
    text = open(filename, encoding="utf-8").read()
    if text == '':
        print('ERROR: SOURCE FILE IS EMPTY')
        return

    # dodanie znaku końca tekstu
    eot_char = b'\xE2\x90\x84'.decode('utf-8')
    text += eot_char

    # tworzenie słownika prawdopodobieństwa wystąpień znaków
    for char in text:
        char_counter += 1
        if char == "\n":
            char = "_NewLine"
        if char == " ":
            char = "_Space"
        if char == "}":
            char = "_CurlyCloseB"
        if char == eot_char:
            char = "_EOT"
        if char in char_probability:
            char_probability[char] += 1
        else:
            char_probability[char] = 1

    char_probability = OrderedDict(sorted(char_probability.items()))

    # obliczanie prawdopodobieństw znaków
    for char in char_probability:
        char_probability[char] = float(char_probability[char]/char_counter)

    # tworzenie drzewa kodowania
    sorted_probability_dict = {k: v for k, v in sorted(char_probability.items(), key=lambda x: x[1], reverse=True)}
    root = tree.Tree("root")
    compute(root, [], sorted_probability_dict)

    # pobranie słownika znaków i ich kodów binarnych
    codes_dict = {}
    codes_dict = root.get_codes_dict(codes_dict, [])
    print(codes_dict)

    # tworzenie stringa wartości binarnych
    bitstr = ''
    for character in text:
        if character == "\n":
            character = "_NewLine"
        if character == " ":
            character = "_Space"
        if character == "}":
            character = "_CurlyCloseB"
        if character == eot_char:
            character = "_EOT"
        bitstr += codes_dict[character]

    # zapis słownika znaków i ich kodów binarnych do pliku oraz samych danych binarnych
    with open(encoded_filename, 'bw') as f:
        f.write(bytes(json.dumps(codes_dict, ensure_ascii=False).encode('utf8')))
        bitstring.BitArray(bin=bitstr).tofile(f)

    end = time.time()
    print("Encoding finished in " + str(end - start) + " seconds.")


def compute(code_tree, path, sorted_probability_dict):
    last_sum = 0.0
    string_sum = 0.0
    substring = {}
    temp_string = sorted_probability_dict.copy()

    if len(sorted_probability_dict) == 1:
        return

    if len(sorted_probability_dict) == 2:
        dict_keys = list(sorted_probability_dict.keys())
        code_tree.add_to_tree(path + [0], dict_keys[0])
        code_tree.add_to_tree(path + [1], dict_keys[1])
        return

    for _, value in sorted_probability_dict.items():
        string_sum += value

    for key, value in sorted_probability_dict.items():
        if last_sum == 0.0:
            last_sum = value
            substring[key] = value
            temp_string.pop(key)
        else:
            actual_sum = last_sum + value
            if ((string_sum/2) - actual_sum < 0 and (string_sum/2) - last_sum >= 0) or ((string_sum/2) - actual_sum <= 0 and (string_sum/2) - last_sum <= 0):
                if abs(actual_sum - (string_sum/2)) >= abs(last_sum - (string_sum/2)):
                    code_tree.add_to_tree(path + [0], ''.join(list(substring.keys())))
                    code_tree.add_to_tree(path + [1], ''.join(list(temp_string.keys())))
                    compute(code_tree, path + [0], substring)
                    compute(code_tree, path + [1], temp_string)
                    return
                else:
                    substring[key] = value
                    temp_string.pop(key)
                    code_tree.add_to_tree(path + [0], ''.join(list(substring.keys())))
                    code_tree.add_to_tree(path + [1], ''.join(list(temp_string.keys())))
                    compute(code_tree, path + [0], substring)
                    compute(code_tree, path + [1], temp_string)
                    return
            else:
                last_sum = actual_sum
                substring[key] = value
                temp_string.pop(key)


if __name__ == '__main__':
    while True:
        print("\nShannon-Fano encryption and decryption utility.")
        inp1 = input("Do you want to encrypt or decrypt file? (e/d): ")
        if inp1 == 'e':
            inp_e1 = input("Relative path to file: ")
            if not os.path.isfile(inp_e1):
                print('ERROR: FILE NOT FOUND\n')
                continue
            inp_e2 = input("Encoded file name: ")
            encrypt_data(inp_e1, inp_e2 + ".pack")
        elif inp1 == 'd':
            inp = input("Relative path to file: ")
            if not os.path.isfile(inp):
                print('ERROR: FILE NOT FOUND\n')
                continue
            decrypt_data(inp)
        else:
            print('ERROR: WRONG COMMAND\n')
            continue
        inp2 = input("\nDo you want to continue with another file? (y/n): ")
        if inp2 == 'n':
            break
