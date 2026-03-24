import subprocess
import os
import re

formats = [
    "250x600-6px-runda-horn",
    "300x250",
    "320x320",
    "320x480-6px-runda-horn",
    "980x240-6px-runda-horn",
    "980x360-6px-runda-horn",
    "980x480-6px-runda-horn"
]

repo_root = r"c:\Users\marku\source\DNAB\HB\mars"
target_dir = r"c:\Users\marku\source\DNAB\HB\mars\-Leverans-Markus\-Leverans-Markus"

for fmt in formats:
    for banner_num in ["1", "2"]:
        rel_path = f"-Leverans-Markus/-Leverans-Markus/{fmt}/banner{banner_num}/index.html"
        res = subprocess.run(["git", "show", f"642fe47:{rel_path}"], cwd=repo_root, capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            print(f"Failed to read {rel_path} from git")
            continue
        
        html = res.stdout
        scene_blocks = re.split(r'class="[^"]*slide-scene', html)[1:]
        
        folders = ["a", "b", "c"]
        for idx, scene in enumerate(scene_blocks):
            if idx >= len(folders): break
            
            letter = folders[idx]
            current_banner_dir = f"banner{banner_num}{letter}"
            file_to_update = os.path.join(target_dir, fmt, current_banner_dir, "index.html")
            
            if not os.path.exists(file_to_update):
                # print(f"File not found: {file_to_update}")
                continue
            
            # extract fonts from old slide
            h_match = re.search(r'<div[^>]*class="[^"]*headline[^"]*"[^>]*style="([^"]*)"', scene, re.IGNORECASE)
            s_match = re.search(r'<div[^>]*class="[^"]*subtext[^"]*"[^>]*style="([^"]*)"', scene, re.IGNORECASE)
            
            h_style = h_match.group(1) if h_match else None
            s_style = s_match.group(1) if s_match else None
            
            h_font = None; h_line = None
            if h_style:
                m1 = re.search(r'font-size:\s*([^;"]+);?', h_style)
                if m1: h_font = m1.group(1).strip()
                m2 = re.search(r'line-height:\s*([^;"]+);?', h_style)
                if m2: h_line = m2.group(1).strip()
                
            s_font = None; s_line = None
            if s_style:
                m1 = re.search(r'font-size:\s*([^;"]+);?', s_style)
                if m1: s_font = m1.group(1).strip()
                m2 = re.search(r'line-height:\s*([^;"]+);?', s_style)
                if m2: s_line = m2.group(1).strip()

            # Now update the local file
            with open(file_to_update, "r", encoding="utf-8") as f:
                content = f.read()
                
            # replace headline
            if h_font and h_line:
                def headline_repl(m):
                    style = m.group(2)
                    style = re.sub(r'font-size:\s*[^;"]+;?', f'font-size: {h_font};', style)
                    style = re.sub(r'line-height:\s*[^;"]+;?', f'line-height: {h_line};', style)
                    return m.group(1) + style + m.group(3)
                
                content = re.sub(r'(<div[^>]*class="[^"]*headline[^"]*"[^>]*style=")([^"]*)(")', headline_repl, content)

            # replace subtext
            if s_font and s_line:
                def subtext_repl(m):
                    style = m.group(2)
                    style = re.sub(r'font-size:\s*[^;"]+;?', f'font-size: {s_font};', style)
                    style = re.sub(r'line-height:\s*[^;"]+;?', f'line-height: {s_line};', style)
                    return m.group(1) + style + m.group(3)
                
                content = re.sub(r'(<div[^>]*class="[^"]*subtext(?: [^"]*)?"[^>]*style=")([^"]*)(")', subtext_repl, content)

            with open(file_to_update, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"Fixed {fmt}/{current_banner_dir}")
