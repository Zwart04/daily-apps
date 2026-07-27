#!/usr/bin/env bash
# Self-test untuk Pembersih File Duplikat
set -euo pipefail

echo "=== Self-Test: Pembersih File Duplikat ==="
echo ""

# Test 1: --help
echo "Test 1: --help"
python3 -m src --help > /dev/null 2>&1 && echo "  PASS" || { echo "  FAIL"; exit 1; }

# Test 2: --test
echo "Test 2: --test"
python3 -m src --test 2>&1
echo ""

# Test 3: Buat folder temp dengan file duplikat
echo "Test 3: Cari duplikat di folder temp"
TMPDIR=$(mktemp -d)
echo "konten sama persis" > "$TMPDIR/file1.txt"
echo "konten sama persis" > "$TMPDIR/file2.txt"
echo "konten beda coy" > "$TMPDIR/file3.txt"
echo "konten sama persis juga" > "$TMPDIR/file4.txt"
# file 1 & 2 duplikat, file 3 berbeda, file 4 beda
python3 -m src "$TMPDIR" --min-size 1 2>&1 > /tmp/test_out.txt
if grep -q "Grup" /tmp/test_out.txt; then
  echo "  PASS: Duplikat ditemukan"
else
  echo "  FAIL: Tidak ada duplikat"
  cat /tmp/test_out.txt
  rm -rf "$TMPDIR"
  exit 1
fi
rm -rf "$TMPDIR"

# Test 4: Mode kering
echo "Test 4: Mode kering"
TMPDIR=$(mktemp -d)
echo "data" > "$TMPDIR/a.txt"
echo "data" > "$TMPDIR/b.txt"
python3 -m src "$TMPDIR" --kering --min-size 1 2>&1 > /tmp/test_kering.txt
if grep -q "KERING" /tmp/test_kering.txt; then
  echo "  PASS: Mode kering bekerja"
else
  echo "  FAIL: Mode kering tidak berfungsi"
  cat /tmp/test_kering.txt
  rm -rf "$TMPDIR"
  exit 1
fi
# File masih harus ada
[ -f "$TMPDIR/a.txt" ] && [ -f "$TMPDIR/b.txt" ] && echo "  PASS: File tidak dihapus" || echo "  FAIL: File terhapus"
rm -rf "$TMPDIR"

# Test 5: JSON output
echo "Test 5: JSON output"
TMPDIR=$(mktemp -d)
echo "test" > "$TMPDIR/x.txt"
echo "test" > "$TMPDIR/y.txt"
python3 -m src "$TMPDIR" --json --min-size 1 2>&1 > /tmp/test_json.txt
python3 -c "import json; d=json.load(open('/tmp/test_json.txt')); assert isinstance(d, dict); print('  PASS: JSON valid')" || { echo "  FAIL: JSON tidak valid"; rm -rf "$TMPDIR"; exit 1; }
rm -rf "$TMPDIR"

echo ""
echo "=== Semua tes selesai ==="
