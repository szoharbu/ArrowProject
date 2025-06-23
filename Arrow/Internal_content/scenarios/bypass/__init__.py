import random

from Arrow.Internal_content.ingredients.feature_a import ing_A
from Arrow.Tool.register_management.register_manager import RegisterManager
from Arrow.Utils.configuration_management import Configuration
from Arrow.Arrow_API import AR
from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow.Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.DISPATCH])
def bypass_bursts():
    num_burst = random.randint(8,15)
    for _ in range(num_burst):
        strategy = random.choice(["long_chain", "short_gap", "load_use", "reuse_noise", "fan_out", "mixed"])

        if strategy == "long_chain":
            generate_dependency_pattern(chain_length=random.randint(5, 10))

        elif strategy == "short_gap":
            generate_dependency_pattern(chain_length=2, gap=random.randint(0, 1))

        elif strategy == "load_use":
            generate_dependency_pattern(chain_length=2, use_load=True, gap=random.randint(0, 1))

        elif strategy == "reuse_noise":
            generate_dependency_pattern(chain_length=4, register_reuse_prob=0.5, include_noise=True)

        elif strategy == "fan_out":
            generate_dependency_pattern(chain_length=1, fan_out=random.randint(2, 4))

        elif strategy == "mixed":
            generate_dependency_pattern(
                chain_length=random.randint(3, 6),
                gap=random.randint(0, 2),
                use_load=random.choice([True, False]),
                register_reuse_prob=random.uniform(0.0, 0.5),
                include_noise=True,
                fan_out=random.randint(1, 3)
            )


def generate_dependency_pattern(
    chain_length: int = 0,
    gap: int = 0,
    use_load: bool = False,
    register_reuse_prob: float = 0.0,
    include_noise: bool = False,
    fan_out: int = 1
) -> list:
    """
    Generate a sequence of instructions with controlled dependencies and hazards.
    """
    base_reg = RegisterManager.get_and_reserve(reg_type="gpr")
    current_reg = base_reg

    use_load = False # WA as Memory is not fully supported yet TODO:: need to fix it!!
    if use_load:
        mem = MemoryManager.Memory(shared=False)
        AR.generate(dest=current_reg, src=mem , comment="generate_dependency_pattern: load from memory")

    for i in range(chain_length):
        next_reg = RegisterManager.get(reg_type="gpr")

        AR.generate(dest=next_reg, src=current_reg, comment=f"generate_dependency_pattern: chain link {i}")

        if gap > 0 and include_noise:
            for _ in range(gap):
                AR.generate(instruction_count=random.randint(1,2), comment="generate_dependency_pattern: random gap")

        for _ in range(fan_out - 1):
            AR.generate(query=(AR.Instruction.mnemonic.contains("mul")), src=next_reg)

        current_reg = next_reg

        if random.random() < register_reuse_prob:
            current_reg = base_reg

    RegisterManager.free(base_reg)
