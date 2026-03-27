#!/usr/bin/env python3
import html
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path('')
SOURCE_ROOT = ROOT / '-Leverans-Markus' / '-Leverans-Markus'
REF_MANIFEST = ROOT / 'banners_december' / '250x600' / 'andas-lugnt' / 'manifest.json'
TEXTS_JSON = ROOT / 'texts.json'

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}
BG_COLOR = '#005ea8'
SLIDE_KEYS = {
    1: ['1a', '1b', '1c'],
    2: ['2a', '2b', '2c'],
}
ALL_SLIDES = [slide for slides in SLIDE_KEYS.values() for slide in slides]
LAYOUTS = {
    '250x600-6px-runda-horn': {
        'show_photo': True,
        'photo_frame': 'left: 15px; top: 16px; width: 220px; height: 342px; border-radius: 6px;',
        'headline': 'left: 15px; top: 378px; width: 220px; font-size: 29px; line-height: 27px;',
        'subtext': 'left: 15px; top: 470px; width: 210px; font-size: 15px; line-height: 15px;',
        'logo': 'left: 15px; bottom: 16px; width: 219px;',
    'text_pivot_x': '28px',
    'image_pivot_y': '36px',
    'subcopy_delay': 160,
    },
    '300x250': {
        'show_photo': False,
        'headline': 'left: 18px; top: 16px; width: 264px; font-size: 29px; line-height: 27px;',
      'subtext': 'left: 18px; top: 141px; width: 210px; font-size: 14px; line-height: 14px;',
        'logo': 'left: 18px; bottom: 16px; width: 214px;',
    'text_pivot_x': '38px',
    'image_pivot_y': '36px',
    'subcopy_delay': 120,
    },
    '320x320': {
        'show_photo': False,
        'headline': 'left: 20px; top: 16px; width: 278px; font-size: 31px; line-height: 29px;',
      'subtext': 'left: 20px; top: 141px; width: 236px; font-size: 14px; line-height: 14px;',
        'logo': 'left: 20px; bottom: 18px; width: 245px;',
    'text_pivot_x': '46px',
    'image_pivot_y': '36px',
    'subcopy_delay': 160,
    },
    '320x480-6px-runda-horn': {
        'show_photo': True,
        'photo_frame': 'left: 21px; top: 21px; width: 278px; height: 172px; border-radius: 6px;',
        'headline': 'left: 21px; top: 221px; width: 278px; font-size: 54px; line-height: 50px;',
        'subtext': 'left: 21px; top: 382px; width: 255px; font-size: 18px; line-height: 18px;',
        'logo': 'left: 21px; bottom: 18px; width: 278px;',
    'text_pivot_x': '46px',
    'image_pivot_y': '36px',
    'subcopy_delay': 160,
    },
    '980x240-6px-runda-horn': {
        'show_photo': True,
        'photo_frame': 'left: 20px; top: 21px; width: 352px; height: 164px; border-radius: 6px;',
        'headline': 'left: 407px; top: 14px; width: 535px; font-size: 56px; line-height: 52px;',
        'subtext': 'left: 409px; top: 178px; width: 295px; font-size: 17px; line-height: 17px;',
        'logo': 'right: 23px; bottom: 17px; width: 279px;',
    'text_pivot_x': '56px',
    'image_pivot_y': '26px',
    'subcopy_delay': 80,
    },
    '980x360-6px-runda-horn': {
        'show_photo': True,
        'photo_frame': 'left: 24px; top: 21px; width: 444px; height: 319px; border-radius: 6px;',
        'headline': 'left: 489px; top: 14px; width: 455px; font-size: 77px; line-height: 71px;',
        'subtext': 'left: 489px; top: 287px; width: 320px; font-size: 19px; line-height: 19px;',
        'logo': 'right: 23px; bottom: 22px; width: 279px;',
    'text_pivot_x': '56px',
    'image_pivot_y': '36px',
    'subcopy_delay': 100,
    },
    '980x480-6px-runda-horn': {
        'show_photo': True,
        'photo_frame': 'left: 23px; top: 21px; width: 445px; height: 441px; border-radius: 6px;',
        'headline': 'left: 491px; top: 16px; width: 458px; font-size: 80px; line-height: 74px;',
        'subtext': 'left: 491px; top: 397px; width: 320px; font-size: 19px; line-height: 19px;',
        'logo': 'right: 23px; bottom: 24px; width: 282px;',
    'text_pivot_x': '56px',
    'image_pivot_y': '36px',
    'subcopy_delay': 120,
    },
}


