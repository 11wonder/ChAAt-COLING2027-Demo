"""Build the two COLING 2027 paper figures as editable SVG compositions."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import fitz
from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
PAPER = ROOT / "paper_coling2027"
if not PAPER.exists():
    PAPER = ROOT / "paper"
FIGS = PAPER / "figs"
RAW = FIGS / "raw_ui"
RAW.mkdir(parents=True, exist_ok=True)

W = 453.543  # 160 mm in PDF points
WHITE = "#FFFFFF"
INK = "#111827"
MUTED = "#4B5563"
RULE = "#AEB6C2"
PALE = "#F4F6F8"
BLUE = "#E8F0F6"
BLUE_EDGE = "#6D8EA5"
CORAL = "#E94343"
CORAL_PALE = "#FDECEC"

CSS = """
header[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], #MainMenu, footer,
section[data-testid="stSidebar"] {display:none !important;}
.block-container {max-width: 1240px !important; padding: 1.2rem 2rem 1.5rem !important;}
"""


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def text(
    x: float,
    y: float,
    value: str,
    size: float = 6.2,
    weight: int = 400,
    color: str = INK,
    anchor: str = "start",
    ident: str | None = None,
) -> str:
    id_attr = f' id="{esc(ident)}"' if ident else ""
    return (
        f'<text{id_attr} x="{x:.2f}" y="{y:.2f}" fill="{color}" '
        f'font-size="{size:.2f}" font-weight="{weight}" text-anchor="{anchor}">'
        f"{esc(value)}</text>"
    )


def rect(x, y, w, h, fill=WHITE, stroke=RULE, radius=5, sw=0.8, ident=None):
    id_attr = f' id="{esc(ident)}"' if ident else ""
    return (
        f'<rect{id_attr} x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def arrow(x1, y1, x2, y2, color=INK, sw=1.35, dashed=False):
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{color}" stroke-width="{sw}" marker-end="url(#arrow)"{dash}/>'
    )


def write_svg(path: Path, width_pt: float, height_pt: float, body: str):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
  width="160mm" height="{height_pt:.3f}pt" viewBox="0 0 {width_pt:.3f} {height_pt:.3f}"
  role="img" aria-label="ChAAt manuscript figure">
  <style>
    text {{ font-family: Arial, Helvetica, sans-serif; }}
  </style>
  <defs>
    <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4"
      markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M0,0 L8,4 L0,8 z" fill="{INK}"/>
    </marker>
  </defs>
  <rect width="{width_pt:.3f}" height="{height_pt:.3f}" fill="{WHITE}"/>
  {body}
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    return svg


def svg_to_pdf(svg: str, width_pt: float, height_pt: float, pdf_path: Path):
    html_doc = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<style>@page{margin:0;size:160mm "
        f"{height_pt * 25.4 / 72:.4f}mm;}}html,body{{margin:0;padding:0;background:white;}}"
        "svg{display:block;width:160mm;height:"
        f"{height_pt * 25.4 / 72:.4f}mm;}}</style></head><body>{svg}</body></html>"
    )
    with sync_playwright() as playwright:
        browser_root = Path.home() / "AppData" / "Local" / "ms-playwright"
        executable = next(
            path
            for path in (
                browser_root / "chromium-1243" / "chrome-win64" / "chrome.exe",
                browser_root / "chromium-1208" / "chrome-win64" / "chrome.exe",
            )
            if path.exists()
        )
        browser = playwright.chromium.launch(headless=True, executable_path=str(executable))
        page = browser.new_page(viewport={"width": 1200, "height": 1200})
        page.set_content(html_doc, wait_until="load")
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_path),
            width="160mm",
            height=f"{height_pt * 25.4 / 72:.4f}mm",
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()


def pdf_to_png(pdf_path: Path, png_path: Path, dpi=400):
    document = fitz.open(pdf_path)
    pixmap = document[0].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    pixmap.save(png_path)
    document.close()


def capture_ui() -> Path:
    out = RAW / "failure_paper.png"
    with sync_playwright() as playwright:
        browser_root = Path.home() / "AppData" / "Local" / "ms-playwright"
        executable = next(
            path
            for path in (
                browser_root / "chromium-1243" / "chrome-win64" / "chrome.exe",
                browser_root / "chromium-1208" / "chrome-win64" / "chrome.exe",
            )
            if path.exists()
        )
        browser = playwright.chromium.launch(headless=True, executable_path=str(executable))
        context = browser.new_context(
            viewport={"width": 1365, "height": 1100},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto("http://127.0.0.1:8501", wait_until="domcontentloaded")
        page.get_by_role("button", name="Load six-model results").wait_for(timeout=30000)
        page.get_by_role("button", name="Load six-model results").click()
        page.get_by_role("tab", name="Failure explorer").click()
        item = page.get_by_text("FN-E8-03", exact=False).first
        item.wait_for(timeout=30000)
        item.click()
        page.wait_for_timeout(1200)
        page.add_style_tag(content=CSS)
        page.wait_for_timeout(400)
        page.screenshot(
            path=str(out),
            clip={"x": 25, "y": 35, "width": 1310, "height": 1005},
        )
        browser.close()
    return out


def make_architecture():
    height = 236
    body = []
    body.append(text(12, 15, "SOURCE-AUDITED DIAGNOSTIC PIPELINE", 6.5, 700))
    body.append(f'<line x1="12" y1="20" x2="180" y2="20" stroke="{CORAL}" stroke-width="1.3"/>')

    # Data and provenance.
    body.append(rect(12, 34, 102, 180, WHITE, RULE, 7, 0.85, "c:data"))
    body.append(text(22, 49, "DATA TIERS", 6.8, 700, ident="n:data-title"))
    tiers = [
        ("50 diagnostic core", "source-verified"),
        ("41 real-exam items", "ecological validity"),
        ("6 open-ended tasks", "explanation"),
    ]
    for index, (title, subtitle) in enumerate(tiers):
        y = 61 + index * 36
        body.append(rect(20, y, 86, 29, PALE, "#CBD2DA", 4, 0.6))
        body.append(text(27, y + 11, title, 6.2, 700))
        body.append(text(27, y + 22, subtitle, 6.0, 400, MUTED))
    body.append(f'<line x1="20" y1="170" x2="106" y2="170" stroke="{RULE}" stroke-width="0.6"/>')
    body.append(text(23, 183, "SOURCE AUDIT", 6.2, 700))
    body.append(text(23, 194, "answer · source · explanation", 6.0, 400, MUTED))
    body.append(text(23, 205, "linked to every item", 6.0, 400, MUTED))

    # Controlled runner.
    body.append(rect(130, 34, 92, 180, BLUE, BLUE_EDGE, 7, 0.85, "c:runner"))
    body.append(text(140, 49, "MODEL RUNNER", 6.8, 700, ident="n:runner-title"))
    runner_lines = [
        ("6 model presets", 70),
        ("3 repeats · T=0", 91),
        ("No tools", 112),
        ("No web search", 127),
        ("JSON output log", 151),
    ]
    for value, y in runner_lines:
        body.append(text(140, y, value, 6.2, 400 if "No" not in value else 600))
    body.append(f'<circle cx="176" cy="180" r="12" fill="none" stroke="{BLUE_EDGE}" stroke-width="1"/>')
    body.append(text(176, 183, "×18", 6.2, 700, INK, "middle"))
    body.append(text(176, 201, "model × item runs", 5.9, 400, MUTED, "middle"))

    # Scoring and audit.
    body.append(rect(238, 34, 92, 180, WHITE, RULE, 7, 0.85, "c:scoring"))
    body.append(text(248, 49, "SCORING & AUDIT", 6.8, 700, ident="n:scoring-title"))
    scoring_lines = [
        ("Key audit", 70),
        ("Exact match", 91),
        ("Rubric review", 112),
        ("3-rater adjudication", 133),
        ("Saved outputs re-grade", 158),
    ]
    for value, y in scoring_lines:
        body.append(text(248, y, value, 6.2, 400))
    body.append(f'<line x1="248" y1="175" x2="320" y2="175" stroke="{RULE}" stroke-width="0.6"/>')
    body.append(text(248, 194, "item-level p and D", 6.0, 400, MUTED))

    # New review contribution.
    body.append(rect(346, 34, 94, 180, CORAL_PALE, CORAL, 7, 1.4, "c:review"))
    body.append(text(356, 49, "DIAGNOSTIC REVIEW", 6.8, 700, ident="n:review-title"))
    steps = [
        ("1", "Compare models", "and dimensions"),
        ("2", "Filter one", "failed item"),
        ("3", "Inspect expected", "and model answer"),
        ("4", "Trace evidence", "to its source"),
    ]
    for index, (number, main, detail) in enumerate(steps):
        y = 67 + index * 36
        body.append(f'<circle cx="360" cy="{y - 3}" r="6.7" fill="{CORAL}"/>')
        body.append(text(360, y - 0.4, number, 5.6, 700, WHITE, "middle"))
        body.append(text(371, y, main, 6.1, 700))
        body.append(text(371, y + 9, detail, 5.8, 400, MUTED))

    # Main stage arrows.
    body.append(arrow(114, 124, 130, 124, INK, 1.55))
    body.append(arrow(222, 124, 238, 124, INK, 1.55))
    body.append(arrow(330, 124, 346, 124, CORAL, 1.8))
    body.append(f'<circle cx="122" cy="116" r="6.4" fill="{INK}"/>')
    body.append(text(122, 118.3, "1", 5.7, 700, WHITE, "middle"))
    body.append(f'<circle cx="230" cy="116" r="6.4" fill="{INK}"/>')
    body.append(text(230, 118.3, "2", 5.7, 700, WHITE, "middle"))
    body.append(f'<circle cx="338" cy="116" r="6.4" fill="{CORAL}"/>')
    body.append(text(338, 118.3, "3", 5.7, 700, WHITE, "middle"))

    # Source trace back.
    body.append(
        f'<path d="M393 214 L393 224 L63 224 L63 214" fill="none" '
        f'stroke="{CORAL}" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>'
    )
    body.append(text(228, 231, "source trace: every failure remains auditable", 6.0, 600, CORAL, "middle"))

    svg = write_svg(FIGS / "fig1_architecture.svg", W, height, "".join(body))
    svg_to_pdf(svg, W, height, FIGS / "fig1_architecture.pdf")
    pdf_to_png(FIGS / "fig1_architecture.pdf", FIGS / "fig1_architecture.png")


def make_interface():
    screenshot = capture_ui()
    image = Image.open(screenshot).convert("RGB")
    image = image.crop((60, 640, 2620, 2010))
    crop_path = RAW / "failure_paper_crop.png"
    image.save(crop_path)
    encoded = base64.b64encode(crop_path.read_bytes()).decode("ascii")
    screenshot_height = 427.543 * image.height / image.width
    height = 30 + screenshot_height + 8
    body = []
    steps = [
        ("1", "Select model + dimension"),
        ("2", "Open the failed item"),
        ("3", "Read model and source evidence"),
    ]
    xs = [40, 195, 350]
    for index, ((number, label), x) in enumerate(zip(steps, xs)):
        body.append(f'<circle cx="{x - 24}" cy="14" r="7" fill="{CORAL}"/>')
        body.append(text(x - 24, 16.3, number, 5.7, 700, WHITE, "middle"))
        body.append(text(x, 16.3, label, 6.2, 700))
        if index < len(steps) - 1:
            body.append(arrow(x + 98, 14, xs[index + 1] - 35, 14, RULE, 1))
    body.append(rect(12, 30, 429.543, screenshot_height, WHITE, RULE, 6, 0.8, "c:ui-capture"))
    body.append(
        f'<image id="n:ui-screenshot" x="13" y="31" width="427.543" height="{screenshot_height - 2:.3f}" '
        f'preserveAspectRatio="none" href="data:image/png;base64,{encoded}"/>'
    )
    svg = write_svg(FIGS / "fig2_interface.svg", W, height, "".join(body))
    svg_to_pdf(svg, W, height, FIGS / "fig2_interface.pdf")
    pdf_to_png(FIGS / "fig2_interface.pdf", FIGS / "fig2_interface.png")


def main():
    make_architecture()
    make_interface()
    print(FIGS / "fig1_architecture.svg")
    print(FIGS / "fig2_interface.svg")


if __name__ == "__main__":
    main()
