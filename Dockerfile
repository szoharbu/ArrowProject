FROM python:3.12-slim

# Base tooling: RISC-V cross toolchain, QEMU for RISC-V, and build essentials
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        gcc-riscv64-unknown-elf \
        binutils-riscv64-unknown-elf \
        qemu-system-misc \
        qemu-system-riscv64 \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Python deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Smoke-test: generate one RISC-V seed and run QEMU golden simulation
# Uses internal content/templates and writes artifacts under /app/Arrow_output
RUN python run_arrow.py random_template \
    --arch riscv \
    --output /app/Arrow_output \
    --seed 1 \
    --upload_statistics False \
    --debug_mode False \
    --instruction_debug_prints False \
    --memory_debug_prints None \
    --create_binary True \
    --env sim

# Default entrypoint: run Arrow; override CMD/args as needed
ENTRYPOINT ["python", "run_arrow.py"]
CMD ["random_template", "--arch", "riscv", "--output", "/app/Arrow_output", "--upload_statistics", "False", "--debug_mode", "False", "--instruction_debug_prints", "False", "--memory_debug_prints", "None", "--create_binary", "True", "--env", "sim"]
