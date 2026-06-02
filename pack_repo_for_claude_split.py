from pathlib import Path

ROOT = Path(".").resolve()
OUT_DIR = ROOT / "_claude_upload"
OUT_DIR.mkdir(exist_ok=True)

MAX_CHARS_PER_PART = 700_000

INCLUDE_EXT = {
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
    "logs",
    "screenshots",
    "debug",
    "_claude_upload",
    "data",
}

EXCLUDE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "marketspy_feedback.db",
}


def should_skip(path: Path) -> bool:
    if set(path.parts) & EXCLUDE_DIRS:
        return True

    if path.name in EXCLUDE_FILES:
        return True

    if path.suffix.lower() not in INCLUDE_EXT:
        return True

    return False


def lang(path: Path) -> str:
    return {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
    }.get(path.suffix.lower(), "text")


def write_part(part_index: int, content: str):
    path = OUT_DIR / f"claude_audit_part_{part_index:02d}.md"
    path.write_text(content, encoding="utf-8", errors="ignore")
    print(f"[OK] Wrote {path}")


def main():
    files = [
        p for p in sorted(ROOT.rglob("*"))
        if p.is_file() and not should_skip(p)
    ]

    file_tree = "# PROJECT FILE TREE\n\n"
    for file in files:
        file_tree += f"- `{file.relative_to(ROOT)}`\n"

    part_index = 1
    current = file_tree + "\n---\n\n"

    for file in files:
        rel = file.relative_to(ROOT)

        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            text = f"FAILED TO READ FILE: {e}"

        block = f"\n## FILE: `{rel}`\n\n```{lang(file)}\n{text}\n```\n"

        if len(current) + len(block) > MAX_CHARS_PER_PART:
            write_part(part_index, current)
            part_index += 1
            current = "# CONTINUED PROJECT CODE AUDIT PACK\n\n"

        current += block

    if current.strip():
        write_part(part_index, current)

    print("[DONE] Upload all files inside _claude_upload to Claude.")


if __name__ == "__main__":
    main()