def parse_format(folder_name: str):
    match = re.match(r'^(\d+)x(\d+)(?:-(\d+)px-runda-horn)?$', folder_name)
    if not match:
        return None
    width, height, radius = match.group(1), match.group(2), match.group(3)
    return int(width), int(height), int(radius or 0)


def parse_mapping(filename: str):
    stem = Path(filename).stem
    mappings = []
    for match in re.finditer(r'(?<![0-9A-Z])([12])([ABC])(?![0-9A-Z])', stem):
        banner = int(match.group(1))
        slide = {'A': 1, 'B': 2, 'C': 3}[match.group(2)]
        mappings.append((banner, slide))
    return mappings


def discover_formats(src_root: Path):
    for directory in sorted(src_root.iterdir()):
        if not directory.is_dir():
            continue
        parsed = parse_format(directory.name)
        if parsed:
            yield directory, parsed


def build_asset_map(format_dir: Path):
    asset_map = {1: {}, 2: {}}
    warnings = []
    for file_path in sorted(format_dir.iterdir()):
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_EXTS:
            continue
        mappings = parse_mapping(file_path.name)
        if not mappings:
            continue
        for banner, slide in mappings:
            if slide in asset_map[banner]:
                warnings.append(
                    f'Overwriting mapping banner {banner} slide {slide}: '
                    f'{asset_map[banner][slide].name} -> {file_path.name}'
                )
            asset_map[banner][slide] = file_path
    return asset_map, warnings


def load_copy_map(path: Path):
    data = json.loads(path.read_text(encoding='utf-8'))
    return {entry['slide'].lower(): entry for entry in data['slides']}


def render_copy_html(text: str):
  escaped = html.escape(text)
  escaped = re.sub(r'(?i)&lt;br\s*/?&gt;', '<br>', escaped)
  return escaped.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')


def render_slide_markup(slide, layout):
    photo_markup = ''
    if layout['show_photo']:
        photo_markup = (
            '      <div class="media-stage media-y">\n'
            f'        <div class="photo-frame media-x" style="{layout["photo_frame"]}">\n'
            f'          <img class="photo" src="{slide["image_src"]}" alt="" draggable="false">\n'
            '        </div>\n'
            '      </div>\n'
        )

    return (
        '    <div class="slide-scene is-active">\n'
        + photo_markup
        + '      <div class="headline-stage headline-y">\n'
        + f'        <div class="headline" style="{layout["headline"]}">{render_copy_html(slide["headline"])}</div>\n'
        + '      </div>\n'
        + '      <div class="subtext-stage subtext-y">\n'
        + f'        <div class="subtext copy-x" style="{layout["subtext"]}">{render_copy_html(slide["subtext"])}</div>\n'
        + '      </div>\n'
        + '    </div>'
    )


