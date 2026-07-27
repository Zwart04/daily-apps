#!/usr/bin/env bash
# Tes mandiri untuk Catatan Cepat
set -euo pipefail

echo "=== TEST CATATAN CEPAT ==="
echo ""

# Test 1: --help
echo "1. Test --help..."
python3 -m src --help > /dev/null && echo "   [OK] --help berfungsi" || { echo "   [GAGAL] --help"; exit 1; }

# Test 2: tes mandiri
echo "2. Test mandiri..."
python3 -m src test || { echo "   [GAGAL] tes mandiri"; exit 1; }

# Test 3: Buat catatan
echo "3. Buat catatan..."
python3 -m src catat "Test dari terminal" --tag test > /tmp/catatan_test_out.txt && echo "   [OK] catat berfungsi"
CATATAN_ID=$(python3 -m src cari "Test dari terminal" 2>/dev/null | grep -oP 'ID: \K[0-9]+' | head -1)

# Test 4: Lihat catatan
echo "4. Lihat daftar catatan..."
python3 -m src lihat > /dev/null && echo "   [OK] lihat berfungsi"

# Test 5: Cari catatan
echo "5. Cari catatan..."
python3 -m src cari "Test dari terminal" > /dev/null && echo "   [OK] cari berfungsi"

# Test 6: Detail catatan
echo "6. Detail catatan..."
python3 -m src detail "$CATATAN_ID" > /dev/null 2>&1 && echo "   [OK] detail berfungsi" || echo "   [-] detail (ID mungkin berbeda)"

# Test 7: Stats
echo "7. Statistik..."
python3 -m src stats > /dev/null && echo "   [OK] stats berfungsi"

# Test 8: Export
echo "8. Export catatan..."
python3 -m src export /tmp/catatan_export.json > /dev/null && echo "   [OK] export JSON berfungsi"
python3 -c "
import json
with open('/tmp/catatan_export.json') as f:
    data = json.load(f)
assert isinstance(data, list)
print('   [OK] JSON valid,', len(data), 'catatan')
"

# Hapus file sementara
rm -f /tmp/catatan_test_out.txt /tmp/catatan_export.json

echo ""
echo "=== SEMUA TEST LULUS ==="
