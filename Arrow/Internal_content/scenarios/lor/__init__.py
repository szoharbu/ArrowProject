import random
from pickle import FALSE

from Arrow.Arrow_API import AR
from Arrow.Utils.configuration_management import Configuration
from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager


class LORManager:
    def __init__(self):
        self.lor_memory_regions = []

    def add_new_region(self, region=None, attributes=None):
        """Add a new memory region."""
        if region is not None:
            # Check region correctness ...
            if region.size > 0x1000:
                raise ValueError("Memory region size must exceed 0x4000KB")
            if region.region_id in [r.region_id for r in self.lor_memory_regions]:
                raise ValueError(f"Memory region {region.region_id} already exists")
        else:
            region = MemoryManager.MemorySegment(f"lor_region", byte_size=0x4000, memory_type=Configuration.Memory_types.DATA_SHARED)

        # Setting region as an LOR region, with the various attributes like region_id, descriptor_is, etc.
        AR.asm("mrs x0, ...")
        self.lor_memory_regions.append(region)

    def get_list(self):
        """Return the full list of memory regions."""
        return self.lor_memory_regions

    def get_random_one(self):
        """Return a random memory region."""
        if not self.lor_memory_regions:
            return None
        return random.choice(self.lor_memory_regions)

    def display_regions(self):
        """Print all memory regions."""
        print("Registered LOR Regions:")
        for region in self.lor_memory_regions:
            print(f"  - {region}")


@AR.scenario_decorator(random=False, tags=[Configuration.Tag.LOR])
def lor_access_scenario():
    lor_manager = LORManager()
    if not lor_manager.get_list() or random.randint(0, 100) < 20: # if list is empty, or in 20% of the cases, add a new region
        lor_manager.add_new_region()
    lor_region = lor_manager.get_random_one()

    for _ in range(10):
        offset = random.randint(0, lor_region.size)
        mem = MemoryManager.Memory(memory_block=lor_region, memory_block_offset=offset)
        action = AR.choice(values={"load": 40, "store": 40, "random_instr": 20})
        if action == "load":
            type = AR.choice(values={"ldar": 50, "ldapr": 30, "ldr": 20})
            AR.generate(src=mem, query=(AR.Instruction.mnemonic.contains(type)))
            # query=(AR.Instruction.usl.flow == "LDAR")) or query=(AR.Instruction.usl.steering_class == ???)) or whatever we add to the DB
        elif action == "store":
            type = AR.choice(values={"stllr": 50, "stlpr": 30, "str": 20})
            AR.generate(dest=mem, query=(AR.Instruction.mnemonic.contains(type)))
        else:
            AR.generate(instruction_count=random.randint(2, 5))


@AR.ingredient_decorator(random=False, priority=Configuration.Priority.HIGH, tags=[Configuration.Tag.LOR])
class lor_access_ingredient(AR.Ingredient):
    def __init__(self):
        self.lor_manager = LORManager()

    def init(self):
        if (not self.lor_manager.get_list() or
                random.randint(0,100) < 20):  # if list is empty, or in 20% of the cases, add a new region
            self.lor_manager.add_new_region()
        self.lor_region = self.lor_manager.get_random_one()

    def body(self):
        for _ in range(5):
            offset = random.randint(0, self.lor_region.size)
            mem = MemoryManager.Memory(memory_block=self.lor_region, memory_block_offset=offset)
            action = AR.choice(values={"load": 50, "store": 50})
            if action == "load":
                ld_type = AR.choice(values={"ldar": 50, "ldapr": 30, "ldr": 20})
                AR.generate(src=mem, query=(AR.Instruction.mnemonic.contains(ld_type)))
            elif action == "store":
                st_type = AR.choice(values={"stllr": 50, "stlpr": 30, "str": 20})
                AR.generate(dest=mem, query=(AR.Instruction.mnemonic.contains(st_type)))

            yield

    def final(self):
        pass