def generate_index_html(width: int, height: int, title: str, layout, slide, shared_font_src: str, shared_logo_src: str):
    slides_markup = render_slide_markup(slide, layout)
    preload_sources = [slide['image_src']] if slide.get('image_src') else []
    preload_json = json.dumps(preload_sources, ensure_ascii=False)
    text_pivot_x = layout['text_pivot_x']
    image_pivot_y = layout['image_pivot_y']
    subcopy_delay = layout['subcopy_delay']
    return f'''<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <script>
    (function() {{
      var src = window.API_URL || 'https://s1.adform.net/banners/scripts/rmb/Adform.DHTML.js?bv=' + Math.random();
      var script = document.createElement('script');
      script.src = src;
      document.head.appendChild(script);
    }})();
  </script>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="ad.size" content="width={width},height={height}">
  <title>{html.escape(title)}</title>
  <style>
    @font-face {{
      font-family: 'Handelsbanken Sans';
      src: url('{html.escape(shared_font_src)}') format('woff2');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    html, body {{
      width: {width}px;
      height: {height}px;
      margin: 0;
      padding: 0;
      overflow: hidden;
      font-family: 'Handelsbanken Sans', sans-serif;
    }}
    .banner {{
      position: relative;
      width: 100%;
      height: 100%;
      overflow: hidden;
      cursor: pointer;
      background: {BG_COLOR};
    }}
    .slide-scene {{
      position: absolute;
      inset: 0;
      pointer-events: auto;
      z-index: 1;
    }}
    .photo-frame {{
      position: absolute;
      overflow: hidden;
      z-index: 1;
    }}
    .media-stage,
    .headline-stage,
    .subtext-stage {{
      position: absolute;
      inset: 0;
    }}
    .media-y,
    .headline-y,
    .subtext-y {{
      transform: translate(0px, {image_pivot_y});
      will-change: transform;
    }}
    .media-y.is-ready,
    .headline-y.is-ready,
    .subtext-y.is-ready {{
      transform: translate(0px, 0px);
      transition: transform 1000ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .media-x,
    .headline-line,
    .copy-x {{
      transform: translate({text_pivot_x}, 0px);
      will-change: transform;
    }}
    .media-x.is-ready,
    .headline-line.is-ready,
    .copy-x.is-ready {{
      transform: translate(0px, 0px);
      transition: transform 1000ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .photo {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transform-origin: center center;
      animation: photoZoom 10s linear forwards;
    }}
    @keyframes photoZoom {{
      from {{
        transform: scale(1);
      }}
      to {{
        transform: scale(1.1);
      }}
    }}
    .headline,
    .subtext {{
      position: absolute;
      z-index: 2;
      color:#f6f5ee;
      margin: 0;
      font-weight: 700;
      letter-spacing: 0em;
    }}
    .headline {{
      white-space: normal;
      display: flex;
      flex-direction: column;
      gap: 0;
    }}
    .headline-line {{
      display: block;
    }}
    .subtext {{
      white-space: normal;
      letter-spacing: 0.02em;
      font-weight: 700;
    }}
    .wordmark {{
      position: absolute;
      z-index: 3;
      display: block;
      {layout['logo']}
    }}
    .click-layer {{
      position: absolute;
      inset: 0;
      z-index: 5;
    }}
  </style>
</head>
<body>
  <div class="banner" id="banner">
{slides_markup}
    <img class="wordmark" src="{html.escape(shared_logo_src)}" alt="Handelsbanken" draggable="false">
    <div class="click-layer" id="clickLayer" aria-label="Open"></div>
  </div>
  <script>
    (function () {{
      'use strict';
      var clickLayer = document.getElementById('clickLayer');
      var defaultClickUrl = 'https://www.handelsbanken.se/sv/privat/bolan';
      function getClickUrl() {{
        try {{ if (window.dhtml && typeof dhtml.getVar === 'function') return dhtml.getVar('clickTAG', defaultClickUrl); }} catch (e) {{}}
        if (typeof window.clickTAG === 'string' && window.clickTAG) return window.clickTAG;
        if (typeof window.clickTag === 'string' && window.clickTag) return window.clickTag;
        return defaultClickUrl;
      }}
      clickLayer.addEventListener('click', function () {{ window.open(getClickUrl()); }});

      var scene = document.querySelector('.slide-scene');
      var mediaY = document.querySelector('.media-y');
      var mediaX = document.querySelector('.media-x');
      var headlineY = document.querySelector('.headline-y');
      var subtextY = document.querySelector('.subtext-y');
      var copyX = document.querySelector('.copy-x');
      var Y_DELAY = 100;
      var X_DELAY = 900;
      var LINE_STAGGER = 40;
      var SUBCOPY_DELAY = {subcopy_delay};

      function preload(list, done) {{
        var remaining = list.length;
        if (!remaining) {{
          done();
          return;
        }}
        list.forEach(function (src) {{
          var img = new Image();
          img.onload = img.onerror = function () {{
            remaining -= 1;
            if (!remaining) {{
              done();
            }}
          }};
          img.src = src;
        }});
      }}

      function splitHeadlineLines(headline) {{
        if (!headline || headline.dataset.linesReady === 'true') {{
          return;
        }}

        var segments = headline.innerHTML.split(/<br\s*\/?>/i).map(function (part) {{
          var temp = document.createElement('div');
          temp.innerHTML = part;
          return temp.textContent.replace(/\s+/g, ' ').trim();
        }}).filter(function (part) {{
          return part.length > 0;
        }});

        if (!segments.length) {{
          var fallbackText = headline.textContent.replace(/\s+/g, ' ').trim();
          if (!fallbackText) {{
            headline.dataset.linesReady = 'true';
            return;
          }}
          segments = [fallbackText];
        }}

        if (!segments.length) {{
          headline.dataset.linesReady = 'true';
          return;
        }}

        var styles = window.getComputedStyle(headline);
        var lineHeight = parseFloat(styles.lineHeight);
        var measure = document.createElement('div');
        measure.style.position = 'absolute';
        measure.style.visibility = 'hidden';
        measure.style.pointerEvents = 'none';
        measure.style.left = '-9999px';
        measure.style.top = '0';
        measure.style.width = styles.width;
        measure.style.fontFamily = styles.fontFamily;
        measure.style.fontSize = styles.fontSize;
        measure.style.fontWeight = styles.fontWeight;
        measure.style.letterSpacing = styles.letterSpacing;
        measure.style.lineHeight = styles.lineHeight;
        measure.style.whiteSpace = 'normal';
        document.body.appendChild(measure);

        var lines = [];
        segments.forEach(function (segment) {{
          var words = segment.split(/\s+/);
          var currentLine = '';

          words.forEach(function (word) {{
            var candidate = currentLine ? currentLine + ' ' + word : word;
            measure.textContent = candidate;
            if (measure.getBoundingClientRect().height > lineHeight * 1.5 && currentLine) {{
              lines.push(currentLine);
              currentLine = word;
            }} else {{
              currentLine = candidate;
            }}
          }});

          if (currentLine) {{
            lines.push(currentLine);
          }}
        }});

        measure.remove();
        headline.innerHTML = '';
        lines.forEach(function (lineText) {{
          var line = document.createElement('span');
          line.className = 'headline-line';
          line.textContent = lineText;
          headline.appendChild(line);
        }});
        headline.dataset.linesReady = 'true';
      }}

      function run() {{
        if (!scene) {{
          return;
        }}

        var headline = scene.querySelector('.headline');
        if (headline) {{
          splitHeadlineLines(headline);
        }}

        var lines = headline ? Array.prototype.slice.call(headline.querySelectorAll('.headline-line')) : [];

        window.setTimeout(function () {{
          [mediaY, headlineY, subtextY].forEach(function (element) {{
            if (element) {{
              element.classList.add('is-ready');
            }}
          }});
        }}, Y_DELAY);

        window.setTimeout(function () {{
          if (mediaX) {{
            mediaX.classList.add('is-ready');
          }}
          lines.forEach(function (line, index) {{
            window.setTimeout(function () {{
              line.classList.add('is-ready');
            }}, index * LINE_STAGGER);
          }});
          if (copyX) {{
            window.setTimeout(function () {{
              copyX.classList.add('is-ready');
            }}, SUBCOPY_DELAY);
          }}
        }}, X_DELAY);
      }}

      preload({preload_json}, function () {{
        requestAnimationFrame(run);
      }});
    }})();
  </script>
</body>
</html>
'''


