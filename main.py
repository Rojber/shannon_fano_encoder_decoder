import json
from collections import OrderedDict
import tree
import time


def encrypt_data(filename, encoded_filename):
    char_probability = {}
    char_counter = 0
    start = time.time()

    text = open(filename, encoding="utf-8").read()

    for char in text:
        char_counter += 1
        if char == "\n":
            char = "_NewLine"
        if char == " ":
            char = "_Space"
        if char in char_probability:
            char_probability[char] += 1
        else:
            char_probability[char] = 1

    char_probability = OrderedDict(sorted(char_probability.items()))

    for char in char_probability:
        char_probability[char] = float(char_probability[char]/char_counter)
        # print(char + " = " + str(char_probability[char]))

    sorted_probability_dict = {k: v for k, v in sorted(char_probability.items(), key=lambda x: x[1], reverse=True)}
    # print(sorted_probability_dict)
    root = tree.Tree("root")
    compute(root, [], sorted_probability_dict)
    # root.print_tree()

    codes_dict = {}
    codes_dict = root.get_codes_dict(codes_dict, [])
    print(codes_dict)

    bitstring = ''
    for character in text:
        if character == "\n":
            character = "_NewLine"
        if character == " ":
            character = "_Space"
        bitstring += codes_dict[character]

    with open(encoded_filename, 'bw') as f:
        f.write(bytes(json.dumps(codes_dict, ensure_ascii=False).encode('utf8')))
        f.write((0).to_bytes(8, 'big'))
        f.write(bytes(int(bitstring[i : i + 8], 2) for i in range(0, len(bitstring), 8)))

    end = time.time()
    print("Encoding finished in " + str(end - start) + " seconds.")


def compute(code_tree, path, sorted_probability_dict):
    # print()
    # print(sorted_probability_dict)
    # print(path)
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
            # print()
            # print("String sum: " + str(string_sum/2))
            # print("Actual sum:" + str(actual_sum))
            # print("Last sum: " + str(last_sum))
            # print()
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
        print("Shannon-Fano encryption and decryption utility.")
        # print("Do you want encrypt or decrypt file? (e/d)")
        inp1 = input("Do you want encrypt or decrypt file? (e/d): ")
        if inp1 == 'e':
            inp_e1 = input("Relative path to file: ")
            inp_e2 = input("Encoded file name: ")
            encrypt_data(inp_e1, inp_e2 + ".pack")
        elif inp1 == 'd':
            # TUTAJ DODAJ WYWOŁANIE FUNKCJI OD DEKODOWANIA
            pass
        else:
            print('WRONG COMMAND\n')
            continue
        inp2 = input("\nDo you want to continue with another file? (y/n): ")
        if inp2 == 'n':
            break
