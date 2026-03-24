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

import json

for fmt in formats:
    for banner_num in ["1", "2"]:
        rel_path = f"-Leverans-Markus/-Leverans-Markus/{fmt}/banner{banner_num}/index.html"
        res = subprocess.run(["git", "show", f"642fe47:{rel_path}"], cwd=repo_root, capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            print(f"Failed to read {rel_path}")
            continue
        
        html = res.stdout
        # print headlines and subtexts
        # find all <div class="headline" ...>
        headlines = re.findall(r'<div[^>]*class="[^"]*headline[^"]*"[^>]*style="([^"]*)"', html, re.IGNORECASE)
        subtexts = re.findall(r'<div[^>]*class="[^"]*subtext[^"]*"[^>]*style="([^"]*)"', html, re.IGNORECASE)
        
        # also we need to understand which slide is which. 
        # let's just find the sequence in order.
        # we can just find all font-size values for .headline and .subtext
        
        # Better: extract the full style attribute for each headline/subtext in the order they appear
        # old files typically have 3 slides: slide 1, 2, 3
        
        scene_blocks = re.split(r'class="[^"]*slide-scene', html)[1:] # split by scene
        
        print(f"--- {fmt} banner{banner_num} ---")
        for idx, scene in enumerate(scene_blocks):
            h_match = re.search(r'<div[^>]*class="[^"]*headline[^"]*"[^>]*style="([^"]*)"', scene, re.IGNORECASE)
            s_match = re.search(r'<div[^>]*class="[^"]*subtext[^"]*"[^>]*style="([^"]*)"', scene, re.IGNORECASE)
            
            h_style = h_match.group(1) if h_match else None
            s_style = s_match.group(1) if s_match else None
            
            h_font = None
            h_line = None
            if h_style:
                m1 = re.search(r'font-size:\s*([^;]+);', h_style)
                if m1: h_font = m1.group(1).strip()
                m2 = re.search(r'line-height:\s*([^;]+);', h_style)
                if m2: h_line = m2.group(1).strip()
                
            s_font = None
            s_line = None
            if s_style:
                m1 = re.search(r'font-size:\s*([^;]+);', s_style)
                if m1: s_font = m1.group(1).strip()
                m2 = re.search(r'line-height:\s*([^;]+);', s_style)
                if m2: s_line = m2.group(1).strip()
                
            print(f"Slide {idx}:")
            print(f"  Headline: font={h_font}, lh={h_line}")
            print(f"  Subtext: font={s_font}, lh={s_line}")
        
