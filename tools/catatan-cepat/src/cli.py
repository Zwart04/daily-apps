"""Antarmuka baris perintah untuk Catatan Cepat."""
import argparse
import os
import signal
import sys
from typing import List

from .core import NoteManager
from .formatter import format_daftar, format_detail, format_stats
from .store import NoteStore
from .types import FilterOptions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="catatan-cepat",
        description="Catat apapun dari terminal dengan cepat. Simpan ide, tugas, atau catatan harian tanpa perlu buka aplikasi.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python3 -m src catat "Belanja mingguan"
  python3 -m src catat "Ide aplikasi" --isi "Buat pembersih file duplikat" --tag ide
  python3 -m src lihat
  python3 -m src cari "belanja"
  python3 -m src tag kerja
  python3 -m src detail 20260705123456
  python3 -m src hapus 20260705123456
  python3 -m src export catatan.json
  python3 -m src stats
        """,
    )

    sub = parser.add_subparsers(dest="perintah", help="Perintah yang tersedia")

    # catat
    p_catat = sub.add_parser("catat", help="Buat catatan baru")
    p_catat.add_argument("judul", help="Judul atau isi catatan")
    p_catat.add_argument("--isi", "-i", default="", help="Isi catatan (jika tidak diisi, sama dengan judul)")
    p_catat.add_argument("--tag", "-t", default="", help="Tag untuk mengelompokkan catatan")

    # lihat
    p_lihat = sub.add_parser("lihat", aliases=["l"], help="Lihat daftar catatan")
    p_lihat.add_argument("--batas", "-n", type=int, default=20, help="Jumlah catatan yang ditampilkan")
    p_lihat.add_argument("--urut", choices=["terbaru", "terlama"], default="terbaru", help="Urutan catatan")

    # cari
    p_cari = sub.add_parser("cari", aliases=["s"], help="Cari catatan")
    p_cari.add_argument("kata", help="Kata kunci pencarian")
    p_cari.add_argument("--batas", "-n", type=int, default=20, help="Jumlah hasil")
    p_cari.add_argument("--tag", "-t", default="", help="Filter berdasarkan tag")

    # tag
    p_tag = sub.add_parser("tag", help="Lihat catatan berdasarkan tag")
    p_tag.add_argument("tag", help="Nama tag")

    # detail
    p_detail = sub.add_parser("detail", aliases=["d"], help="Lihat detail catatan")
    p_detail.add_argument("id", help="ID catatan")

    # hapus
    p_hapus = sub.add_parser("hapus", aliases=["rm"], help="Hapus catatan")
    p_hapus.add_argument("id", help="ID catatan yang akan dihapus")

    # export
    p_export = sub.add_parser("export", help="Export catatan ke file")
    p_export.add_argument("file", nargs="?", default="catatan.json", help="Nama file output")
    p_export.add_argument("--format", "-f", choices=["json", "markdown"], default="json", help="Format output")
    p_export.add_argument("--tag", "-t", default="", help="Export hanya catatan dengan tag tertentu")
    p_export.add_argument("--cari", default="", help="Export hanya catatan yang mengandung kata kunci")

    # stats
    sub.add_parser("stats", help="Lihat statistik catatan")

    # test
    p_test = sub.add_parser("test", help="Jalankan tes mandiri")

    # Global
    parser.add_argument("--test", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--version", action="version", version="Catatan Cepat v1.0.0")

    return parser


def _self_test() -> None:
    """Jalankan tes mandiri."""
    import tempfile
    import shutil
    import json

    passed = 0
    failed: List[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed
        if ok:
            passed += 1
        else:
            failed.append(f"{name}: {detail}")

    # Buat folder sementara untuk test
    test_dir = tempfile.mkdtemp(prefix="catatan_test_")
    try:
        store = NoteStore(data_dir=test_dir)
        manager = NoteManager(store)

        # Test 1: Tambah catatan
        n1 = manager.catat("Test catatan 1", "Ini isi catatan pertama", tag="test")
        check("tambah catatan 1", n1.judul == "Test catatan 1")
        check("tambah catatan 1 punya id", len(n1.id) > 10)

        # Test 2: Tambah catatan lagi
        n2 = manager.catat("Test catatan 2", "Ini isi catatan kedua", tag="kerja")
        check("tambah catatan 2", n2.judul == "Test catatan 2")
        check("total 2 catatan", store.total_catatan == 2)

        # Test 3: Cari catatan
        hasil = manager.lihat_semua(FilterOptions())
        check("lihat semua", len(hasil) >= 2)

        # Test 4: Cari dengan kata kunci
        hasil = manager.lihat_semua(FilterOptions(kata_kunci="kedua"))
        check("cari kata kunci 'kedua'", len(hasil) == 1)
        check("hasil cari benar", hasil[0].judul == "Test catatan 2")

        # Test 5: Filter tag
        hasil = manager.lihat_semua(FilterOptions(tag="kerja"))
        check("filter tag 'kerja'", len(hasil) == 1)
        check("filter tag benar", hasil[0].tag == "kerja")

        # Test 6: Detail
        detail = manager.lihat_satu(n1.id)
        check("detail catatan", detail.id == n1.id)

        # Test 7: Hapus
        ok = manager.hapus(n2.id)
        check("hapus catatan", ok)
        check("total setelah hapus", store.total_catatan == 1)

        # Test 8: Coba lihat yang sudah dihapus
        try:
            manager.lihat_satu(n2.id)
            check("lihat catatan terhapus seharusnya error", False)
        except ValueError:
            check("lihat catatan terhapus error", True)

        # Test 9: Export JSON
        tmp_json = os.path.join(test_dir, "export.json")
        manager.export_json(tmp_json, FilterOptions())
        with open(tmp_json) as f:
            data = json.load(f)
        check("export JSON valid", isinstance(data, list))
        check("export JSON isi", len(data) == 1)

        # Test 10: Export Markdown
        tmp_md = os.path.join(test_dir, "export.md")
        manager.export_markdown(tmp_md, FilterOptions())
        with open(tmp_md) as f:
            md = f.read()
        check("export Markdown valid", "# Catatan Saya" in md)

        # Test 11: Stats
        stats = manager.stats()
        check("stats punya total", stats["total"] == 1)
        check("stats punya tag", stats["total_tag"] >= 1)

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

    total = passed + len(failed)
    print(f"Catatan Cepat: tes mandiri: {passed}/{total} lulus", file=sys.stderr)
    for f in failed:
        print(f"  GAGAL: {f}", file=sys.stderr)
    sys.exit(1 if failed else 0)


def _handle_catat(args, manager: NoteManager) -> None:
    """Handle perintah catat."""
    note = manager.catat(args.judul, args.isi, args.tag)
    print(f"Catatan tersimpan! ID: {note.id}")


def _handle_lihat(args, manager: NoteManager) -> None:
    """Handle perintah lihat."""
    filter_opts = FilterOptions(batas=args.batas, urut=args.urut)
    notes = manager.lihat_semua(filter_opts)
    print(format_daftar(notes))


def _handle_cari(args, manager: NoteManager) -> None:
    """Handle perintah cari."""
    filter_opts = FilterOptions(
        kata_kunci=args.kata,
        tag=args.tag or None,
        batas=args.batas,
    )
    notes = manager.lihat_semua(filter_opts)
    if not notes:
        print(f"Tidak ada catatan yang cocok dengan '{args.kata}'.")
        return
    print(format_daftar(notes))


def _handle_tag(args, manager: NoteManager) -> None:
    """Handle perintah tag."""
    filter_opts = FilterOptions(tag=args.tag, batas=50)
    notes = manager.lihat_semua(filter_opts)
    if not notes:
        print(f"Tidak ada catatan dengan tag '{args.tag}'.")
        return
    print(f"Catatan dengan tag '{args.tag}':")
    print(format_daftar(notes))


def _handle_detail(args, manager: NoteManager) -> None:
    """Handle perintah detail."""
    try:
        note = manager.lihat_satu(args.id)
        print(format_detail(note))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_hapus(args, manager: NoteManager) -> None:
    """Handle perintah hapus."""
    if manager.hapus(args.id):
        print(f"Catatan {args.id} berhasil dihapus.")
    else:
        print(f"Error: Catatan dengan ID '{args.id}' tidak ditemukan.", file=sys.stderr)
        sys.exit(1)


def _handle_export(args, manager: NoteManager) -> None:
    """Handle perintah export."""
    filter_opts = FilterOptions(
        kata_kunci=args.cari or None,
        tag=args.tag or None,
        batas=999999,
    )

    try:
        if args.format == "json":
            path = manager.export_json(args.file, filter_opts)
        else:
            path = manager.export_markdown(args.file, filter_opts)
        print(f"Catatan berhasil diexport ke: {path}")
    except Exception as e:
        print(f"Error: Gagal export: {e}", file=sys.stderr)
        sys.exit(1)


def _handle_stats(_, manager: NoteManager) -> None:
    """Handle perintah stats."""
    stats = manager.stats()
    print(format_stats(stats))


def main() -> None:
    """Fungsi utama."""
    signal.signal(signal.SIGINT, lambda s, f: (print(file=sys.stderr), sys.exit(130)))

    parser = _build_parser()
    args = parser.parse_args()

    # Test via --test
    if args.test:
        _self_test()
        return

    # Test via subcommand
    if getattr(args, "perintah", None) == "test":
        _self_test()
        return

    store = NoteStore()
    manager = NoteManager(store)

    handlers = {
        "catat": _handle_catat,
        "lihat": _handle_lihat,
        "l": _handle_lihat,
        "cari": _handle_cari,
        "s": _handle_cari,
        "tag": _handle_tag,
        "detail": _handle_detail,
        "d": _handle_detail,
        "hapus": _handle_hapus,
        "rm": _handle_hapus,
        "export": _handle_export,
        "stats": _handle_stats,
    }

    handler = handlers.get(args.perintah) if hasattr(args, "perintah") else None
    if handler:
        handler(args, manager)
    else:
        # Default: tampilkan semua catatan
        filter_opts = FilterOptions(batas=20, urut="terbaru")
        notes = manager.lihat_semua(filter_opts)
        print(format_daftar(notes))


if __name__ == "__main__":
    main()
