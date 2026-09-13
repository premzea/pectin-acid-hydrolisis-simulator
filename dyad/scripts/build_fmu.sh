#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FMU_DIR="$DIR/export/fmu"
OUT_FMU="$DIR/export/PectinHydrolysisTwin.fmu"

echo "==> Compiling C model into Linux x86_64 shared library..."
gcc -O3 -shared -fPIC \
    -I"$FMU_DIR/sources" \
    "$FMU_DIR/sources/PectinHydrolysisTwin.c" \
    -o "$FMU_DIR/binaries/linux64/PectinHydrolysisTwin.so" \
    -lm

echo "==> Packaging FMU archive..."
python3 - << EOF
import zipfile, os
fmu_dir = "$FMU_DIR"
out_fmu = "$OUT_FMU"
with zipfile.ZipFile(out_fmu, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(fmu_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, fmu_dir)
            zf.write(full_path, rel_path)
print(f"Successfully packaged {out_fmu}")
EOF

echo "==> Validating with FMPy..."
python3 -m fmpy validate "$OUT_FMU"
echo "==> FMU build & validation complete!"
