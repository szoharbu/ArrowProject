from __future__ import annotations
import random

class Label(str):
    """
    :param postfix: Optional, A string that will be appended to the end of the unique label
    :return: A unique assembly label
    """
    # generate incremental labels
    _label_index = random.randint(1234, 5678)  # start at a random label

    def __new__(cls, postfix: str = "") -> Label:
        if postfix != "":
            postfix = f"_{postfix}"

        label = f"label_{Label._label_index}{postfix}"
        Label._label_index += 1
        return super().__new__(cls, label)