import os
import math
from bitarray import bitarray
import heapq
from collections import defaultdict


def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.read()


def calculate_average_word_length(text):
    words = text.split()
    total_length = sum(len(word) for word in words)
    average_length = total_length / len(words) if len(words) > 0 else 0
    return average_length+1


def analyze_content(content):
    letters = {}
    counter = 0

    for letter in content:
        cardinality = letters.get(letter, 0)
        letters[letter] = cardinality + 1
        counter += 1

    return letters, counter


def to_probability(dictionary, counter):
    for letter in dictionary:
        dictionary[letter] /= counter
    return dictionary


def create(dictionary):
    code_dictionary = {}
    unique_characters = len(dictionary.keys())
    length = math.ceil(math.log(unique_characters + 1, 2))

    for index, key in enumerate(dictionary.keys()):
        base = int_to_bits(length, index)
        code_dictionary[key] = base
    return code_dictionary, length


def calculate_efficiency(code_dict, frequency_table, average_length):
    entropy = 0
    total_frequency = sum(frequency_table.values())

    for char, frequency in frequency_table.items():
        probability = frequency / total_frequency
        entropy -= probability * math.log2(probability)

    efficiency = entropy / average_length

    return 100 * efficiency


def int_to_bits(length, value):
    bits_array = [1 if digit == '1' else 0 for digit in bin(value)[2:]]
    bits = bitarray(length - len(bits_array))
    bits.setall(0)
    for bit in bits_array:
        bits.append(bit)
    return bits


def encode(code_dict, text):
    encoded = bitarray()

    for letter in text:
        encoded += code_dict[letter]

    return encoded


def decode(encoded_bits, code_dict, length):
    decoded = ''
    total_length = len(encoded_bits)

    index = 0
    while index < total_length and index < len(encoded_bits):
        code = ''
        for i in range(length):
            code += str(encoded_bits[index])
            index += 1
            if index >= total_length:
                break
        decoded += code_dict.get(code, '')

    return decoded


def save(code_dict, encoded_content, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(directory + 'encoded_result', 'wb') as content_file:
        content_file.write(encoded_content.tobytes())

    with open(directory + 'key', 'w') as key_file:
        for key in code_dict.keys():
            key_file.write(key)


def load(directory):
    encoded_content = bitarray()

    with open(directory + 'encoded_result', 'rb') as content_file:
        encoded_content.fromfile(content_file)

    with open(directory + 'key', 'r') as key_file:
        content = key_file.read()
        code_length = math.ceil(math.log(len(content) + 1, 2))
        code_dictionary = {}
        for index, key in enumerate(content):
            base = int_to_bits(code_length, index)
            code_dictionary[base.to01()] = key

    return encoded_content, code_length, code_dictionary


def calculate_sizes(directory, original):
    encoded_size = os.stat(directory + 'encoded_result').st_size
    key_size = os.stat(directory + 'key').st_size
    original_size = os.stat(original).st_size
    return encoded_size, key_size, original_size


class HuffmanNode:
    def __init__(self, character=None, frequency=0):
        self.character = character
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


def build_frequency_table(data):
    frequency_table = defaultdict(int)
    for char in data:
        frequency_table[char] += 1
    return frequency_table


def build_huffman_tree(frequency_table):
    priority_queue = []
    for char, frequency in frequency_table.items():
        node = HuffmanNode(char, frequency)
        heapq.heappush(priority_queue, node)

    while len(priority_queue) > 1:
        left_child = heapq.heappop(priority_queue)
        right_child = heapq.heappop(priority_queue)

        parent_frequency = left_child.frequency + right_child.frequency
        parent = HuffmanNode(frequency=parent_frequency)
        parent.left = left_child
        parent.right = right_child

        heapq.heappush(priority_queue, parent)

    return priority_queue[0]


def build_code_table(huffman_tree):
    code_table = {}

    def traverse(node, current_code):
        if node.character:
            code_table[node.character] = current_code
        else:
            traverse(node.left, current_code + '0')
            traverse(node.right, current_code + '1')

    traverse(huffman_tree, '')
    return code_table


def huffman_encode(data):
    frequency_table = build_frequency_table(data)
    huffman_tree = build_huffman_tree(frequency_table)
    code_table = build_code_table(huffman_tree)

    encoded_data = encode(code_table, data)
    return encoded_data, huffman_tree


def huffman_decode(encoded_data, huffman_tree, code_table, length):
    decoded_data = decode(encoded_data, code_table, length)
    return decoded_data

def main():
    directory_name = 'encoded/'
    file_name = 'norm_romeo.txt'
    content = read_file(file_name=file_name)
    letters_dictionary, counter = analyze_content(content)
    code_dict, code_length = create(letters_dictionary)
    encoded_data, huffman_tree = huffman_encode(content)
    save(code_dict, encoded_data, directory_name)
    encoded_content, loaded_code_length, loaded_code_dictionary = load(directory_name)
    decoded_data = huffman_decode(encoded_content, huffman_tree, loaded_code_dictionary, loaded_code_length)
    en_size, k_size, o_size = calculate_sizes(directory_name, file_name)
    frequency_table = build_frequency_table(content)
    average_length = calculate_average_word_length(content)
    efficiency = calculate_efficiency(code_dict, frequency_table, average_length)

    sum_size = k_size + en_size
    print('Original file => ' + file_name)
    print('Size          => ' + str(o_size) + ' [bytes]')

    print('Encoded size:')
    print('\tEncoded       => ' + str(en_size) + ' [bytes]')
    print('\tKey           => ' + str(k_size) + ' [bytes]')
    print('\tSUM           => ' + str(sum_size) + ' [bytes]')
    print('\tEfficiency    => ' + str(efficiency) + '%')
    print('\tavg word      => ' + str(average_length))
    print('\tCompression Ratio => ' + str(o_size / sum_size))
    print('\tSpace savings     => ' + str(1 - sum_size / o_size))



if __name__ == '__main__':
    main()
