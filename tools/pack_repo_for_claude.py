from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "_claude_upload"
OUT_DIR.mkdir(exist_ok=True)

MAX_CHARS_PER_PART = 850_000
CODE_FENCE = "`" * 3

INCLUDE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".sql",
}

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "_claude_upload",
    "data",
    "logs",
    "screenshots",
    "debug",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "pack_repo_for_claude.py",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "marketspy_feedback.db",
}

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".mp4",
    ".zip",
    ".rar",
    ".7z",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".exe",
    ".dll",
    ".pyd",
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
}


def should_skip(path: Path) -> bool:
    """
    Menentukan apakah file harus dilewati agar Claude tidak dikasih sampah digital.
    """

    path_parts = set(path.parts)

    if path_parts & EXCLUDE_DIRS:
        return True

    if path.name in EXCLUDE_FILES:
        return True

    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    if path.suffix.lower() not in INCLUDE_EXTENSIONS:
        return True

    return False


def safe_read(path: Path) -> str:
    """
    Membaca file teks dengan aman.
    Kalau UTF-8 gagal, fallback ke latin-1.
    """

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")
    except Exception as exc:
        return f"<<FAILED_TO_READ: {exc}>>"


def get_language_name(path: Path) -> str:
    """
    Menentukan label bahasa untuk markdown code block.
    """

    suffix = path.suffix.lower().replace(".", "")

    language_map = {
        "py": "python",
        "js": "javascript",
        "jsx": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "html": "html",
        "css": "css",
        "scss": "scss",
        "json": "json",
        "md": "markdown",
        "txt": "text",
        "yml": "yaml",
        "yaml": "yaml",
        "toml": "toml",
        "ini": "ini",
        "cfg": "ini",
        "sql": "sql",
    }

    return language_map.get(suffix, "text")


def collect_files() -> list[Path]:
    """
    Mengambil semua file penting dari project.
    """

    files: list[Path] = []

    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and not should_skip(path):
            files.append(path)

    return files


def build_file_tree(files: list[Path]) -> str:
    """
    Membuat daftar struktur file agar Claude paham isi project.
    """

    lines: list[str] = []

    for path in files:
        relative_path = path.relative_to(ROOT).as_posix()
        lines.append(f"- {relative_path}")

    return "\n".join(lines)


def build_header(files: list[Path]) -> str:
    """
    Header konteks project untuk Claude Cloud.
    """

    file_tree = build_file_tree(files)

    return f"""# PASARINTAI AI - REPO CONTEXT FOR CLAUDE

## PROJECT PURPOSE

Project ini adalah aplikasi web scraping marketplace untuk mengambil data produk Tokopedia, melakukan filtering budget, AI crosscheck, feedback benar/salah, dan menampilkan rekomendasi produk seperti termurah, terbaik, dan most trusted.

## IMPORTANT RULES

- Jangan ubah tujuan utama project.
- Jangan hapus fitur feedback benar/salah.
- Jangan hapus progress realtime ETA dan elapsed.
- Jangan upload file rahasia seperti .env, token, cookie, database, dan cache.
- Untuk penulisan PI, ikuti Buku Pedoman Penulisan Ilmiah Prodi Informatika 2025.
- Untuk jurnal, gunakan sumber valid yang diberikan user, jangan membuat sumber palsu.

## FILE TREE

{file_tree}

---

"""


def build_file_block(path: Path) -> str:
    """
    Membuat markdown block untuk satu file.
    """

    relative_path = path.relative_to(ROOT).as_posix()
    language = get_language_name(path)
    content = safe_read(path)

    return (
        f"\n\n# FILE: {relative_path}\n\n"
        f"{CODE_FENCE}{language}\n"
        f"{content}\n"
        f"{CODE_FENCE}\n"
    )


def split_content_into_parts(files: list[Path]) -> list[str]:
    """
    Membagi hasil dump repo jadi beberapa file markdown agar aman diupload ke Claude Cloud.
    """

    parts: list[str] = []
    current_part = build_header(files)

    for path in files:
        block = build_file_block(path)

        if len(current_part) + len(block) > MAX_CHARS_PER_PART:
            parts.append(current_part)
            current_part = ""

        current_part += block

    if current_part.strip():
        parts.append(current_part)

    return parts


def write_parts(parts: list[str]) -> None:
    """
    Menulis hasil dump repo ke folder _claude_upload.
    """

    OUT_DIR.mkdir(exist_ok=True)

    for index, content in enumerate(parts, start=1):
        output_path = OUT_DIR / f"repo_context_part_{index:02d}.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"[OK] wrote {output_path} ({len(content):,} chars)")


def main() -> None:
    """
    Entry point script.
    """

    files = collect_files()

    if not files:
        print("[WARN] Tidak ada file source code yang ditemukan.")
        return

    parts = split_content_into_parts(files)
    write_parts(parts)

    print("")
    print(f"[DONE] Total source files packed: {len(files)}")
    print(f"[DONE] Total upload parts created: {len(parts)}")
    print(f"[DONE] Upload semua file dari folder: {OUT_DIR}")
    print("")
    print("[UPLOAD KE CLAUDE CLOUD]")
    print("1. Upload semua repo_context_part_*.md dari folder _claude_upload")
    print("2. Upload Buku Pedoman Penulisan Ilmiah Prodi Informatika 2025.pdf")
    print("3. Upload SOURCE_REGISTER.md berisi jurnal valid")
    print("")
    print("[WARN] Jangan upload .env, .db, node_modules, .venv, logs, atau file sensitif.")


if __name__ == "__main__":
    main()