def generate_manifest(width: int, height: int, title: str):
    data = json.loads(REF_MANIFEST.read_text(encoding='utf-8'))
    data['title'] = title
    data['description'] = 'Handelsbanken campaign banner'
    data['width'] = str(width)
    data['height'] = str(height)
    data['source'] = 'index.html'
    return json.dumps(data, ensure_ascii=False, indent=2) + '\n'


def copy_slide(src: Path, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)


def resolve_slide_source(format_dir: Path, asset_map, banner_num: int, slide_idx: int, width: int, height: int):
    source = asset_map[banner_num].get(slide_idx)
    if source:
        return source

    layout_guess = format_dir / 'Layout' / f'{banner_num}{"ABC"[slide_idx - 1]} {width}x{height}.jpg'
    if layout_guess.exists():
        return layout_guess

    source = asset_map[banner_num].get(1)
    if source:
        return source

    raise RuntimeError(
        f'Cannot build {format_dir.name}/banner{banner_num}: no usable source image for slide {slide_idx}'
    )


def build_banner_spec(slide_key: str, copy_map, show_photo: bool):
    copy = copy_map[slide_key]
    return {
        'slide_key': slide_key,
        'headline': copy['headline'],
        'subtext': copy['subtext'],
        'image_src': None,
    }


def to_web_path(path: Path):
    return str(path).replace('\\', '/')


