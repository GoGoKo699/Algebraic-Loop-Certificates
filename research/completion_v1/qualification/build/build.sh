#!/bin/sh
set -eu
BASE=/workspace/scratch/9781207fd51b
export PATH="$BASE/ric3-toolchain/bin:$BASE/ric3-build-tools/usr/lib/llvm-18/bin:$BASE/ric3-build-tools/usr/bin:$PATH"
export LD_LIBRARY_PATH="$BASE/ric3-build-tools/usr/lib/x86_64-linux-gnu"
export CARGO_HOME="$BASE/ric3-cargo-cache"
export CARGO_TARGET_DIR="$BASE/ric3-cargo-target"
cd "$BASE/ric3-native-src"
cargo build --release --locked --offline -j 2
