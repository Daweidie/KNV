#!/bin/sh
# Build the transitional, Vix-written Kix compiler with the read-only
# ../Vix-lang compiler input prepared by build-vixc-host.sh.
# The current stage exposes Kix lexing, syntax checking, and text/JSON ASTs.

set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

HOST="${HOST:-build/vixc-host}"
OUT="${OUT:-build/kixc-stage0}"
OBJ="${OBJ:-build/kixc-stage0.o}"
CXX="${CXX:-clang++}"
LLVM_CONFIG="${LLVM_CONFIG:-llvm-config}"

if [ ! -x "$HOST" ]; then
    sh scripts/build-vixc-host.sh
fi

echo "[1/2] compiling src/main.vix with the host seed"
"$HOST" src/main.vix -obj -o "$OBJ"

echo "[2/2] linking $OUT"
"$CXX" -fuse-ld=lld -o "$OUT" \
    "$OBJ" build/host/helper.o build/host/runtime.o \
    build/host/api.o build/host/Llc.o build/host/Linker.o build/host/Passes.o \
    $("$LLVM_CONFIG" --ldflags --libs all) -llldELF -llldCommon -lz -lzstd

echo "[ok] built $OUT"