def relative_web_path(target: Path, base_dir: Path):
    return to_web_path(Path(os.path.relpath(target, base_dir)))


def find_reference_images(format_dir: Path, banner_num: int, width: int, height: int, slide_idx: int | None = None):
    ref_root = format_dir / 'Layout' if (format_dir / 'Layout').exists() else format_dir
    references = []
    suffixes = ('ABC'[slide_idx - 1],) if slide_idx else ('A', 'B', 'C')
    for suffix in suffixes:
        expected_stem = f'{banner_num}{suffix} {width}x{height}'
        match = next(
            (
                file_path for file_path in sorted(ref_root.iterdir())
                if file_path.is_file()
                and file_path.suffix.lower() in IMAGE_EXTS
                and file_path.stem == expected_stem
            ),
            None,
        )
        if match:
            references.append(match)
    return references


def generate_root_index(entries):
    sections = []
    for entry in entries:
        reference_markup = ''.join(
            (
                '          <figure class="ref-card">\n'
                f'            <img src="{html.escape(ref_path)}" alt="Reference {idx} for {html.escape(entry["label"])}" loading="lazy">\n'
                f'            <figcaption>Ref {idx}</figcaption>\n'
                '          </figure>\n'
            )
            for idx, ref_path in enumerate(entry['reference_paths'], start=1)
        )
        if not reference_markup:
            reference_markup = '          <p class="ref-empty">No reference images found.</p>\n'

        sections.append(
            '      <section class="banner-card">\n'
            f'        <div class="banner-meta">\n'
            f'          <h2>{html.escape(entry["label"])}</h2>\n'
            f'          <p>{entry["width"]}x{entry["height"]}</p>\n'
            f'          <a class="banner-link" href="{html.escape(entry["banner_path"])}" target="_blank" rel="noopener noreferrer">Öppna</a>\n'
            '        </div>\n'
            '        <div class="ref-grid">\n'
            f'{reference_markup}'
            '        </div>\n'
            '      </section>'
        )

    return f'''<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Banner Viewer</title>
  <style>
    :root {{
      --page-bg: #f5f1e8;
      --card-bg: #ffffff;
      --card-border: #d7d1c3;
      --text: #1b1b1b;
      --muted: #5c5a55;
      --link-bg: #005ea8;
      --link-text: #ffffff;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background: linear-gradient(180deg, #f8f4ea 0%, var(--page-bg) 100%);
      color: var(--text);
    }}
    main {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      line-height: 1.05;
      font-weight: 700;
    }}
    .intro {{
      margin: 0 0 28px;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.4;
    }}
    .banner-list {{
      display: grid;
      gap: 18px;
    }}
    .banner-card {{
      display: grid;
      grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
      gap: 18px;
      align-items: start;
      padding: 18px;
      border: 1px solid var(--card-border);
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.92);
      box-shadow: 0 10px 30px rgba(31, 30, 25, 0.08);
    }}
    .banner-meta h2 {{
      margin: 0 0 6px;
      font-size: 22px;
      line-height: 1.1;
    }}
    .banner-meta p {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 14px;
    }}
    .banner-link {{
      display: inline-block;
      padding: 10px 14px;
      border-radius: 999px;
      background: var(--link-bg);
      color: var(--link-text);
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
    }}
    .ref-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .ref-card {{
      margin: 0;
      padding: 10px;
      border: 1px solid var(--card-border);
      border-radius: 14px;
      background: var(--card-bg);
    }}
    .ref-card img {{
      display: block;
      width: 100%;
      max-height: min(28vh, 220px);
      object-fit: contain;
      object-position: center top;
      margin: 0 auto;
      background: #eef2f5;
      border-radius: 8px;
    }}
    .ref-card figcaption {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      text-align: center;
    }}
    .ref-empty {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    @media (max-width: 960px) {{
      .banner-card {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 700px) {{
      .ref-grid {{
        grid-template-columns: 1fr;
      }}
      .ref-card img {{
        max-height: min(24vh, 180px);
      }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>Banners</h1>
    <div class="banner-list">
{chr(10).join(sections)}
    </div>
  </main>
</body>
</html>
'''


