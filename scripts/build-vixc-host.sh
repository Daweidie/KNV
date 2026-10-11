#!/bin/sh
# Build a runnable host vixc from the read-only sibling Vix-lang tree,
# relinked against the system LLVM (verified with LLVM 23).  Every generated
# file stays under KNV/build; Vix-lang is only a compiler input.
#
# Usage:  sh scripts/build-vixc-host.sh
# Env:    OUT=build/vixc-host  CC=clang  CXX=clang++  LLVM_CONFIG=llvm-config
#
# This does not run or modify the upstream seed executable.  The checked-in
# executable needs LLVM 21, while its newer build needs LLVM 22; rebuilding
# the seed IR makes it usable with the installed LLVM 23.

set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VIX_HOME="${VIX_HOME:-$ROOT/../Vix-lang}"
OUT="${OUT:-build/vixc-host}"
OBJDIR="${OBJDIR:-build/host}"
CC="${CC:-clang}"
CXX="${CXX:-clang++}"
LLVM_CONFIG="${LLVM_CONFIG:-llvm-config}"

for f in seed/vixc.ll src/helper.c src/runtime.c lib/api.c \
         lib/llvm/Llc.cpp lib/llvm/Linker.cpp lib/llvm/Passes.cpp; do
    if [ ! -f "$VIX_HOME/$f" ]; then
        echo "build-vixc-host: missing $f" >&2
        echo "build-vixc-host: expected the Vix compiler tree at $VIX_HOME" >&2
        exit 1
    fi
done

mkdir -p "$OBJDIR"

echo "[1/3] compiling $VIX_HOME/seed/vixc.ll -> object"
"$CC" -c "$VIX_HOME/seed/vixc.ll" -o "$OBJDIR/seed.o"

echo "[2/3] compiling support objects"
"$CC"  -c "$VIX_HOME/src/helper.c"      -o "$OBJDIR/helper.o"  $("$LLVM_CONFIG" --cflags)   -Wno-deprecated-declarations
"$CC"  -c "$VIX_HOME/src/runtime.c"     -o "$OBJDIR/runtime.o"
"$CC"  -c "$VIX_HOME/lib/api.c"         -o "$OBJDIR/api.o"
"$CXX" -c "$VIX_HOME/lib/llvm/Llc.cpp"    -o "$OBJDIR/Llc.o"    $("$LLVM_CONFIG" --cxxflags) -Wno-deprecated-declarations
"$CXX" -c "$VIX_HOME/lib/llvm/Linker.cpp" -o "$OBJDIR/Linker.o" $("$LLVM_CONFIG" --cxxflags) -Wno-deprecated-declarations
"$CXX" -c "$VIX_HOME/lib/llvm/Passes.cpp" -o "$OBJDIR/Passes.o" $("$LLVM_CONFIG" --cxxflags) -Wno-deprecated-declarations

echo "[3/3] linking $OUT"
"$CXX" -fuse-ld=lld -o "$OUT" \
    "$OBJDIR/seed.o" "$OBJDIR/helper.o" "$OBJDIR/runtime.o" \
    "$OBJDIR/api.o" "$OBJDIR/Llc.o" "$OBJDIR/Linker.o" "$OBJDIR/Passes.o" \
    $("$LLVM_CONFIG" --ldflags --libs all) -llldELF -llldCommon -lz -lzstd

echo "[ok] built $OUT"
"$OUT" --version || true
