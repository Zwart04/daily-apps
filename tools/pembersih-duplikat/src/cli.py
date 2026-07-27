"""Command-line interface untuk Pembersih File Duplikat."""
import argparse
import os
import signal
import sys
import tempfile
from typing import List

from .config import load_config
from .core import cari_duplikat, hitung_ruang_terbuang
from .formatter import format_output
from .types import ALLOWED_FORMATS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pembersih-duplikat",
        description="Cari dan bersihkan file duplikat di folder komputer Anda",
        epilog="Contoh: python3 -m src ~/Downloads  |  python3 -m src ~/Downloads --kering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("folder", nargs="?", default=None,
                        help="Folder yang ingin diperiksa (contoh: ~/Downloads)")
    parser.add_argument("--test", action="store_true",
                        help="Jalankan tes mandiri (self-test)")
    parser.add_argument("--json", action="store_true",
                        help="Output dalam format JSON")
    parser.add_argument("--format", choices=ALLOWED_FORMATS, default="text",
                        help="Format output (text/json)")
    parser.add_argument("--kering", action="store_true",
                        help="Mode kering: hanya lihat, jangan hapus (dry-run)")
    parser.add_argument("--hapus", action="store_true",
                        help="Hapus file duplikat (simpan 1 file asli per grup)")
    parser.add_argument("--min-size", type=int, default=1024,
                        help="Ukuran minimal file dalam byte (default: 1024 = 1 KB)")
    parser.add_argument("--version", action="version",
                        version="pembersih-duplikat 1.0.0")
    return parser


def _self_test() -> None:
    """Jalankan self-test untuk verifikasi semua modul berfungsi."""
    passed = 0
    failed: List[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed
        if ok:
            passed += 1
        else:
            failed.append(f"{name}: {detail}")

    # 1. Buat folder temp dengan file duplikat
    with tempfile.TemporaryDirectory() as tmpdir:
        # Buat beberapa file
        file_a = os.path.join(tmpdir, "file_a.txt")
        file_b = os.path.join(tmpdir, "file_b.txt")
        file_c = os.path.join(tmpdir, "file_c.txt")

        with open(file_a, "w") as f:
            f.write("Ini adalah konten file test A" * 100)
        with open(file_b, "w") as f:
            f.write("Ini adalah konten file test B" * 100)  # berbeda
        with open(file_c, "w") as f:
            f.write("Ini adalah konten file test A" * 100)  # sama dengan A

        # 2. Test scan_folder
        from .core import scan_folder
        cfg = load_config()
        files = scan_folder(tmpdir, cfg["exclude_dirs"], 1)
        check("scan_folder: minimal 3 file", len(files) >= 3)

        # 3. Test cari_duplikat
        dups = cari_duplikat(tmpdir, min_size=1)
        check("cari_duplikat: ada duplikat", len(dups) > 0)

        # 4. Test hitung ruang
        ruang = hitung_ruang_terbuang(dups)
        check("hitung_ruang_terbuang: > 0", ruang > 0)

        # 5. Test core module
        from .core import group_by_size, filter_duplicates
        groups = group_by_size(files)
        check("group_by_size: returns dict", isinstance(groups, dict))

        # 6. Test formatter
        from .formatter import format_output
        out = format_output(dups)
        check("format_output: returns str", isinstance(out, str) and len(out) > 0)

        json_out = format_output(dups, fmt="json")
        import json
        parsed = json.loads(json_out)
        check("JSON output bisa di-parse", isinstance(parsed, dict))

        # 7. Test config
        check("load_config returns dict", isinstance(cfg, dict))
        check("config has exclude_dirs", "exclude_dirs" in cfg)

    total = passed + len(failed)
    print(f"pembersih-duplikat: self-test: {passed}/{total} passed")
    for f in failed:
        print(f"  GAGAL: {f}")
    sys.exit(1 if failed else 0)


def _hapus_duplikat(duplicates: dict, kering: bool = False) -> None:
    """Hapus file duplikat, sisakan 1 file asli per grup."""
    total_dihapus = 0
    total_ruang = 0

    for fhash, flist in duplicates.items():
        # File pertama dianggap asli, sisanya duplikat
        for i, fpath in enumerate(flist):
            if i == 0:
                continue  # skip file asli
            try:
                size = os.path.getsize(fpath)
                if kering:
                    print(f"  (KERING) Akan hapus: {fpath} ({size} byte)")
                else:
                    os.remove(fpath)
                    print(f"  Terhapus: {fpath} ({size} byte)")
                total_dihapus += 1
                total_ruang += size
            except (OSError, PermissionError) as e:
                print(f"  GAGAL hapus: {fpath} — {e}", file=sys.stderr)

    if kering:
        print(f"\nMode KERING: {total_dihapus} file akan dihapus, "
              f"{total_ruang} byte akan dibebaskan.")
        print("Jalankan tanpa --kering untuk benar-benar menghapus.")
    else:
        print(f"\nSelesai! {total_dihapus} file duplikat dihapus. "
              f"{total_ruang} byte ruang dibebaskan.")


def main() -> None:
    """Entry point utama."""
    signal.signal(signal.SIGINT, lambda s, f: (print("\nDibatalkan pengguna."), sys.exit(130)))

    parser = _build_parser()
    args = parser.parse_args()

    if args.test:
        _self_test()
        return

    if not args.folder:
        print("Error: Tentukan folder yang ingin diperiksa.")
        print("  python3 -m src ~/Downloads")
        print("  python3 -m src --help  (untuk bantuan)")
        sys.exit(1)

    folder = os.path.abspath(os.path.expanduser(args.folder))

    if not os.path.isdir(folder):
        print(f"Error: Folder tidak ditemukan: {folder}", file=sys.stderr)
        sys.exit(1)

    # Load config
    cfg = load_config()
    fmt = "json" if args.json else args.format

    # Semua info/progress ke stderr supaya tidak campur dengan output JSON
    print(f"Memeriksa folder: {folder}", file=sys.stderr)
    print("Mencari file duplikat...", file=sys.stderr)

    def progress(msg: str) -> None:
        print(f"  {msg}", file=sys.stderr)

    duplicates = cari_duplikat(
        folder,
        exclude_dirs=cfg["exclude_dirs"],
        min_size=args.min_size,
        chunk_size=cfg["chunk_size"],
        progress_callback=progress,
    )

    # Output ke stdout (untuk JSON juga ke stdout — tapi tanpa campur info)
    output = format_output(duplicates, fmt=fmt)
    if fmt == "json":
        # JSON murni ke stdout
        print(output)
    else:
        print(f"\n{output}")

    # Hapus jika diminta
    if args.hapus or args.kering:
        if not duplicates:
            print("Tidak ada duplikat untuk dihapus.", file=sys.stderr)
        else:
            _hapus_duplikat(duplicates, kering=args.kering)
    elif duplicates:
        print("\nGunakan --hapus untuk menghapus file duplikat.", file=sys.stderr)
        print("Gunakan --kering untuk lihat file yang akan dihapus (tanpa hapus).", file=sys.stderr)


if __name__ == "__main__":
    main()