def main():
    if not SOURCE_ROOT.exists():
        raise SystemExit(f'Missing source root: {SOURCE_ROOT}')
    if not TEXTS_JSON.exists():
        raise SystemExit(f'Missing text source: {TEXTS_JSON}')

    shared_font = SOURCE_ROOT / 'HandelsbankenSans-Bold.woff2'
    shared_logo = SOURCE_ROOT / 'HB Wordmark HN9 RGB.svg'
    copy_map = load_copy_map(TEXTS_JSON)
    index_entries = []

    for format_dir, (width, height, _radius) in discover_formats(SOURCE_ROOT):
        layout = LAYOUTS.get(format_dir.name)
        if not layout:
            raise RuntimeError(f'Missing layout config for {format_dir.name}')

        asset_map, warnings = build_asset_map(format_dir)
        print(f'Format {format_dir.name} ({width}x{height})')
        for warning in warnings:
            print('  WARN:', warning)

        for banner_num, slide_keys in SLIDE_KEYS.items():
            for slide_idx, slide_key in enumerate(slide_keys, start=1):
                out_dir = format_dir / f'banner{slide_key}'
                out_dir.mkdir(parents=True, exist_ok=True)
                shared_font_src = relative_web_path(shared_font, out_dir)
                shared_logo_src = relative_web_path(shared_logo, out_dir)

                for stale_asset in (
                    out_dir / 'HandelsbankenSans-Bold.woff2',
                    out_dir / 'HB Wordmark HN9 RGB.svg',
                    out_dir / 'images' / 'slide.jpg',
                ):
                    if stale_asset.exists():
                        stale_asset.unlink()
                if (out_dir / 'images').exists():
                    shutil.rmtree(out_dir / 'images')

                title = f'Handelsbanken banner{slide_key} {width}x{height}'
                slide = build_banner_spec(slide_key, copy_map, layout['show_photo'])
                if layout['show_photo']:
                    slide_src = resolve_slide_source(format_dir, asset_map, banner_num, slide_idx, width, height)
                    slide['image_src'] = relative_web_path(slide_src, out_dir)
                (out_dir / 'index.html').write_text(
                    generate_index_html(width, height, title, layout, slide, shared_font_src, shared_logo_src),
                    encoding='utf-8',
                )
                (out_dir / 'manifest.json').write_text(generate_manifest(width, height, title), encoding='utf-8')

                index_entries.append({
                  'label': f'{format_dir.name} banner{slide_key}',
                  'width': width,
                  'height': height,
                  'banner_path': to_web_path(out_dir / 'index.html'),
                  'reference_paths': [to_web_path(path) for path in find_reference_images(format_dir, banner_num, width, height, slide_idx)],
                })

        (ROOT / 'index.html').write_text(generate_root_index(index_entries), encoding='utf-8')


if __name__ == '__main__':
    main()
