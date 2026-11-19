#!/usr/bin/env python3
import json, os, re, subprocess, sys, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUT = ROOT / "output"
TMP = OUT / "tmp"
OUT.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

W, H = 1080, 1920
BG = (10, 14, 30)
WHITE = (245, 247, 255)
MUTED = (177, 190, 215)
ACCENT = (113, 94, 255)
CYAN = (55, 220, 210)

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        print(p.stderr[-5000:])
        raise RuntimeError("Command failed: " + " ".join(cmd))

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=fnt)[2] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def draw_scene(scene, idx, total, channel, topic):
    im = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(im)
    # Original abstract circuit/game-inspired artwork, not copied game assets.
    for x in range(-300, 1500, 110):
        d.line((x, 0, x-420, H), fill=(20, 31, 58), width=3)
    for y in range(170, H, 180):
        d.line((0, y, W, y), fill=(18, 28, 52), width=2)
    d.rounded_rectangle((65, 90, 1015, 1820), radius=48, outline=(47, 62, 103), width=4)
    d.rounded_rectangle((95, 120, 985, 145), radius=12, fill=ACCENT)
    d.text((105, 205), channel.upper(), font=font( thirty:=30, True), fill=CYAN)
    d.text((105, 300), f"{idx+1:02d} / {total:02d}", font=font(32, True), fill=MUTED)

    # Decorative abstract "city" / controller shapes.
    cx, cy = 540, 720
    d.rounded_rectangle((cx-190, cy-170, cx+190, cy+170), radius=50, fill=(24, 38, 75), outline=ACCENT, width=8)
    d.ellipse((cx-90, cy-70, cx+90, cy+110), outline=CYAN, width=10)
    d.line((cx-115, cy, cx-45, cy), fill=WHITE, width=18)
    d.line((cx-80, cy-35, cx-80, cy+35), fill=WHITE, width=18)
    d.ellipse((cx+65, cy-70, cx+105, cy-30), fill=ACCENT)
    d.ellipse((cx+65, cy+5, cx+105, cy+45), fill=CYAN)
    # Accent bars
    d.rounded_rectangle((130, 1010, 950, 1024), radius=7, fill=(38, 54, 90))

    heading = scene["heading"].strip().upper()
    hf = font(66, True)
    y = 1110
    for line in wrap(d, heading, hf, 820):
        d.text((130, y), line, font=hf, fill=WHITE, stroke_width=1)
        y += 88

    cap = scene["caption"].strip()
    cf = font(43)
    y += 45
    for line in wrap(d, cap, cf, 820):
        d.text((130, y), line, font=cf, fill=MUTED)
        y += 62

    d.text((130, 1710), "ORIGINAL GAMING EXPLAINER", font=font(25, True), fill=CYAN)
    return im

def main():
    content_path = ROOT / "content" / "episode.json"
    data = json.loads(content_path.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    if not scenes:
        raise SystemExit("No scenes found in content/episode.json")
    if len(scenes) > 8:
        raise SystemExit("Use 8 scenes or fewer for this starter workflow.")

    # Validate sources: the workflow requires the creator to supply real sources.
    sources = [s for s in data.get("sources", []) if s.get("url","").startswith("http") and s.get("url") != "https://"]
    if not sources:
        print("WARNING: No usable source URLs supplied. Fact-check the episode before publishing.")

    segments = []
    for i, scene in enumerate(scenes):
        image_path = TMP / f"scene_{i:02d}.png"
        wav_path = TMP / f"voice_{i:02d}.wav"
        mp4_path = TMP / f"segment_{i:02d}.mp4"
        draw_scene(scene, i, len(scenes), data.get("channel_name","Pixel Uncovered"), data.get("topic","Gaming")).save(image_path)

        narration = scene["narration"].strip()
        if not narration:
            raise SystemExit(f"Scene {i+1} has no narration.")
        voice = data.get("voice", "en-us")
        run(["espeak-ng", "-v", voice, "-s", "148", "-w", str(wav_path), narration])
        # Still image duration follows narration; subtitles are part of the original scene graphic.
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(image_path), "-i", str(wav_path),
            "-c:v", "libx264", "-tune", "stillimage", "-vf", "scale=1080:1920,format=yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
            str(mp4_path)
        ])
        segments.append(mp4_path)

    concat_file = TMP / "concat.txt"
    concat_file.write_text("".join(f"file '{p.resolve()}'\n" for p in segments), encoding="utf-8")
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", data.get("title","gaming_short")).strip("_")[:70]
    final = OUT / f"{safe_title or 'gaming_short'}.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", "-movflags", "+faststart", str(final)])

    # First scene also serves as thumbnail artwork.
    (TMP / "scene_00.png").replace(OUT / "thumbnail.png")
    metadata = [
        f"TITLE: {data.get('title','')}",
        "",
        "DESCRIPTION:",
        data.get("description",""),
        "",
        "HASHTAGS: " + " ".join(data.get("hashtags", [])),
        "",
        "TOPIC: " + data.get("topic",""),
        "",
        "SOURCES TO CHECK:",
    ]
    metadata += [f"- {s.get('label','Source')}: {s.get('url','')}" for s in data.get("sources", [])]
    metadata += ["", "REVIEW BEFORE PUBLISHING: verify every claim, audio pronunciation, visual design, copyright and platform suitability."]
    (OUT / "youtube_metadata.txt").write_text("\n".join(metadata), encoding="utf-8")
    (OUT / "script.txt").write_text("\n\n".join(s["narration"] for s in scenes), encoding="utf-8")
    print(f"SUCCESS: {final}")
    print(f"Duration and audio generated. Review the MP4 and metadata before uploading.")

if __name__ == "__main__":
    main()
