from pathlib import Path


ROOT = Path(r"c:\Users\marku\source\DNAB\HB\mars\-Leverans-Markus\-Leverans-Markus")
HEADLINE_TRACKING_OLD = "letter-spacing: 0em;"
HEADLINE_TRACKING_NEW = "letter-spacing: 0.01em;"
WIDE_SUBTEXT_OLD = "class=\"subtext copy-x\" style=\"left: 365px; bottom: 21px;"
WIDE_SUBTEXT_NEW = "class=\"subtext copy-x\" style=\"left: 365px; bottom: 22px;"


def process_file(file_path: Path) -> bool:
    content = file_path.read_text(encoding="utf-8")
    updated = content.replace(HEADLINE_TRACKING_OLD, HEADLINE_TRACKING_NEW)

    if "980x360-6px-runda-horn" in file_path.parts:
        updated = updated.replace(WIDE_SUBTEXT_OLD, WIDE_SUBTEXT_NEW)

    if updated == content:
        return False

    file_path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    total = 0
    for file_path in ROOT.glob("**/index.html"):
        total += 1
        if process_file(file_path):
            changed += 1

    print(f"Processed {total} files, updated {changed} files.")


if __name__ == "__main__":
    main()