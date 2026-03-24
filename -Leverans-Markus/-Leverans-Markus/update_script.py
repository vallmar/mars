import os
import re

target_dir = r"c:\Users\marku\source\DNAB\HB\mars\-Leverans-Markus\-Leverans-Markus"
file_paths = []

for root, dirs, files in os.walk(target_dir):
    for f in files:
        if f == "index.html":
            file_paths.append(os.path.join(root, f))

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. JS Delays
    content = re.sub(r'var\s+Y_DELAY\s*=\s*\d+;', 'var Y_DELAY = 0;', content)
    content = re.sub(r'var\s+X_DELAY\s*=\s*\d+;', 'var X_DELAY = 800;', content)
    content = re.sub(r'var\s+LINE_STAGGER\s*=\s*\d+;', 'var LINE_STAGGER = 0;', content)
    content = re.sub(r'var\s+SUBCOPY_DELAY\s*=\s*\d+;', 'var SUBCOPY_DELAY = 0;', content)

    # 2. Easing
    # replace any cubic-bezier with the new one for transitions
    content = re.sub(
        r'cubic-bezier\([^\)]+\)',
        'cubic-bezier(0.7, 0, 0.2, 1)',
        content
    )

    # 3. Distances for X
    # looking for translate(Xpx, 0px); where X might be > 30
    def repl_x(match):
        val = int(match.group(1))
        if val > 30:
            val = 30
        return f"transform: translate({val}px, 0px)"
    content = re.sub(r'transform:\s*translate\((\d+)px,\s*0px\)', repl_x, content)
    
    # 4. Handle duration
    content = re.sub(r'transition:\s*transform\s+\d+ms', 'transition: transform 1000ms', content)

    # If container overflow hidden isn't there, maybe add it? It's already in .banner
    # the prompt says "Prefer using: overflow: hidden on container". We can just rely on the existing .banner class having it.

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

changed = 0
for fp in file_paths:
    if process_file(fp):
        changed += 1

print(f"Processed {len(file_paths)} files, updated {changed} files.")
