FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    make \
    g++ \
    clang \
    cmake \
    python3 \
    python3-pip \
    python3-venv \
    verilator \
    iverilog \
    yosys \
    gcc-riscv64-unknown-elf \
    binutils-riscv64-unknown-elf \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-publishers \
    latexmk \
    zip \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    nextpnr-ice40 \
    nextpnr-ecp5 \
    || true

RUN python3 -m pip install --break-system-packages yowasp-yosys

WORKDIR /workspace
COPY . /workspace

CMD ["make", "reproduce", "PYTHON=python3"]
