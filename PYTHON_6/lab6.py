import pickle
import os
import math
from bitarray import bitarray
import heapq
from collections import defaultdict

def read_file(file_name):
    with open(file_name, 'rb') as file:
        return file.read()

def compress_lzw(input_file, output_file, size):
    # Odczytaj dane z pliku wejściowego w trybie binarnym
    with open(input_file, 'rb') as file:
        input_data = file.read()

    # Dekoduj dane wejściowe z użyciem kodowania 'latin-1'
    input_data = input_data.decode('latin-1')

    # Reszta kodu pozostaje bez zmian...

    # Inicjalizuj słownik
    dictionary = {}
    next_code = 0
    compressed_data = []

    # Funkcja pomocnicza do dodawania wpisów do słownika
    def add_to_dictionary(sequence):
        nonlocal next_code
        dictionary[sequence] = next_code
        next_code += 1

    # Inicjalizuj słownik jednoznakowymi symbolami
    for char in range(256):
        add_to_dictionary(chr(char))

    # Kompresuj dane wejściowe
    current_sequence = ''
    for char in input_data:
        sequence = current_sequence + char
        if sequence in dictionary:
            current_sequence = sequence
        else:
            compressed_data.append(dictionary[current_sequence])
            if next_code < size:
                add_to_dictionary(sequence)
            current_sequence = char

    # Dodaj ostatnią sekwencję do skompresowanych danych
    if current_sequence in dictionary:
        compressed_data.append(dictionary[current_sequence])

    # Oblicz liczbę bajtów potrzebną do zapisania kodów
    num_bytes = max(1, (next_code - 1).bit_length() // 8 + 1)

    # Zapisz skompresowane dane do pliku wyjściowego
    with open(output_file, 'wb') as file:
        for code in compressed_data:
            file.write(code.to_bytes(num_bytes, 'big'))

def decompress_lzw(input_file, output_file):
    # Odczytaj skompresowane dane z pliku wejściowego
    with open(input_file, 'rb') as file:
        compressed_data = file.read()

    # Inicjalizuj słownik
    dictionary = {}
    next_code = 0
    output_data = []

    # Funkcja pomocnicza do dodawania wpisów do słownika
    def add_to_dictionary(sequence):
        nonlocal next_code
        dictionary[next_code] = sequence
        next_code += 1

    # Inicjalizuj słownik jednoznakowymi symbolami
    for char in range(256):
        add_to_dictionary(chr(char))

    # Dekompresuj dane wejściowe
    current_code = compressed_data[0]
    output_data.append(dictionary[current_code])
    for code in compressed_data[1:]:
        if code in dictionary:
            entry = dictionary[code]
        else:
            entry = dictionary[current_code] + dictionary[current_code][0]
        output_data.append(entry)
        dictionary[next_code] = dictionary[current_code] + entry[0]
        next_code += 1
        current_code = code

    # Zapisz zdekompresowane dane do pliku wyjściowego z użyciem kodowania 'utf-8'
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(''.join(output_data))

def get_file_size(file_path):
    return calculate_file_size_in_mb(os.path.getsize(file_path))

def calculate_file_size_in_mb(file_size_in_bytes):
    file_size_in_mb = file_size_in_bytes / (1024 * 1024)
    return file_size_in_mb

def main():
    print("-------------------------------------------------------------------------------------------------------------------------")
    work_file = 'norm_wiki_sample.txt'
    print('\tOriginal file                                  => ' + work_file)

    work_file_size = get_file_size(work_file)
    print('\tSize of work file                              => ' + str(work_file_size) + ' MB')

    compress_lzw(work_file, 'norm_wiki_sample_compressed_lzw.txt', size=2**12)
    norm_wiki_sample_compressed_lzw = get_file_size('norm_wiki_sample_compressed_lzw.txt')
    print('\tSize of file with dictionary size = 2^12       => ' + str(norm_wiki_sample_compressed_lzw) + ' MB')

    compress_lzw(work_file, 'norm_wiki_sample_compressed2_lzw.txt', size=2**18)
    norm_wiki_sample_compressed2_lzw = get_file_size('norm_wiki_sample_compressed2_lzw.txt')
    print('\tSize of file with dictionary size = 2^18       => ' + str(norm_wiki_sample_compressed2_lzw) + ' MB')

    decompress_lzw('norm_wiki_sample_compressed_lzw.txt', 'norm_wiki_sample_decompress_lzw.txt')
    norm_wiki_sample_decompress_lzw = get_file_size('norm_wiki_sample_decompress_lzw.txt')
    print('\tSize of decoded file with dictionary size 2^12 => ' + str(norm_wiki_sample_decompress_lzw) + ' MB')

    print("-------------------------------------------------------------------------------------------------------------------------")

    work_file = 'wiki_sample.txt'
    print('\tOriginal file                                  => ' + work_file)

    work_file_size = get_file_size(work_file)
    print('\tSize of work file                              => ' + str(work_file_size) + ' MB')

    compress_lzw(work_file, 'wiki_sample_compressed_lzw.txt', size=2**12)
    wiki_sample_compressed_lzw = get_file_size('wiki_sample_compressed_lzw.txt')
    print('\tSize of file with dictionary size = 2^12       => ' + str(wiki_sample_compressed_lzw) + ' MB')

    compress_lzw(work_file, 'wiki_sample_compressed2_lzw.txt', size=2**18)
    wiki_sample_compressed2_lzw = get_file_size('wiki_sample_compressed2_lzw.txt')
    print('\tSize of file with dictionary size = 2^18       => ' + str(wiki_sample_compressed2_lzw) + ' MB')

    decompress_lzw('wiki_sample_compressed_lzw.txt', 'wiki_sample_decompress_lzw.txt')
    wiki_sample_decompress_lzw = get_file_size('wiki_sample_decompress_lzw.txt')
    print('\tSize of decoded file with dictionary size 2^12 => ' + str(wiki_sample_decompress_lzw) + ' MB')

    print("-------------------------------------------------------------------------------------------------------------------------")

    work_file = 'lena.bmp'
    print('\tOriginal file                                  => ' + work_file)

    work_file_size = get_file_size(work_file)
    print('\tSize of work file                              => ' + str(work_file_size) + ' MB')

    compress_lzw(work_file, 'lena_compressed_lzw.bmp', size=2**12)
    lena_compressed_lzw = get_file_size('lena_compressed_lzw.bmp')
    print('\tSize of file with dictionary size = 2^12       => ' + str(lena_compressed_lzw) + ' MB')

    compress_lzw(work_file, 'lena_compressed2_lzw.bmp', size=2**18)
    lena_compressed2_lzw = get_file_size('lena_compressed2_lzw.bmp')
    print('\tSize of file with dictionary size = 2^18       => ' + str(lena_compressed2_lzw) + ' MB')

    decompress_lzw('lena_compressed_lzw.bmp', 'lena_decompress_lzw.bmp')
    lena_decompress_lzw = get_file_size('lena_decompress_lzw.bmp')
    print('\tSize of decoded file with dictionary size 2^12 => ' + str(lena_decompress_lzw) + ' MB')

if __name__ == '__main__':
    main()