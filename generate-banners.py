#!/usr/bin/env python3
import html
import json
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
        'subtext': 'left: 18px; top: 142px; width: 210px; font-size: 14px; line-height: 14px;',
        'logo': 'left: 18px; bottom: 16px; width: 214px;',
    'text_pivot_x': '38px',
    'image_pivot_y': '36px',
    'subcopy_delay': 120,
    },
    '320x320': {
        'show_photo': False,
        'headline': 'left: 20px; top: 16px; width: 278px; font-size: 31px; line-height: 29px;',
        'subtext': 'left: 20px; top: 156px; width: 236px; font-size: 14px; line-height: 14px;',
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


def render_slide_markup(slides, layout):
    chunks = []
    for index, slide in enumerate(slides, start=1):
        active_class = ' is-active' if index == 1 else ''
        photo_markup = ''
        if layout['show_photo']:
            photo_markup = (
        f'      <div class="photo-frame media-pivot" style="{layout["photo_frame"]}">\n'
                f'        <img class="photo" src="{slide["image_src"]}" alt="" draggable="false">\n'
                '      </div>\n'
            )
        chunks.append(
            '    <div class="slide-scene' + active_class + '">\n'
            + photo_markup
      + f'      <div class="headline headline-pivot" style="{layout["headline"]}">{html.escape(slide["headline"])}</div>\n'
      + f'      <div class="subtext copy-pivot" style="{layout["subtext"]}">{html.escape(slide["subtext"])}</div>\n'
            + '    </div>'
        )
    return '\n'.join(chunks)


def generate_index_html(width: int, height: int, title: str, layout, slides):
    slides_markup = render_slide_markup(slides, layout)
    preload_sources = [slide['image_src'] for slide in slides if slide.get('image_src')]
    preload_json = json.dumps(preload_sources, ensure_ascii=False)
    text_pivot_x = layout['text_pivot_x']
    image_pivot_y = layout['image_pivot_y']
    subcopy_delay = layout['subcopy_delay']
    exit_x = f'{width + 120}px'
    exit_y = f'{height + 120}px'
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
      src: url('HandelsbankenSans-Bold.woff2') format('woff2');
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
      opacity: 0;
      pointer-events: none;
      will-change: opacity;
    }}
    .slide-scene.is-active {{
      opacity: 1;
      pointer-events: auto;
      z-index: 1;
    }}
    .slide-scene.is-exiting {{
      opacity: 1;
      z-index: 2;
    }}
    .photo-frame {{
      position: absolute;
      overflow: hidden;
      z-index: 1;
    }}
    .media-pivot {{
      opacity: 0;
      transform: translate(0px, {image_pivot_y});
      will-change: transform, opacity;
    }}
    .media-pivot.is-y {{
      opacity: 1;
      transform: translate(0px, 0px);
      transition: transform 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0), opacity 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .media-pivot.is-y-out {{
      opacity: 0;
      transform: translate(0px, 0px);
      transition: opacity 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .photo {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .headline,
    .subtext {{
      position: absolute;
      z-index: 2;
      color: #fff;
      margin: 0;
      font-weight: 700;
      letter-spacing: -0.04em;
    }}
    .headline {{
      white-space: normal;
      display: flex;
      flex-direction: column;
      gap: 0;
    }}
    .headline-pivot {{
      opacity: 0;
      transform: translate(0px, 36px);
      will-change: transform, opacity;
    }}
    .headline-pivot.is-y {{
      opacity: 1;
      transform: translate(0px, 0px);
      transition: transform 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0), opacity 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .headline-pivot.is-y-out {{
      opacity: 0;
      transform: translate(0px, -{exit_y});
      transition: transform 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0), opacity 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .headline-line {{
      display: block;
      opacity: 1;
      transform: translate({text_pivot_x}, 0px);
      will-change: transform;
    }}
    .headline-line.is-x {{
      transform: translate(0px, 0px);
      transition: transform 600ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .headline-line.is-x-out {{
      opacity: 0;
      transform: translate(calc(-1 * {exit_x}), 0px);
      transition: transform 600ms cubic-bezier(0.7, 0.0, 0.0, 1.0), opacity 450ms linear;
    }}
    .subtext {{
      white-space: normal;
      letter-spacing: 0.02em;
      font-weight: 700;
    }}
    .copy-pivot {{
      opacity: 0;
      transform: translate({text_pivot_x}, 0px);
      will-change: transform, opacity;
    }}
    .copy-pivot.is-x {{
      opacity: 1;
      transform: translate(0px, 0px);
      transition: transform 600ms cubic-bezier(0.7, 0.0, 0.0, 1.0), opacity 900ms cubic-bezier(0.7, 0.0, 0.0, 1.0);
    }}
    .copy-pivot.is-x-out {{
      opacity: 0;
      transform: translate(calc(-1 * {exit_x}), 0px);
      transition: transform 600ms cubic-bezier(0.7, 0.0, 0.0, 1.0), opacity 450ms linear;
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
    <img class="wordmark" src="HB Wordmark HN9 RGB.svg" alt="Handelsbanken" draggable="false">
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

      var slides = Array.prototype.slice.call(document.querySelectorAll('.slide-scene'));
      var current = 0;
      var displayMs = 3800;
      var Y_DURATION = 675;
      var Y_TRANSITION_MS = 900;
      var X_TRANSITION_MS = 600;
      var LINE_STAGGER = 40;
      var MEDIA_DELAY = 100;
      var CONTAINER_DELAY = 100;
      var SUBCOPY_DELAY = {subcopy_delay};
      var EXIT_Y_DELAY = 180;
      var EXIT_SUBCOPY_DELAY = 220;
      var SCENE_CLEANUP_MS = 1200;
      var SCENE_HANDOFF_DELAY = 220;

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

        var text = headline.textContent.trim();
        if (!text) {{
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

        var words = text.split(/\\s+/);
        var lines = [];
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

        measure.remove();
        headline.textContent = '';
        lines.forEach(function (lineText) {{
          var line = document.createElement('span');
          line.className = 'headline-line';
          line.textContent = lineText;
          headline.appendChild(line);
        }});
        headline.dataset.linesReady = 'true';
      }}

      function queueSceneTimer(scene, callback, delay) {{
        if (!scene._timers) {{
          scene._timers = [];
        }}
        var timer = window.setTimeout(callback, delay);
        scene._timers.push(timer);
      }}

      function clearSceneTimers(scene) {{
        if (!scene || !scene._timers) {{
          return;
        }}
        scene._timers.forEach(function (timer) {{
          window.clearTimeout(timer);
        }});
        scene._timers = [];
      }}

      function resetScene(scene) {{
        clearSceneTimers(scene);
        var media = scene.querySelector('.media-pivot');
        var headline = scene.querySelector('.headline-pivot');
        var subcopy = scene.querySelector('.copy-pivot');
        if (media) {{
          media.classList.remove('is-y');
          media.classList.remove('is-y-out');
        }}
        if (headline) {{
          headline.classList.remove('is-y');
          headline.classList.remove('is-y-out');
          splitHeadlineLines(headline);
          Array.prototype.forEach.call(headline.querySelectorAll('.headline-line'), function (line) {{
            line.classList.remove('is-x');
            line.classList.remove('is-x-out');
          }});
        }}
        if (subcopy) {{
          subcopy.classList.remove('is-x');
          subcopy.classList.remove('is-x-out');
        }}
      }}

      function animateSceneIn(scene) {{
        resetScene(scene);

        var media = scene.querySelector('.media-pivot');
        var headline = scene.querySelector('.headline-pivot');
        var subcopy = scene.querySelector('.copy-pivot');
        var lines = headline ? Array.prototype.slice.call(headline.querySelectorAll('.headline-line')) : [];

        if (media) {{
          queueSceneTimer(scene, function () {{
            media.classList.add('is-y');
          }}, MEDIA_DELAY);
        }}

        if (headline) {{
          queueSceneTimer(scene, function () {{
            headline.classList.add('is-y');
          }}, CONTAINER_DELAY);
        }}

        lines.forEach(function (line, index) {{
          queueSceneTimer(scene, function () {{
            line.classList.add('is-x');
          }}, (index * LINE_STAGGER) + Y_DURATION);
        }});

        if (subcopy) {{
          queueSceneTimer(scene, function () {{
            subcopy.classList.add('is-x');
          }}, SUBCOPY_DELAY + Y_DURATION);
        }}
      }}

      function animateSceneOut(scene) {{
        var media = scene.querySelector('.media-pivot');
        var headline = scene.querySelector('.headline-pivot');
        var subcopy = scene.querySelector('.copy-pivot');
        var lines = headline ? Array.prototype.slice.call(headline.querySelectorAll('.headline-line')) : [];

        clearSceneTimers(scene);
        scene.classList.add('is-exiting');

        lines.slice().reverse().forEach(function (line, index) {{
          queueSceneTimer(scene, function () {{
            line.classList.add('is-x-out');
          }}, index * LINE_STAGGER);
        }});

        if (subcopy) {{
          queueSceneTimer(scene, function () {{
            subcopy.classList.add('is-x-out');
          }}, EXIT_SUBCOPY_DELAY);
        }}

        if (media) {{
          queueSceneTimer(scene, function () {{
            media.classList.add('is-y-out');
          }}, EXIT_Y_DELAY);
        }}

        queueSceneTimer(scene, function () {{
          scene.classList.remove('is-active');
          scene.classList.remove('is-exiting');
          resetScene(scene);
        }}, SCENE_CLEANUP_MS);
      }}

      function show(index) {{
        var nextScene = slides[index];
        var currentScene = slides[current];

        if (index === current) {{
          nextScene.classList.add('is-active');
          animateSceneIn(nextScene);
          return;
        }}

        slides.forEach(function (slide, slideIndex) {{
          if (slideIndex !== index && slideIndex !== current) {{
            slide.classList.remove('is-active');
            slide.classList.remove('is-exiting');
            resetScene(slide);
          }}
        }});

        if (currentScene && currentScene !== nextScene) {{
          animateSceneOut(currentScene);
        }}

        window.setTimeout(function () {{
          nextScene.classList.remove('is-exiting');
          nextScene.classList.add('is-active');
          animateSceneIn(nextScene);
        }}, SCENE_HANDOFF_DELAY);

        current = index;
      }}

      function run() {{
        show(0);
        setInterval(function () {{
          show((current + 1) % slides.length);
        }}, displayMs);
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


def build_slide_specs(banner_num: int, copy_map, show_photo: bool):
    specs = []
    for slide_idx, slide_key in enumerate(SLIDE_KEYS[banner_num], start=1):
        copy = copy_map[slide_key]
        specs.append({
            'headline': copy['headline'],
            'subtext': copy['subtext'],
            'image_src': f'images/slide{slide_idx}.jpg' if show_photo else None,
        })
    return specs


def to_web_path(path: Path):
    return str(path).replace('\\', '/')


def find_reference_images(format_dir: Path, banner_num: int, width: int, height: int):
    ref_root = format_dir / 'Layout' if (format_dir / 'Layout').exists() else format_dir
    references = []
    for suffix in ('A', 'B', 'C'):
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
            f'          <a class="banner-link" href="{html.escape(entry["banner_path"])}" target="_blank" rel="noopener noreferrer">Open banner</a>\n'
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
    <h1>Banner Viewer</h1>
    <p class="intro">Open any generated banner in a new tab. Each row also shows the three reference images scaled to stay easy to compare, even for the largest formats.</p>
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

        for banner_num in (1, 2):
            out_dir = format_dir / f'banner{banner_num}'
            images_dir = out_dir / 'images'

            if layout['show_photo']:
                images_dir.mkdir(parents=True, exist_ok=True)
                for slide_idx in (1, 2, 3):
                    src = resolve_slide_source(format_dir, asset_map, banner_num, slide_idx, width, height)
                    dst = images_dir / f'slide{slide_idx}.jpg'
                    copy_slide(src, dst)
            elif images_dir.exists():
                shutil.rmtree(images_dir)

            if shared_font.exists():
                shutil.copy2(shared_font, out_dir / shared_font.name)
            if shared_logo.exists():
                shutil.copy2(shared_logo, out_dir / shared_logo.name)

            title = f'Handelsbanken banner{banner_num} {width}x{height}'
            slides = build_slide_specs(banner_num, copy_map, layout['show_photo'])
            (out_dir / 'index.html').write_text(
                generate_index_html(width, height, title, layout, slides),
                encoding='utf-8',
            )
            (out_dir / 'manifest.json').write_text(generate_manifest(width, height, title), encoding='utf-8')

            index_entries.append({
              'label': f'{format_dir.name} banner{banner_num}',
              'width': width,
              'height': height,
              'banner_path': to_web_path(out_dir / 'index.html'),
              'reference_paths': [to_web_path(path) for path in find_reference_images(format_dir, banner_num, width, height)],
            })

        (ROOT / 'index.html').write_text(generate_root_index(index_entries), encoding='utf-8')


if __name__ == '__main__':
    main()