from pathlib import Path

ROOT = Path(".").resolve()
OUT = ROOT / "_claude_audit.md"

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

MAX_FILE_CHARS = 120_000


def should_skip(path: Path) -> bool:
    parts = set(path.parts)

    if parts & EXCLUDE_DIRS:
        return True

    if path.name in EXCLUDE_FILES:
        return True

    if path.suffix.lower() not in INCLUDE_EXT:
        return True

    return False


def language_for(path: Path) -> str:
    ext = path.suffix.lower()

    return {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".json": "json",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".txt": "text",
    }.get(ext, "text")


def main():
    files = []

    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and not should_skip(path):
            files.append(path)

    with OUT.open("w", encoding="utf-8", errors="ignore") as out:
        out.write("# PROJECT CODE AUDIT PACK\n\n")
        out.write(f"Root: `{ROOT}`\n\n")

        out.write("## FILE TREE\n\n")
        for file in files:
            rel = file.relative_to(ROOT)
            out.write(f"- `{rel}`\n")

        out.write("\n---\n\n")

        for file in files:
            rel = file.relative_to(ROOT)

            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                out.write(f"\n## FILE: `{rel}`\n\n")
                out.write(f"Failed to read file: {e}\n")
                continue

            if len(text) > MAX_FILE_CHARS:
                text = text[:MAX_FILE_CHARS]
                text += "\n\n/* FILE TRUNCATED BECAUSE TOO LARGE */\n"

            lang = language_for(file)

            out.write(f"\n## FILE: `{rel}`\n\n")
            out.write(f"```{lang}\n")
            out.write(text)
            out.write("\n```\n")

    print(f"[OK] Created: {OUT}")
    print(f"[OK] Files packed: {len(files)}")


if __name__ == "__main__":
    main()