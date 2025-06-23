
def convert_int_value_to_bytes(init_value, element_size):
    """
    Convert a large integer into a list of bytes, ensuring the block size is respected.
    Returns a list of integers, each representing a byte.
    """
    byte_representation = []

    # Calculate the number of bytes needed to represent the value
    num_bytes = (init_value.bit_length() + 7) // 8

    # Collect bytes into a list (little-endian order)
    for i in range(num_bytes):
        byte_representation.append((init_value >> (i * 8)) & 0xFF)

    # Pad with zeros if the init_value is smaller than the element size
    while len(byte_representation) < element_size:
        byte_representation.append(0)

    return byte_representation


def convert_bytes_to_words(byte_representation):
    """
    Convert a list of bytes (integers) into a list of words (and smaller chunks if needed).
    Returns a list of tuples in the format (value, type) where type is "word" or "byte".
    """
    word_size = 4  # Number of bytes per word
    words = []  # List to hold the result
    num_bytes = len(byte_representation)

    idx = 0
    while idx < num_bytes:
        # If enough bytes are available for a word
        if idx + word_size <= num_bytes:
            # Combine 4 bytes into a word (little-endian order)
            word_value = 0
            for i in range(word_size):
                word_value |= byte_representation[idx + i] << (i * 8)
            words.append((word_value, "word"))
            idx += word_size
        else:
            # Handle remaining bytes
            remaining_bytes = num_bytes - idx
            byte_value = 0
            for i in range(remaining_bytes):
                byte_value |= byte_representation[idx + i] << (i * 8)
            words.append((byte_value, "byte"))
            idx += remaining_bytes

    return words

