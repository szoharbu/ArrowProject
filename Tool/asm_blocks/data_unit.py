from typing import Optional

class DataUnit:
    def __init__(
            self,
            byte_size: int,
            memory_segment_id:str,
            memory_block_id:str,
            address: Optional[int] = None,
            name:str=None,
            init_value_byte_representation: list[int]=None,
    ):
        """
        Initializes an DataUnit from shared or preserved blocks. later be published into the date_usage file
        """
        self.name = name
        self.address = address
        self.byte_size = byte_size
        self.memory_block_id = memory_block_id
        self.memory_segment_id = memory_segment_id
        self.init_value_byte_representation = init_value_byte_representation


        if self.init_value_byte_representation is not None:
            formatted_bytes = ", ".join(f"0x{byte:02x}" for sublist in self.init_value_byte_representation for byte in sublist)
        else:
            formatted_bytes = "None"

        self.data_unit_str = f"[name:{self.name}, memory_block:{self.memory_block_id}, memory_segment:{self.memory_segment_id}, "
        if address is not None:
            self.data_unit_str += f"address:{hex(self.address)}, "
        self.data_unit_str += f"byte_size:{self.byte_size}, init_value:{formatted_bytes}]"
        #print(self.data_unit_str)
        #logger = get_logger()
        #logger.debug(f"DataUnit generated: {self.data_unit_str}")

    def __str__(self):
        return self.data_unit_str
