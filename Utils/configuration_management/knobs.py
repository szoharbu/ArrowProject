import random
from Utils.configuration_management.enums import Tag
from Utils.configuration_management.knob_manager import Knob


class Knobs:
    class Config:
        core_count = Knob(name='core_count', value_func=1, read_only=True, dynamic=False, global_knob=False)
        processor_mode = Knob(name='processor_mode', value_func=lambda: random.choice(["comp32","64bit"]), read_only=True, dynamic=False, global_knob=False)
        privilege_level = Knob(name='privilege_level', value_func=lambda: random.randint(0,3), read_only=True, dynamic=False, global_knob=False)
        skip_boot = Knob(name='skip_boot', value_func=False, read_only=True, dynamic=False, global_knob=False)
    class Template:
        scenario_count = Knob(name='scenario_count', value_func=lambda: random.randint(3,6), read_only=True, dynamic=False, global_knob=False)
        scenario_query = Knob(name='scenario_query', value_func={Tag.REST:100}, read_only=True, dynamic=True, global_knob=False)
    class Memory:
        code_block_count = Knob(name='code_block_count', value_func=lambda: random.randint(4,8), read_only=True, dynamic=False, global_knob=False)
        data_block_count = Knob(name='data_block_count', value_func=lambda: random.randint(5,8), read_only=True, dynamic=False, global_knob=False)
        shared_memory_reuse = Knob(name='shared_memory_reuse', value_func=lambda: random.randint(45, 60), read_only=True, dynamic=False, global_knob=False, description="Probability to reuse shared memory, 100 mean always, default is around 50 ")

