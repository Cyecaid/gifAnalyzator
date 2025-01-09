class LZWDecoder:
    def __init__(self, min_code_size, data):
        self.min_code_size = min_code_size
        self.data = data

        self.clear_code = 1 << self.min_code_size
        self.end_code = self.clear_code + 1
        self.code_size = self.min_code_size + 1
        self.next_code = self.end_code + 1
        self.max_code_size = 12

    def decode(self):
        dictionary = {i: [i] for i in range(self.clear_code)}
        bit_buffer, bits_in_buffer = 0, 0
        data_iter = iter(self.data)
        codes = []
        old_code = None

        while True:
            current_code, bit_buffer, bits_in_buffer = self.read_next_code_from_block(
                bit_buffer, bits_in_buffer, self.code_size, data_iter)

            if current_code is None:
                break

            if current_code == self.clear_code:
                dictionary = {i: [i] for i in range(self.clear_code)}
                self.reset_parameters_after_clear_code()
                old_code = None
                continue
            elif current_code == self.end_code:
                break

            entry, dictionary, old_code = self.process_code(current_code, dictionary, old_code, codes)

        return codes

    def reset_parameters_after_clear_code(self):
        self.code_size = self.min_code_size + 1
        self.next_code = self.clear_code + 2

    @staticmethod
    def read_next_code_from_block(bit_buffer, bits_in_buffer, code_size, data_iter):
        while bits_in_buffer < code_size:
            try:
                byte = next(data_iter)
                bit_buffer |= byte << bits_in_buffer
                bits_in_buffer += 8
            except StopIteration:
                break

        if bits_in_buffer < code_size:
            return None, bit_buffer, bits_in_buffer

        current_code = bit_buffer & ((1 << code_size) - 1)
        bit_buffer >>= code_size
        bits_in_buffer -= code_size

        return current_code, bit_buffer, bits_in_buffer

    def process_code(self, current_code, dictionary, old_code, codes):
        if current_code in dictionary:
            entry = dictionary[current_code][:]
        elif old_code is not None:
            entry = dictionary[old_code] + [dictionary[old_code][0]]
        else:
            entry = None

        codes.extend(entry)

        if old_code is not None:
            dictionary[self.next_code] = dictionary[old_code] + [entry[0]]
            self.next_code += 1

            if self.next_code >= (1 << self.code_size) and self.code_size < self.max_code_size:
                self.code_size += 1

        old_code = current_code
        return entry, dictionary, old_code
