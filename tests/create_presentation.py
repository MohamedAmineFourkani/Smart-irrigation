"""Generate Smart Irrigation System Presentation (v2 — NASA Clusters)."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# ── Color palette ─────────────────────────────────────────────────────────────
BG_DARK   = RGBColor(0x0A, 0x0F, 0x0D)
BG_CARD   = RGBColor(0x11, 0x1A, 0x15)
GREEN     = RGBColor(0x00, 0xC8, 0x96)
TEAL      = RGBColor(0x3B, 0x82, 0xF6)
ORANGE    = RGBColor(0xF5, 0x9E, 0x0B)
RED       = RGBColor(0xEF, 0x44, 0x44)
PURPLE    = RGBColor(0x8B, 0x5C, 0xF6)
WHITE     = RGBColor(0xE2, 0xEF, 0xE8)
DIM       = RGBColor(0x6B, 0x8F, 0x77)
DARKER    = RGBColor(0x1E, 0x2E, 0x24)

# ── Helper functions ──────────────────────────────────────────────────────────
def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_shape(slide, left, top, width, height, fill_color=None, border_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color or BG_CARD
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_textbox(slide, left, top, width, height, text, font_size=14, bold=False, color=WHITE, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_para(text_frame, text, font_size=12, bold=False, color=WHITE, space_before=Pt(4), alignment=PP_ALIGN.LEFT):
    p = text_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = "Calibri"
    p.alignment = alignment
    if space_before:
        p.space_before = space_before
    return p

def add_bullet(text_frame, text, level=0, font_size=12, color=WHITE):
    p = text_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.name = "Calibri"
    p.level = level
    p.space_before = Pt(2)
    return p

def title_slide(title, subtitle="", color=GREEN):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DARK)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(3.2), Inches(13.333), Pt(3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    add_textbox(slide, Inches(1), Inches(3.6), Inches(11), Inches(1.2), title, font_size=40, bold=True, color=WHITE, alignment=PP_ALIGN.LEFT)
    add_textbox(slide, Inches(1), Inches(4.8), Inches(11), Inches(0.6), subtitle, font_size=18, color=DIM, alignment=PP_ALIGN.LEFT)
    return slide

def section_slide(number, title):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DARK)
    add_textbox(slide, Inches(1), Inches(1.5), Inches(2), Inches(1), f"{number:02d}", font_size=60, bold=True, color=GREEN)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(2.6), Inches(3), Pt(3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = GREEN
    shape.line.fill.background()
    add_textbox(slide, Inches(1), Inches(2.9), Inches(11), Inches(1), title, font_size=32, bold=True, color=WHITE)
    return slide

def content_slide(title, content_fn):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DARK)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.9))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BG_CARD
    shape.line.fill.background()
    add_textbox(slide, Inches(0.8), Inches(0.15), Inches(11), Inches(0.6), title, font_size=22, bold=True, color=GREEN)
    content_fn(slide)
    return slide


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1: Title
# ═══════════════════════════════════════════════════════════════════════════════
s = title_slide(
    "Smart Irrigation System",
    "AI-Driven Hybrid Control Platform\nIoT \u00b7 Machine Learning \u00b7 Failsafe Architecture\n\nMohamed Amine Fourkani"
)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2: Agenda
# ═══════════════════════════════════════════════════════════════════════════════
s = section_slide(1, "Agenda")
txBox = add_textbox(s, Inches(1.5), Inches(3.5), Inches(10), Inches(3.5), "", font_size=16)
tf = txBox.text_frame
tf.word_wrap = True
items = [
    "Problem Statement & Requirements",
    "System Architecture & Design Decisions",
    "NASA POWER Climate Clustering (NEW)",
    "3-Layer Hybrid Decision Engine",
    "ML Model Training & Performance",
    "Protection Mechanisms (Safety by Design)",
    "Data Pipeline & Persistence",
    "Dashboard & Visualization",
    "Testing & Validation",
    "GitHub Repository & Documentation",
]
for i, item in enumerate(items):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = item
    p.font.size = Pt(18)
    p.font.color.rgb = WHITE
    p.font.name = "Calibri"
    p.space_before = Pt(8)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3: Problem Statement
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Problem Statement & Requirements", lambda slide: None)
txBox = add_textbox(s, Inches(0.8), Inches(1.2), Inches(5.5), Inches(5.5), "", font_size=14)
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Problem"; p.font.size = Pt(20); p.font.bold = True; p.font.color.rgb = ORANGE; p.font.name = "Calibri"
bullets = [
    "Traditional irrigation relies on fixed schedules",
    "No adaptation to actual soil conditions or weather",
    "Water waste \u2192 over-irrigation and runoff",
    "Crop stress \u2192 under-irrigation during dry spells",
]
for b in bullets:
    add_bullet(tf, b, font_size=14, color=WHITE)

add_para(tf, "", font_size=8)
add_para(tf, "Solution Requirements", font_size=20, bold=True, color=ORANGE)
reqs = [
    "Real-time soil monitoring via LoRaWAN (TTN)",
    "Weather forecast integration (Open-Meteo + NASA POWER)",
    "AI-assisted decision making (DT / RF / XGBoost)",
    "Failsafe: cooldown, daily budget, manual timeout",
    "Audit trail: every decision logged to SQLite",
    "Interactive dashboard with manual override",
]
for r in reqs:
    add_bullet(tf, r, font_size=14, color=WHITE)

# Right side: key numbers box
shape = add_shape(s, Inches(7), Inches(1.2), Inches(5.5), Inches(4.2), fill_color=BG_CARD, border_color=DARKER)
txBox2 = add_textbox(s, Inches(7.3), Inches(1.4), Inches(5), Inches(4), "", font_size=14)
tf2 = txBox2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]; p.text = "Key Metrics"; p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = GREEN
metrics = [
    ("10,108", "historical sensor readings (Soil_Moisture.csv)"),
    ("9,587", "NASA POWER daily records (26 years)"),
    ("3", "ML models trained & compared"),
    ("5", "climate clusters (KMeans + RF)"),
    ("5", "protection layers (safety chain)"),
    ("9", "decision sources (fully auditable)"),
    ("20 min", "sensor polling interval"),
    ("5 hours", "minimum cooldown between cycles"),
    ("60 min/day", "maximum irrigation budget"),
]
for val, desc in metrics:
    add_para(tf2, f"{val}  {desc}", font_size=14, color=WHITE, space_before=Pt(6))

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4: System Architecture
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("System Architecture", lambda slide: None)

# Layer boxes
layers = [
    ("Layer 3 \u2014 AI Model",         0.8, "DT / RF / XGBoost trained on Soil_Moisture.csv",  GREEN,    Inches(0.6)),
    ("Layer 2 \u2014 Real-Time",       3.0, "TTN Sensor Thresholds + Safety Veto",              TEAL,     Inches(0.6)),
    ("Layer 1 \u2014 Strategic",       5.2, "Open-Meteo 7-day + NASA Cluster Classification",   ORANGE,   Inches(0.6)),
]
for label, left, desc, color, height in layers:
    shape = add_shape(s, Inches(left), Inches(1.3), Inches(3.2), Inches(1.4), fill_color=BG_CARD, border_color=color)
    add_textbox(s, Inches(left + 0.2), Inches(1.4), Inches(2.8), Inches(0.4), label, font_size=14, bold=True, color=color)
    add_textbox(s, Inches(left + 0.2), Inches(1.8), Inches(2.8), Inches(0.6), desc, font_size=11, color=WHITE)

# Planner + Dashboard
shape = add_shape(s, Inches(0.8), Inches(3.3), Inches(3.2), Inches(1.2), fill_color=BG_CARD, border_color=RED)
add_textbox(s, Inches(1.0), Inches(3.4), Inches(2.8), Inches(0.4), "Safety Layer", font_size=14, bold=True, color=RED)
add_textbox(s, Inches(1.0), Inches(3.8), Inches(2.8), Inches(0.5), "Cooldown + Daily Budget + Validation", font_size=11, color=WHITE)

shape = add_shape(s, Inches(0.8), Inches(4.8), Inches(3.2), Inches(1.0), fill_color=BG_CARD, border_color=GREEN)
add_textbox(s, Inches(1.0), Inches(4.9), Inches(2.8), Inches(0.4), "UI Layer", font_size=14, bold=True, color=GREEN)
add_textbox(s, Inches(1.0), Inches(5.25), Inches(2.8), Inches(0.4), "Streamlit Dashboard", font_size=11, color=WHITE)

# Data layer on right
data_items = [
    ("SQLite Database", "data/irrigation.db (decision log)", GREEN),
    ("Historical Soil Data", "data/Soil_Moisture.csv (10,108 rows)", TEAL),
    ("NASA POWER Data", "data/data.csv (9,587 rows, 26 years)", PURPLE),
    ("AI Models", "models/*.pkl (DT, RF, XGBoost)", ORANGE),
    ("Cluster Models", "models/nasa_*.pkl (Scaler, KMeans, RF)", PURPLE),
    ("Config", "src/config.py (all thresholds)", RED),
]
for i, (label, path, color) in enumerate(data_items):
    y = Inches(1.3 + i * 0.9)
    shape = add_shape(s, Inches(8.0), y, Inches(4.5), Inches(0.75), fill_color=BG_CARD, border_color=color)
    add_textbox(s, Inches(8.3), y + Inches(0.02), Inches(4.0), Inches(0.35), label, font_size=13, bold=True, color=color)
    add_textbox(s, Inches(8.3), y + Inches(0.35), Inches(4.0), Inches(0.3), path, font_size=10, color=DIM)

# Project structure
add_textbox(s, Inches(8.0), Inches(5.2), Inches(4.5), Inches(0.4), "Project Structure", font_size=14, bold=True, color=GREEN)
structure_box = add_textbox(s, Inches(8.0), Inches(5.6), Inches(4.5), Inches(1.7), "", font_size=11)
tf = structure_box.text_frame
tf.word_wrap = True
lines = [
    "smart_irrigation_project/",
    "\u251c\u2500\u2500 main.py              Entry point",
    "\u251c\u2500\u2500 src/config.py         All thresholds",
    "\u251c\u2500\u2500 src/controller.py    3-layer engine",
    "\u251c\u2500\u2500 src/cluster_trainer.py  NASA KMeans+RF",
    "\u251c\u2500\u2500 src/forecaster.py    Open-Meteo + NASA",
    "\u251c\u2500\u2500 dashboard/app.py     Streamlit UI",
    "\u2514\u2500\u2500 tests/               Unit tests",
]
for i, line in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = line
    p.font.size = Pt(10)
    p.font.color.rgb = DIM if i == 0 else WHITE
    p.font.name = "Consolas"
    p.space_before = Pt(1)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5: NASA POWER Climate Clustering (NEW)
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("NASA POWER Climate Clustering", lambda slide: None)

# Left: explanation
shape = add_shape(s, Inches(0.8), Inches(1.2), Inches(5.8), Inches(2.5), fill_color=BG_CARD, border_color=PURPLE)
txBox = add_textbox(s, Inches(1.1), Inches(1.3), Inches(5.4), Inches(2.3), "", font_size=14)
tf = txBox.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Pipeline"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = PURPLE
add_bullet(tf, "NASA POWER API \u2192 9,587 daily records (Jan 2000 \u2013 Apr 2026)", font_size=13)
add_bullet(tf, "Features: T2M, RH2M, WS2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN, PS", font_size=13)
add_bullet(tf, "StandardScaler \u2192 KMeans(n=5) \u2192 RandomForest classifier", font_size=13)
add_bullet(tf, "Clusters sorted by ascending rain \u2192 consistent 0..4 labels", font_size=13)
add_bullet(tf, "Models saved: nasa_scaler.pkl, nasa_kmeans.pkl, nasa_rf_cluster.pkl", font_size=13)

# Right: architecture flow
shape = add_shape(s, Inches(7.0), Inches(1.2), Inches(5.5), Inches(2.5), fill_color=BG_CARD, border_color=GREEN)
txBox = add_textbox(s, Inches(7.3), Inches(1.3), Inches(5), Inches(2.3), "", font_size=14)
tf = txBox.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Forecast Integration"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = GREEN
add_bullet(tf, "Open-Meteo API fetches 7-day forecast (unchanged)", font_size=13)
add_bullet(tf, "Same 6 weather features extracted from response", font_size=13)
add_bullet(tf, "Scaled with nasa_scaler.pkl (trained on 26 years)", font_size=13)
add_bullet(tf, "Classified with nasa_rf_cluster.pkl \u2192 0..4 cluster ID", font_size=13)
add_bullet(tf, "CLUSTER_PLAN maps ID \u2192 DRY/MILD/WET + power level", font_size=13)

# Cluster characteristics table
headers = ["Cluster", "Label", "Temp (\u00b0C)", "Humidity (%)", "Rain (mm)", "Power", "x/week"]
rows = [
    ["0", "VERY_DRY",  "14.3", "56", "0.09", "FULL", "4"],
    ["1", "DRY",       "22.7", "55", "0.10", "FULL", "3"],
    ["2", "MILD",      "28.4", "36", "0.10", "HALF", "2"],
    ["3", "WET",       "15.4", "68", "1.07", "LOW",  "1"],
    ["4", "VERY_WET",  "13.8", "78", "14.05","NONE", "0"],
]

shape = add_shape(s, Inches(0.8), Inches(4.0), Inches(11.7), Inches(2.8), fill_color=BG_CARD, border_color=PURPLE)
add_textbox(s, Inches(1.1), Inches(4.1), Inches(5), Inches(0.4), "Cluster Characteristics (mean values)", font_size=14, bold=True, color=PURPLE)

col_widths = [Inches(1.0), Inches(1.5), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.6)]
col_starts = [Inches(1.1)]
for w in col_widths[:-1]:
    col_starts.append(col_starts[-1] + w)

# Header row
for j, (header, cx, cw) in enumerate(zip(headers, col_starts, col_widths)):
    cell = add_shape(s, cx, Inches(4.6), cw - Pt(2), Inches(0.4), fill_color=DARKER, border_color=DARKER)
    add_textbox(s, cx + Inches(0.05), Inches(4.62), cw - Inches(0.1), Inches(0.35), header, font_size=12, bold=True, color=PURPLE, alignment=PP_ALIGN.CENTER)

# Data rows
cluster_colors = [RED, ORANGE, GREEN, TEAL, PURPLE]
for i, row in enumerate(rows):
    y = Inches(5.1 + i * 0.42)
    for j, (val, cx, cw) in enumerate(zip(row, col_starts, col_widths)):
        c = cluster_colors[i] if j == 1 else WHITE
        add_textbox(s, cx + Inches(0.05), y, cw - Inches(0.1), Inches(0.35), val, font_size=12, color=c, alignment=PP_ALIGN.CENTER)

add_textbox(s, Inches(1.1), Inches(6.5), Inches(11), Inches(0.3), "Run: python main.py --train-clusters  \u2022  Trained on 9,587 NASA POWER daily records", font_size=12, color=DIM)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6: Decision Priority Chain
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Decision Priority Chain (9 Levels)", lambda slide: None)

decisions = [
    ("1", "EMERGENCY",    "moisture < 5%",  "Immediate pump ON \u2014 bypasses ALL layers",  RED),
    ("2", "MANUAL_ON",    "User force ON",  "30 min auto-off timer for safety",              ORANGE),
    ("3", "SAFETY_VETO",  "moisture > 20%", "Prevents root rot \u2014 pump forced OFF",       RED),
    ("4", "STRATEGIC_SKIP","Forecast = WET/VERY_WET","No irrigation planned (NASA cluster 3/4)",TEAL),
    ("5", "PLANNER_VETO", "Cooldown/Budget","5h cooldown + 60 min/day limit active",         ORANGE),
    ("6", "CONSENSUS",    "All 3 layers",    "Soil dry + AI agrees + forecast approves",      GREEN),
    ("7", "AI_VETO",      "Soil dry \u2260 AI",  "Soil < 15% but model says no irrigation needed", TEAL),
    ("8", "MONITORING",   "15-20% zone",    "Approaching threshold \u2014 no action yet",      ORANGE),
    ("9", "OPTIMAL",      "moisture > 20%", "Optimal conditions \u2014 no action needed",      GREEN),
]

for i, (pri, source, condition, desc, color) in enumerate(decisions):
    y = Inches(1.1 + i * 0.65)
    add_textbox(s, Inches(0.8), y, Inches(0.5), Inches(0.5), pri, font_size=16, bold=True, color=color)
    shape = add_shape(s, Inches(1.5), y, Inches(2.8), Inches(0.45), fill_color=BG_CARD, border_color=color)
    add_textbox(s, Inches(1.6), y + Inches(0.03), Inches(2.6), Inches(0.4), source, font_size=12, bold=True, color=color)
    add_textbox(s, Inches(4.6), y, Inches(3.5), Inches(0.45), condition, font_size=12, color=WHITE)
    add_textbox(s, Inches(8.3), y, Inches(4.5), Inches(0.45), desc, font_size=11, color=DIM)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 7: ML Models
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Machine Learning Models", lambda slide: None)

# Left: dataset info
shape = add_shape(s, Inches(0.8), Inches(1.2), Inches(5.5), Inches(2.5), fill_color=BG_CARD, border_color=GREEN)
txBox = add_textbox(s, Inches(1.1), Inches(1.3), Inches(5), Inches(2.3), "", font_size=14)
tf = txBox.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Training Data: Soil_Moisture.csv"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = GREEN
add_bullet(tf, "10,108 historical sensor readings", font_size=13)
add_bullet(tf, "Features: temp_SOIL, water_SOIL, conduct_SOIL", font_size=13)
add_bullet(tf, "Target: Irrigation_Required (water_SOIL < 15%)", font_size=13)
add_bullet(tf, "Positive class: 376 / 10,108 (3.7%)", font_size=13)
add_bullet(tf, "Train / Test split: 80 / 20, stratified", font_size=13)

# Right: model params
shape = add_shape(s, Inches(7.0), Inches(1.2), Inches(5.5), Inches(2.5), fill_color=BG_CARD, border_color=TEAL)
txBox = add_textbox(s, Inches(7.3), Inches(1.3), Inches(5), Inches(2.3), "", font_size=14)
tf = txBox.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Model Configuration"; p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = TEAL
add_bullet(tf, "Decision Tree: max_depth=8, min_samples_leaf=10, balanced", font_size=13)
add_bullet(tf, "Random Forest: n_estimators=200, max_depth=10, balanced", font_size=13)
add_bullet(tf, "XGBoost: n_estimators=200, max_depth=6, lr=0.05", font_size=13)
add_bullet(tf, "5-fold Stratified Cross-Validation", font_size=13)
add_bullet(tf, "Evaluation: Accuracy, Precision, Recall, F1", font_size=13)

# Results table
headers = ["Model", "CV Accuracy", "Test Accuracy", "Precision", "Recall", "F1"]
rows = [
    ["Decision Tree", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000"],
    ["Random Forest", "1.0000", "1.0000", "1.0000", "1.0000", "1.0000"],
    ["XGBoost",       "0.9986", "0.9980", "0.9733", "0.9733", "0.9733"],
]

shape = add_shape(s, Inches(0.8), Inches(4.0), Inches(11.7), Inches(2.8), fill_color=BG_CARD, border_color=GREEN)
add_textbox(s, Inches(1.1), Inches(4.1), Inches(5), Inches(0.4), "Performance Comparison", font_size=14, bold=True, color=GREEN)

col_widths = [Inches(2.5), Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.8)]
col_starts = [Inches(1.1)]
for w in col_widths[:-1]:
    col_starts.append(col_starts[-1] + w)

for j, (header, cx, cw) in enumerate(zip(headers, col_starts, col_widths)):
    cell = add_shape(s, cx, Inches(4.6), cw - Pt(2), Inches(0.4), fill_color=DARKER, border_color=DARKER)
    add_textbox(s, cx + Inches(0.05), Inches(4.62), cw - Inches(0.1), Inches(0.35), header, font_size=12, bold=True, color=GREEN, alignment=PP_ALIGN.CENTER)

for i, row in enumerate(rows):
    y = Inches(5.1 + i * 0.45)
    row_color = GREEN if i == 0 else WHITE
    for j, (val, cx, cw) in enumerate(zip(row, col_starts, col_widths)):
        cell_color = GREEN if (i == 0 and j == 0) or (i == 1 and j == 0) else WHITE
        if i == 2:
            cell_color = DIM
        add_textbox(s, cx + Inches(0.05), y, cw - Inches(0.1), Inches(0.35), val, font_size=12, color=row_color if j == 0 else cell_color, alignment=PP_ALIGN.CENTER)

add_textbox(s, Inches(1.1), Inches(6.3), Inches(11), Inches(0.4), "Best model by F1: Decision Tree \u2022 Models saved as .pkl files (joblib serialization)", font_size=12, color=DIM)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8: Protection Mechanisms
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Protection Mechanisms (Safety by Design)", lambda slide: None)

protections = [
    ("Sensor Validation", "validate_sensor_reading()\ndata_fetcher.py", "Checks temp (-10..60\u00b0C), moisture (0..100%),\nconductivity (0..2000 \u00b5S/cm). Invalid \u2192 INVALID_DATA source", GREEN),
    ("Cooldown Timer", "IrrigationPlanner\nplanner.py", "5-hour minimum between irrigation cycles.\nConfigurable via PLANNER_COOLDOWN_MIN.", TEAL),
    ("Daily Budget", "IrrigationPlanner\nplanner.py", "60 min max irrigation per day.\nAutomatically resets at midnight.", ORANGE),
    ("Manual Auto-Off", "controller.py\nconfig.py", "Manual override times out after 30 min.\nConfigurable via MANUAL_PUMP_TIMEOUT_MIN.", RED),
    ("API Retry", "data_fetcher.py\nconfig.py", "3 retries with 5s backoff, 15s timeout.\nOn failure \u2192 SENSOR_OFFLINE logged to DB.", TEAL),
]

for i, (title, location, desc, color) in enumerate(protections):
    y = Inches(1.1 + i * 1.2)
    shape = add_shape(s, Inches(0.8), y, Inches(3.0), Inches(0.95), fill_color=BG_CARD, border_color=color)
    add_textbox(s, Inches(1.0), y + Inches(0.05), Inches(2.6), Inches(0.35), title, font_size=14, bold=True, color=color)
    add_textbox(s, Inches(1.0), y + Inches(0.4), Inches(2.6), Inches(0.4), location, font_size=10, color=DIM)
    shape2 = add_shape(s, Inches(4.0), y, Inches(8.5), Inches(0.95), fill_color=BG_CARD, border_color=DARKER)
    add_textbox(s, Inches(4.2), y + Inches(0.1), Inches(8.1), Inches(0.75), desc, font_size=13, color=WHITE)

add_textbox(s, Inches(0.8), Inches(6.3), Inches(12), Inches(0.5), "All parameters centralized in src/config.py \u2014 no hardcoded values", font_size=13, bold=True, color=ORANGE)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9: Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Dashboard & Visualization", lambda slide: None)

dash_features = [
    ("Live Sensor Data", "Moisture, temperature, conductivity,\nbattery, pump status, connection indicator"),
    ("Protection Status", "Cooldown timer countdown,\ndaily water budget (used / max)"),
    ("AI Decision Engine", "All 3 layers visible with current\nstate and final decision reason"),
    ("7-Day Forecast", "Open-Meteo data classified into\n5 NASA climate clusters"),
    ("Manual Control", "Force ON/OFF with 30 min safety timeout;\nall actions logged to SQLite"),
    ("Alerts", "Low moisture, sensor offline,\nplanner veto, battery low (120s dedup)"),
    ("Historical Charts", "Moisture, temperature, conductivity trends +\npump activations + decision pie"),
    ("Audit Log", "Full decision history with\nreason and decision source"),
]

for i, (title, desc) in enumerate(dash_features):
    col = i % 4
    row = i // 4
    x = Inches(0.8 + col * 3.1)
    y = Inches(1.1 + row * 2.8)
    color = [GREEN, TEAL, ORANGE, PURPLE][col % 4]
    shape = add_shape(s, x, y, Inches(2.8), Inches(2.3), fill_color=BG_CARD, border_color=color)
    add_textbox(s, x + Inches(0.15), y + Inches(0.1), Inches(2.5), Inches(0.4), title, font_size=13, bold=True, color=color)
    add_textbox(s, x + Inches(0.15), y + Inches(0.6), Inches(2.5), Inches(1.4), desc, font_size=11, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10: Data Pipeline
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Data Pipeline & Persistence", lambda slide: None)

# Pipeline flow
boxes = [
    ("TTN Sensor\n(LoRaWAN)", GREEN, Inches(0.8)),
    ("fetch_live_data()\n3 retries + validation", TEAL, Inches(3.5)),
    ("SQLite Database\nirrigation.db", ORANGE, Inches(6.2)),
    ("Streamlit\nDashboard", GREEN, Inches(8.9)),
    ("CSV Export\nDownload", TEAL, Inches(11.0)),
]
for label, color, x in boxes:
    shape = add_shape(s, x, Inches(1.5), Inches(2.2), Inches(1.2), fill_color=BG_CARD, border_color=color)
    add_textbox(s, x + Inches(0.1), Inches(1.6), Inches(2.0), Inches(1.0), label, font_size=12, color=WHITE, alignment=PP_ALIGN.CENTER)

arrow_positions = [(Inches(3.0), Inches(2.0)), (Inches(5.7), Inches(2.0)), (Inches(8.4), Inches(2.0)), (Inches(10.5), Inches(2.0))]
for ax, ay in arrow_positions:
    add_textbox(s, ax, ay, Inches(0.5), Inches(0.4), "\u25b6", font_size=20, color=GREEN, alignment=PP_ALIGN.CENTER)

# Schema
schema = add_shape(s, Inches(0.8), Inches(3.2), Inches(11.7), Inches(3.8), fill_color=BG_CARD, border_color=DARKER)
add_textbox(s, Inches(1.1), Inches(3.3), Inches(5), Inches(0.4), "Database Schema: irrigation_log", font_size=14, bold=True, color=GREEN)

schema_fields = [
    ("id", "INTEGER PK"),
    ("timestamp", "TEXT (ISO8601)"),
    ("temp_SOIL / water_SOIL / conduct_SOIL", "REAL / REAL / INTEGER"),
    ("zone / strategic_label / strategic_power", "TEXT"),
    ("ai_prediction / ai_probability", "INTEGER / REAL"),
    ("pump_on / decision_source / reason", "INTEGER / TEXT / TEXT"),
    ("model / manual_remaining", "TEXT"),
    ("cooldown_remaining / daily_used", "TEXT (human-readable)"),
]
for i, (field, dtype) in enumerate(schema_fields):
    col = i % 2
    row = i // 2
    x = Inches(1.1 + col * 5.8)
    y = Inches(3.8 + row * 0.55)
    add_textbox(s, x, y, Inches(3.0), Inches(0.4), field, font_size=11, bold=True, color=WHITE)
    add_textbox(s, x + Inches(3.0), y, Inches(2.5), Inches(0.4), dtype, font_size=11, color=DIM)

# NASA data flow section
add_textbox(s, Inches(1.1), Inches(6.0), Inches(11), Inches(0.4), "NASA POWER Data Flow (Added in v2)", font_size=14, bold=True, color=PURPLE)
nasa_steps = [
    "1. nasa_fetcher (future) \u2192 NASA POWER API \u2192 data/data.csv (9,587 rows)",
    "2. cluster_trainer \u2192 reads data.csv \u2192 StandardScaler + KMeans + RF \u2192 3 .pkl files",
    "3. forecaster \u2192 Open-Meteo 7-day forecast \u2192 scale with nasa_scaler \u2192 predict with nasa_rf_cluster",
]
for i, step in enumerate(nasa_steps):
    add_textbox(s, Inches(1.1), Inches(6.4 + i * 0.35), Inches(11), Inches(0.3), step, font_size=11, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11: Testing
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Testing & Validation", lambda slide: None)

test_files = [
    ("tests/test_validation.py", "9 tests", GREEN, [
        "Valid reading: all keys present and in range",
        "Missing key detection",
        "Out-of-range moisture (>100%)",
        "Negative moisture",
        "Extreme temperature (100\u00b0C)",
        "Non-numeric value",
        "Partial key check (is_sensor_healthy)",
        "Empty reading (all keys missing)",
    ]),
    ("tests/test_planner.py", "9 tests", TEAL, [
        "Irrigates in RED zone with AI agreement",
        "Blocks irrigation in GREEN zone",
        "Cooldown active (prevents second cycle)",
        "Cooldown expires (allows irrigation)",
        "Daily budget enforcement (15 min limit)",
        "Daily budget resets at midnight",
        "AI disagreement prevents irrigation",
        "ORANGE zone monitoring (no action)",
        "Response dict contains all required keys",
    ]),
]

for i, (filename, count, color, cases) in enumerate(test_files):
    x = Inches(0.8 + i * 6.3)
    shape = add_shape(s, x, Inches(1.2), Inches(5.8), Inches(5.5), fill_color=BG_CARD, border_color=color)
    add_textbox(s, x + Inches(0.2), Inches(1.3), Inches(5.4), Inches(0.4), filename, font_size=13, bold=True, color=color)
    add_textbox(s, x + Inches(0.2), Inches(1.7), Inches(5.4), Inches(0.3), count, font_size=12, color=color)
    for j, case in enumerate(cases):
        add_textbox(s, x + Inches(0.3), Inches(2.2 + j * 0.4), Inches(5.2), Inches(0.35), f"\u2713  {case}", font_size=11, color=WHITE)

add_textbox(s, Inches(0.8), Inches(6.9), Inches(12), Inches(0.4), "Run: python tests/test_validation.py  \u2022  python tests/test_planner.py", font_size=12, color=DIM)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 12: Usage
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("Running the System", lambda slide: None)

commands = [
    ("Live System", GREEN, [
        "python main.py --skip-train             # start live loop with saved models",
        "python main.py --train-clusters          # retrain NASA cluster models",
        "python main.py --model xgboost_model     # use XGBoost (default: RF)",
    ]),
    ("Dashboard", TEAL, [
        "streamlit run dashboard/app.py           # web UI",
    ]),
    ("Standalone Modules", ORANGE, [
        "python src/forecaster.py                 # fetch + classify 7-day forecast",
        "python src/cluster_trainer.py             # train NASA cluster models",
        "python src/trainer.py                    # train DT/RF/XGBoost + compare",
        "python src/database.py                   # init DB + view records",
    ]),
    ("Testing & Seeds", PURPLE, [
        "python tests/test_validation.py          # run validation tests",
        "python tests/test_planner.py             # run planner tests",
        "python tests/seed_data.py                # inject 20 sample records",
    ]),
]

for i, (title, color, cmds) in enumerate(commands):
    col = i % 2
    row = i // 2
    x = Inches(0.8 + col * 6.3)
    y = Inches(1.2 + row * 3.0)
    shape = add_shape(s, x, y, Inches(5.8), Inches(2.5), fill_color=BG_CARD, border_color=color)
    add_textbox(s, x + Inches(0.2), y + Inches(0.05), Inches(5.4), Inches(0.35), title, font_size=14, bold=True, color=color)
    for j, cmd in enumerate(cmds):
        add_textbox(s, x + Inches(0.3), y + Inches(0.5 + j * 0.45), Inches(5.2), Inches(0.4), cmd, font_size=11, color=WHITE, font_name="Consolas")

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 13: GitHub
# ═══════════════════════════════════════════════════════════════════════════════
s = content_slide("GitHub Repository & Documentation", lambda slide: None)

shape = add_shape(s, Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.5), fill_color=BG_CARD, border_color=GREEN)
add_textbox(s, Inches(1.2), Inches(1.7), Inches(11), Inches(0.5), "https://github.com/MohamedAmineFourkani/Smart-irrigation", font_size=20, bold=True, color=GREEN)

items = [
    "README.md: Full architecture documentation, setup guide, config reference",
    "src/config.py: All thresholds documented with defaults and descriptions",
    "tests/: Unit tests for sensor validation and planner logic",
    "dashboard/app.py: 800+ lines of production-quality Streamlit code",
    "cluster_trainer.py: KMeans + RF pipeline on 26 years of NASA POWER data",
    "Full commit history showing incremental development",
]
txBox = add_textbox(s, Inches(1.2), Inches(4.3), Inches(11), Inches(2.5), "", font_size=14)
tf = txBox.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Repository Contents"; p.font.size = Pt(18); p.font.bold = True; p.font.color.rgb = GREEN
for item in items:
    add_bullet(tf, item, font_size=14, color=WHITE)

add_para(tf, "", font_size=8)
add_para(tf, "Key Design Principles", font_size=18, bold=True, color=ORANGE)
principles = [
    "All thresholds centralized in one file (config.py)",
    "Backwards-compatible database migrations (ALTER TABLE ADD COLUMN IF NOT EXISTS)",
    "Every decision is logged for full audit trail",
    "Failsafe: emergency mode bypasses all layers",
]
for p_text in principles:
    add_bullet(tf, p_text, font_size=14, color=WHITE)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 14: Thank You
# ═══════════════════════════════════════════════════════════════════════════════
s = title_slide(
    "Thank You",
    "Questions?\n\nhttps://github.com/MohamedAmineFourkani/Smart-irrigation"
)

# ── Save ──────────────────────────────────────────────────────────────────────
output_path = r"C:\Users\User\Desktop\Smart Irrigation System v2.pptx"
prs.save(output_path)
print(f"Saved: {output_path}")
print(f"Slides: {len(prs.slides)}")
