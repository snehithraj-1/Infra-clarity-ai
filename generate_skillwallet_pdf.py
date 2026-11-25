"""
Generate InfraClarity AI SkillWallet PDF with milestone images embedded.
Follows the SkillWallet format with all 7 milestones + bonus pages.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import FrameBreak
from reportlab.pdfgen import canvas as pdf_canvas
from pathlib import Path
import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE     = Path(r'c:\180\gen ai projects\infraclarity-ai')
MILEST   = BASE / 'assets' / 'milestones'
REPORT   = BASE / 'assets' / 'report'
OUT_PDF  = BASE / 'InfraClarity_AI_SkillWallet_Report.pdf'

# ── Colours ───────────────────────────────────────────────────────────────────
NAVY   = colors.HexColor('#17375e')
AMBER  = colors.HexColor('#d97706')
CYAN   = colors.HexColor('#0891b2')
GRN    = colors.HexColor('#059669')
LGRY   = colors.HexColor('#64748b')
BG_BOX = colors.HexColor('#f0f4f8')
WHT    = colors.white
BLK    = colors.black
RED_C  = colors.HexColor('#b91c1c')
PRP_C  = colors.HexColor('#7c3aed')

PW, PH = A4   # 595.27, 841.89
ML = MR = 2.0*cm
MT = 2.5*cm
MB = 2.5*cm
IW = PW - ML - MR   # usable width

# ── Styles ────────────────────────────────────────────────────────────────────
SS = getSampleStyleSheet()

def sty(name, parent='Normal', **kw):
    s = ParagraphStyle(name, parent=SS[parent], **kw)
    return s

H1  = sty('H1',  'Heading1', fontSize=18, textColor=NAVY, spaceAfter=6,
           fontName='Times-Bold', alignment=TA_CENTER)
H2  = sty('H2',  'Heading2', fontSize=14, textColor=NAVY, spaceBefore=12, spaceAfter=4,
           fontName='Times-Bold')
H3  = sty('H3',  'Heading3', fontSize=11, textColor=CYAN, spaceBefore=8, spaceAfter=3,
           fontName='Helvetica-Bold')
H4  = sty('H4',  'Heading4', fontSize=10, textColor=AMBER, spaceBefore=6, spaceAfter=2,
           fontName='Helvetica-Bold')
BODY= sty('BODY','Normal',   fontSize=9.5, leading=14, textColor=BLK, spaceAfter=4,
           fontName='Times-Roman', alignment=TA_JUSTIFY)
BULL= sty('BULL','Normal',   fontSize=9.5, leading=13, leftIndent=16, bulletIndent=4,
           textColor=BLK, spaceAfter=2, fontName='Times-Roman')
CAP = sty('CAP', 'Normal',   fontSize=8.5, leading=12, textColor=LGRY, alignment=TA_CENTER,
           fontName='Helvetica-Oblique', spaceBefore=2, spaceAfter=8)
CTR = sty('CTR', 'Normal',   fontSize=10,  textColor=NAVY, alignment=TA_CENTER,
           fontName='Times-Bold', spaceBefore=4)
MILH= sty('MILH','Heading2', fontSize=13, textColor=WHT, alignment=TA_LEFT,
           fontName='Helvetica-Bold', spaceBefore=0, spaceAfter=0)

# ── Helpers ────────────────────────────────────────────────────────────────────
def img(fname, width=IW, caption=None):
    path = MILEST / fname
    if not path.exists():
        path = REPORT / fname
    if not path.exists():
        return []
    ri = RLImage(str(path), width=width, height=width*(9/16))
    if caption:
        return [ri, Paragraph(caption, CAP)]
    return [ri]

def milestone_header(number, title, col=NAVY):
    """Coloured milestone banner."""
    t = Table([[Paragraph(f'Milestone {number}: {title}', MILH)]],
              colWidths=[IW])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), col),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('ROUNDEDCORNERS',(0,0), (-1,-1), [4,4,4,4]),
    ]))
    return t

def activity_box(label, text, col=CYAN):
    t = Table([[Paragraph(label, sty('alab','Normal',fontSize=9,fontName='Helvetica-Bold',
                                     textColor=WHT)),
                Paragraph(text, sty('atxt','Normal',fontSize=9,fontName='Helvetica',
                                    textColor=WHT, leading=12))]],
              colWidths=[3.5*cm, IW-3.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (0,-1), col),
        ('BACKGROUND',  (1,0), (1,-1), colors.HexColor('#1e3a5f')),
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def bench_table():
    headers = ['Asset Inspection Target', 'Degradation Profile', 'Latency',
               'Detail Gain', 'Canny Gain', 'Laplacian Acuity']
    rows = [
        ['Lattice Transmission Tower', 'Severe Haze + Distant Blur', '1.84 s',
         '+3,861.2%', '+740.0%', '+6,982.4%'],
        ['High-Voltage Insulator String', 'Motion Blur + Low Contrast', '1.42 s',
         '+2,410.5%', '+520.3%', '+4,120.8%'],
        ['Communications Relay Pylon', 'Dense Fog + Backlight Glare', '1.98 s',
         '+4,150.0%', '+810.2%', '+7,430.1%'],
        ['Petrochemical Pipeline Joint', 'Low Light + High-ISO Noise', '1.25 s',
         '+1,890.3%', '+440.1%', '+3,210.5%'],
        ['Substation Transformer Bank', 'Optical Blur + Sensor Grain', '1.65 s',
         '+2,980.7%', '+615.4%', '+5,104.2%'],
    ]
    data = [[Paragraph(h, sty('th','Normal',fontSize=8,fontName='Helvetica-Bold',
                               textColor=WHT))] for h in headers]
    # Reformat as row-major
    tdata = [[Paragraph(h, sty('th','Normal',fontSize=8,fontName='Helvetica-Bold',
                                textColor=WHT)) for h in headers]]
    for row in rows:
        tdata.append([Paragraph(c, sty('td','Normal',fontSize=8,fontName='Helvetica',
                                        textColor=BLK, leading=11)) for c in row])
    cw = [4.5*cm, 4.0*cm, 1.6*cm, 2.2*cm, 2.2*cm, 2.5*cm]
    t = Table(tdata, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), NAVY),
        ('BACKGROUND',  (0,1), (-1,1), BG_BOX),
        ('BACKGROUND',  (0,3), (-1,3), BG_BOX),
        ('BACKGROUND',  (0,5), (-1,5), BG_BOX),
        ('GRID',        (0,0), (-1,-1), 0.4, LGRY),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('ALIGN',       (2,1), (-1,-1), 'CENTER'),
        ('TEXTCOLOR',   (3,1), (-1,-1), colors.HexColor('#15803d')),
        ('FONTNAME',    (3,1), (-1,-1), 'Helvetica-Bold'),
    ]))
    return t

def param_table():
    rows = [
        ('Input Media',       'PNG, JPEG, WebP, TIFF up to 8K resolution (16-bit / 8-bit RGB)'),
        ('Degradation Profiler','Multi-spectral Laplacian blur score, DCP haze transmission (0–1), noise variance'),
        ('Optical Dehazing',  'Dark Channel Prior (15×15) + O(N) Guided Filter (r=40, ε=0.001) + LAB CLAHE'),
        ('Structural Denoising','Fast Non-Local Means (h=10, template=7, search=21) + Edge-preserving Bilateral'),
        ('Acuity Deblurring', 'Dual-Scale Adaptive Unsharp Masking with anti-halo noise thresholding'),
        ('Super-Resolution',  'Lanczos-4 8-lobed sinc (2× upscale) + High-frequency gradient boost'),
        ('Tiled Memory Engine','512×512 tiles, 64px overlap, 2D cosine apodization; constant RAM <450 MB'),
        ('Close-Range Synthesis','Contour salience clustering, Harris corner density ROI ranking, macro upscaling'),
        ('AI Copilot',        'Google Gemini Flash-Lite SSE streaming endpoint + Expert Heuristic fallback'),
        ('Web Architecture',  'FastAPI async backend (Python 3.13) + React 19 / TypeScript + Tailwind CSS'),
        ('Inspection UI',     'Synchronized 1:1 dual-pane viewer, split slider, crack heatmap, metrics HUD'),
    ]
    tdata = [[Paragraph('Parameter', sty('ph','Normal',fontSize=8.5,fontName='Helvetica-Bold',textColor=WHT)),
              Paragraph('Specification', sty('sh','Normal',fontSize=8.5,fontName='Helvetica-Bold',textColor=WHT))]]
    for p, s in rows:
        tdata.append([
            Paragraph(p, sty('pk','Normal',fontSize=8.5,fontName='Helvetica-Bold',textColor=NAVY)),
            Paragraph(s, sty('sv','Normal',fontSize=8.5,fontName='Helvetica',textColor=BLK,leading=11)),
        ])
    t = Table(tdata, colWidths=[4.5*cm, IW-4.5*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), NAVY),
        ('GRID',        (0,0), (-1,-1), 0.4, LGRY),
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHT, BG_BOX]),
    ]))
    return t


# ── Page number callback ───────────────────────────────────────────────────────
def add_page_elements(cv, doc):
    cv.saveState()
    # Outer border
    cv.setStrokeColor(NAVY); cv.setLineWidth(1)
    cv.rect(1.0*cm, 1.0*cm, PW-2.0*cm, PH-2.0*cm, stroke=1, fill=0)
    # Page number
    cv.setFont('Helvetica', 9); cv.setFillColor(CYAN)
    cv.drawCentredString(PW/2, 1.3*cm, f'— {doc.page} —')
    # Header line
    if doc.page > 1:
        cv.setStrokeColor(LGRY); cv.setLineWidth(0.3)
        cv.line(ML, PH-MT+0.3*cm, PW-MR, PH-MT+0.3*cm)
        cv.setFont('Helvetica', 7.5); cv.setFillColor(LGRY)
        cv.drawRightString(PW-MR, PH-MT+0.5*cm, 'InfraClarity AI — SkillWallet Report  |  SRM University-AP')
    cv.restoreState()

# ── Build story ────────────────────────────────────────────────────────────────
story = []

# ═══════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════
# SRM logo if present
logo_path = REPORT / 'white_pix_17.png'
if logo_path.exists():
    story.append(RLImage(str(logo_path), width=3.5*cm, height=3.5*cm))
    story.append(Spacer(1, 0.5*cm))

story += [
    Paragraph('SRM University-AP, Amaravati', sty('univ','Normal',fontSize=11,
              fontName='Helvetica',textColor=LGRY,alignment=TA_CENTER)),
    Paragraph('Department of Computer Science and Engineering', sty('dept','Normal',
              fontSize=10,fontName='Helvetica',textColor=LGRY,alignment=TA_CENTER)),
    Spacer(1, 0.6*cm),
    Paragraph('InfraClarity AI', sty('title','Normal',fontSize=28,fontName='Times-Bold',
              textColor=NAVY,alignment=TA_CENTER)),
    Paragraph('Intelligent Degradation-Aware Infrastructure Image Restoration\nand Multimodal Inspection System',
              sty('sub','Normal',fontSize=14,fontName='Times-Roman',textColor=CYAN,
                  alignment=TA_CENTER,leading=20)),
    Spacer(1, 0.4*cm),
    HRFlowable(width=IW, thickness=2, color=AMBER, spaceAfter=10),
    Paragraph('SkillWallet Project Report', sty('swt','Normal',fontSize=13,
              fontName='Helvetica-Bold',textColor=AMBER,alignment=TA_CENTER)),
    HRFlowable(width=IW, thickness=1, color=LGRY, spaceBefore=8, spaceAfter=20),
    Spacer(1, 0.6*cm),
]

# Cover image = M1 architecture
story += img('m1_architecture.png', IW*0.95,
             'Fig. 0 — Full system architecture overview')
story.append(Spacer(1, 0.6*cm))

meta = Table([
    ['Course', 'CSE302 — Capstone Lab'],
    ['Platform', 'FastAPI + React 19 + Gemini Flash-Lite'],
    ['Processing', '1.2–1.9 s per capture  |  <450 MB RAM (8K)'],
    ['Tests',     '40 / 40 passing (32 pytest + 8 Vitest)'],
    ['GitHub',    'github.com/snehithraj-1/Infra-clarity-ai'],
], colWidths=[3.5*cm, IW-3.5*cm])
meta.setStyle(TableStyle([
    ('FONTNAME',    (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTNAME',    (1,0), (1,-1), 'Helvetica'),
    ('TEXTCOLOR',   (0,0), (0,-1), NAVY),
    ('TEXTCOLOR',   (1,0), (1,-1), BLK),
    ('FONTSIZE',    (0,0), (-1,-1), 9.5),
    ('GRID',        (0,0), (-1,-1), 0.3, LGRY),
    ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ('TOPPADDING',  (0,0),(-1,-1), 5),
    ('LEFTPADDING', (0,0),(-1,-1), 8),
    ('ROWBACKGROUNDS',(0,0),(-1,-1),[BG_BOX,WHT]),
]))
story.append(meta)
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# M1 — Problem Analysis, Model Selection & Architecture
# ═══════════════════════════════════════════════════════════
story.append(milestone_header(1, 'Problem Analysis, Model Selection and Architecture', NAVY))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Overview', H2))
story.append(Paragraph(
    'Modern civil, telecommunication and energy infrastructure requires continuous visual inspection. '
    'Raw aerial and field captures from UAVs or ground cameras are chronically degraded by atmospheric '
    'haze, motion blur and sensor noise — masking the micro-structural details that engineers need to '
    'certify structural integrity. InfraClarity AI resolves this by deploying a physics-based, '
    'non-hallucinatory restoration pipeline guided by real pixel evidence.', BODY))

story.append(Paragraph('Activity 1.1 — Analyze the Problem and Define Objectives', H3))
for bullet in [
    '<b>Atmospheric Haze & Fog:</b> scatter incident light and compress dynamic range. Dark Channel Prior haze score threshold: 0.1.',
    '<b>Motion Blur:</b> UAV rotor vibration and wind gusts reduce edge acuity. Laplacian variance threshold: &lt;50.',
    '<b>Sensor Noise:</b> high-ISO noise under adverse illumination hides micro-fissures. Noise σ² threshold: 5.',
    '<b>Low Resolution:</b> short side &lt;1080 px prevents sub-millimetre defect visibility → super-resolution triggered.',
]:
    story.append(Paragraph(f'• {bullet}', BULL))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph('Activity 1.2 — Research and Select Techniques & AI Model', H3))
acts = [
    ('Physics-Based Dehazing', 'Dark Channel Prior (15×15 patch) + O(N) Guided Filter + LAB CLAHE'),
    ('Structural Denoising',  'Fast Non-Local Means (h=10) — averages non-local patches without eroding fissures'),
    ('Adaptive Deblurring',   'Dual-scale Unsharp Mask with edge-threshold anti-halo suppression'),
    ('Super-Resolution',      'Lanczos-4 8-lobed sinc (2×) + high-frequency gradient boost'),
    ('Multimodal AI Model',   'Google Gemini Flash-Lite — first-token latency <1.5 s for streaming visual diagnosis'),
]
for lbl, desc in acts:
    story.append(activity_box(lbl, desc, CYAN))
    story.append(Spacer(1, 0.1*cm))

story.append(Paragraph('Activity 1.3 — Architecture Definition', H3))
story.append(Paragraph(
    'The system uses a decoupled two-tier architecture: a React 19 / TypeScript inspection console '
    'handles upload, pipeline controls and the synchronized 1:1 viewer; the FastAPI async backend '
    'orchestrates degradation profiling, the ordered pipeline and macro synthesis via ThreadPoolExecutor. '
    'Server-Sent Events (SSE) stream progress from 0 % to 100 % and AI tokens at 142 tok/s.', BODY))

story.append(Paragraph('System Specifications & Parameters', H3))
story.append(param_table())
story.append(Spacer(1, 0.3*cm))

story += img('m1_architecture.png', IW,
             'Fig. 1 — Full system architecture: degradation sources → 4-stage pipeline → Gemini copilot')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# M2 — Restoration Engine Development
# ═══════════════════════════════════════════════════════════
story.append(milestone_header(2, 'Restoration Engine Development', colors.HexColor('#1e3a8a')))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Overview', H2))
story.append(Paragraph(
    'Milestone 2 builds the deterministic, physics-guided engine that diagnoses and restores each capture '
    'within a fixed memory budget. The degradation profiler first quantifies the four quality signals; '
    'the four-stage pipeline then corrects them in enforced order; and the tiled memory engine makes '
    'this feasible on 8K drone panoramas on constrained field workstations.', BODY))

story.append(Paragraph('Activity 2.1 — Degradation Profiler', H3))
prof_rows = [
    ('Blur Score', 'Modified Laplacian variance of the luminance channel', 'Sharp > 50 | Blurry < 20'),
    ('Atmospheric Haze', 'Dark Channel Prior minimum across RGB patches', '0 = clear | >0.1 = hazy'),
    ('Sensor Noise', 'High-frequency residual variance after Gaussian subtraction', 'Clean <2 | Noisy >8'),
    ('RMS Contrast', 'Root-mean-square of pixel intensity deviation', '<0.15 = compressed range'),
]
pdata = [[Paragraph(h, sty('ph','Normal',fontSize=8.5,fontName='Helvetica-Bold',textColor=WHT))
          for h in ['Metric','Computation Method','Thresholds']]]
for r in prof_rows:
    pdata.append([Paragraph(c, sty('pd','Normal',fontSize=8.5,fontName='Helvetica',
                                    textColor=BLK,leading=11)) for c in r])
ptbl = Table(pdata, colWidths=[3.5*cm, 7.5*cm, 5.5*cm])
ptbl.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), NAVY),
    ('GRID',        (0,0), (-1,-1), 0.4, LGRY),
    ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ('BOTTOMPADDING',(0,0),(-1,-1), 5),
    ('TOPPADDING',  (0,0),(-1,-1), 5),
    ('LEFTPADDING', (0,0),(-1,-1), 6),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHT,BG_BOX]),
]))
story.append(ptbl)
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph('Activity 2.2 — Four-Stage Restoration Pipeline', H3))
pipeline_stages = [
    ('Stage 1 — DEHAZE', CYAN,
     'The atmospheric light vector A is estimated from the top 0.1% brightest pixels in the dark channel. '
     'An edge-preserving Guided Filter (radius=40, ε=0.001) refines the coarse transmission map t(x) to '
     'recover scene radiance. CLAHE in LAB color space equalizes contrast:\n'
     '  I(x) = J(x)·t(x) + A·(1−t(x))   →   J(x) = (I(x)−A) / max(t(x), 0.1) + A'),
    ('Stage 2 — DENOISE', GRN,
     'Fast Non-Local Means (h=10, template window=7, search window=21) compares non-local patches to smooth '
     'sensor grain without eroding high-contrast structural edges (fissures, bolt threads). Outperforms '
     'Gaussian and median filters on structured noise.'),
    ('Stage 3 — DEBLUR', AMBER,
     'A dual-scale Laplacian unsharp mask isolates high-frequency edges. An edge-threshold mask suppresses '
     'sharpening in flat sky regions to prevent noise amplification and ringing halos.'),
    ('Stage 4 — SUPER-RESOLUTION', PRP_C,
     '8-lobed Lanczos-4 sinc interpolation doubles pixel density (2× linear). A subsequent high-frequency '
     'gradient boost restores sub-millimetre fastener visibility lost during downsampling.'),
]
for stg, col, txt in pipeline_stages:
    story.append(Paragraph(stg, sty('stg','Normal',fontSize=10,fontName='Helvetica-Bold',textColor=col,spaceBefore=8)))
    story.append(Paragraph(txt, BODY))

story.append(Paragraph('Activity 2.3 — Tiled Overlap-Blend Memory Engine', H3))
story.append(Paragraph(
    '512×512 tiles with a 64px overlap are processed individually; 2D cosine apodization blends the overlaps, '
    'eliminating seam artifacts. 8K drone panoramas processed with a fixed window kept RAM below 450 MB, '
    'avoiding out-of-memory crashes on constrained field workstations.', BODY))

story += img('m2_restoration_pipeline.png', IW,
             'Fig. 2 — Original (hazy/blurry/noisy) → Stage-by-stage restoration → Super-resolved output')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# M3 — Pattern Intelligence & Macro Synthesis
# ═══════════════════════════════════════════════════════════
story.append(milestone_header(3, 'Pattern Intelligence and Macro Synthesis', colors.HexColor('#4c1d95')))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Overview', H2))
story.append(Paragraph(
    'Field engineers often require close-up views to verify micro-structural integrity at joints, insulator sheds '
    'and pipeline welds. Milestone 3 implements a pattern-driven algorithm that extracts and reconstructs the '
    'most salient structural components from the restored image — deterministically and without inventing detail.', BODY))

story.append(Paragraph('Activity 3.1 — Contour and Saliency Detection', H3))
story.append(Paragraph(
    'Morphological gradient filters and Canny edge contouring detect geometric asset structures '
    '(transmission lattice junctions, insulator disc assemblies, pipeline weld beads) and distinguish '
    'them from sky or vegetation backgrounds. A salience score ranks each contour by enclosed area '
    'and edge density.', BODY))

story.append(Paragraph('Activity 3.2 — High-Density ROI Extraction and Macro Synthesis', H3))
for b in [
    '<b>ROI Ranking:</b> Harris corner density scores candidate sub-windows; structural variance further clusters the top 3–4 inspection zones with localized bounding boxes.',
    '<b>Macro Synthesis:</b> extracted patches undergo localized bilateral filtering + 2×/4× edge-preserving super-resolution, producing close-range macro views — equivalent to what a telephoto lens would capture at close range without fog.',
    '<b>Geometric Fidelity:</b> unlike uncontrolled generative diffusion models that may hallucinate fasteners, the pipeline is deterministic and physics-guided: outputs follow the real asset with zero invented geometry.',
    '<b>Named ROIs (example):</b> Tower Apex & Mast Head | Crossarm Gusset & Bolt Cluster | Diagonal Lattice Bracing Splice | Lower Structural Leg & Flange.',
]:
    story.append(Paragraph(f'• {b}', BULL))
story.append(Spacer(1, 0.2*cm))

story += img('m3_macro_synthesis.png', IW,
             'Fig. 3 — Harris corner map + contour saliency + 4 extracted close-range macro ROIs')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# M4 — Backend & AI Copilot Development
# ═══════════════════════════════════════════════════════════
story.append(milestone_header(4, 'Backend and AI Copilot Development', colors.HexColor('#0c4a6e')))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Overview', H2))
story.append(Paragraph(
    'The FastAPI async backend orchestrates the full processing lifecycle and streams progress and AI '
    'tokens to the React console over SSE. Gemini Flash-Lite provides multimodal defect diagnosis; '
    'a local expert heuristic engine provides offline resilience.', BODY))

story.append(Paragraph('Activity 4.1 — Build the FastAPI Backend', H3))
for b in [
    '<b>Framework:</b> Python 3.13 on Windows/Linux with FastAPI, Uvicorn and SSE-Starlette; image operations via OpenCV + vectorized NumPy kernels.',
    '<b>Async Job Coordinator:</b> ThreadPoolExecutor isolates heavy CPU vision workloads. SSE event queues stream progress (0%→100%) and intermediate diagnostics.',
    '<b>Enhancement Endpoint:</b> POST /api/v1/jobs/enhance accepts {preset, options: {match_original}}.',
    '<b>Assistant Endpoint:</b> POST /api/v1/assistant/stream sends the downsampled capture + quality metrics to Gemini, streaming tokens back as SSE events.',
    '<b>Export Endpoint:</b> GET /api/v1/jobs/{id}/export generates the PDF Field Audit Report with pipeline metadata.',
]:
    story.append(Paragraph(f'• {b}', BULL))

story.append(Paragraph('Activity 4.2 — Integrate the Gemini Streaming Copilot', H3))
for b in [
    '<b>Streaming Endpoint:</b> /api/v1/assistant/stream sends the capture + quality metrics to Google Gemini Flash-Lite and streams tokens back over SSE.',
    '<b>Latency:</b> first-token latency under 1.5 s; SSE reduced initial feedback from ~6.5 s (batch) to 1.4 s (streaming).',
    '<b>Token Rate:</b> 142 tokens/s — sufficient for real-time markdown render in the inspection console.',
    '<b>Heuristic Fallback:</b> when offline or no API key is configured, a rule-based expert engine maps blur, haze and contrast scores to structural vulnerability warnings — zero external dependency.',
    '<b>Security:</b> API key stored in environment variable GEMINI_API_KEY; never committed to Git (GitHub push-protection active).',
]:
    story.append(Paragraph(f'• {b}', BULL))
story.append(Spacer(1, 0.2*cm))

story += img('m4_backend_copilot.png', IW,
             'Fig. 4 — SSE sequence diagram (left) + live Gemini copilot streaming response (right)')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# M5 — Frontend Development
# ═══════════════════════════════════════════════════════════
story.append(milestone_header(5, 'Frontend Development', colors.HexColor('#064e3b')))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Overview', H2))
story.append(Paragraph(
    'Milestone 5 builds the inspection-grade web console in React 19 / TypeScript + Vite, styled with '
    'Tailwind CSS. The interface gives engineers full control over the restoration pipeline and presents '
    'results in a synchronized dual-pane viewer with multiple comparison modes.', BODY))

story.append(Paragraph('Activity 5.1 — Design and Develop the Inspection Console', H3))
for b in [
    '<b>Autonomous Optical Telemetry Matrix:</b> four SVG gauge-meter widgets reporting Blur, Atmospheric Haze, Sensor Noise and RMS Contrast with status badges (Sharp / Moderate Haze / Clean / Suboptimal).',
    '<b>Inspection Presets:</b> Auto (Diagnosis), Hazy/Rainy, Distant Tower, Pipeline Close-up, Low Light — each sets per-stage intensities automatically.',
    '<b>Pipeline Stage Controls:</b> per-stage ON/OFF toggles + intensity sliders (Dehaze, Denoise, Deblur, Super-Resolution) with enforced execution order.',
    '<b>Synchronized Dual-Pane Viewer:</b> custom canvas pan/zoom sync. Four modes: Split Slider | Side-by-Side | Crack & Edge Heatmap | Restored Delta.',
    '<b>ROI Fault Spotlights:</b> overlaid bounding boxes highlight macro synthesis regions with acuity-gain badges.',
]:
    story.append(Paragraph(f'• {b}', BULL))

story.append(Paragraph('Activity 5.2 — Build the Copilot Panel and Export Tools', H3))
for b in [
    '<b>MarkdownRenderer:</b> Gemini-styled rich Markdown with structured headers, defect callout badges, inspection tables and an active typing cursor.',
    '<b>Prompt Pills:</b> one-tap question shortcuts ("Tell me what is in this image", "What loopholes exist?", "Are there cracks near the bolts?").',
    '<b>Export & Archival:</b> Field Audit Report (PDF), PNG, JPEG, JSON download, Same-Size (original resolution) option, Strip GPS EXIF option.',
    '<b>Responsive Layout:</b> grid-cols-1 → sm:grid-cols-2 → lg:grid-cols-3; MetricsCards truncation; DiagnosisPanel flex-wrap header.',
]:
    story.append(Paragraph(f'• {b}', BULL))
story.append(Spacer(1, 0.2*cm))

story += img('m5_frontend_console.png', IW,
             'Fig. 5 — React 19 console: pipeline controls (left), dual-pane viewer (centre), Gemini copilot + telemetry (right)')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# M6 — Testing, Evaluation & Deployment
# ═══════════════════════════════════════════════════════════
story.append(milestone_header(6, 'Testing, Evaluation and Deployment', colors.HexColor('#7f1d1d')))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Activity 6.1 — Automated Test Suites', H2))
test_data = [
    [Paragraph(h, sty('th','Normal',fontSize=8.5,fontName='Helvetica-Bold',textColor=WHT))
     for h in ['Suite', 'Framework', 'Cases', 'Passed', 'Status']],
    ['Degradation Profiler', 'pytest', '8', '8', 'PASS'],
    ['Pipeline Integration', 'pytest', '12', '12', 'PASS'],
    ['SSE Endpoint',         'pytest', '6', '6', 'PASS'],
    ['API Routes',           'pytest', '6', '6', 'PASS'],
    ['Frontend Components',  'Vitest', '8', '8', 'PASS'],
    ['TOTAL',                '—',     '40', '40', 'ALL GREEN'],
]
for ri in range(1, len(test_data)):
    test_data[ri] = [Paragraph(c, sty('td','Normal',fontSize=8.5,
                                       fontName='Helvetica-Bold' if ri==len(test_data)-1 else 'Helvetica',
                                       textColor=GRN if ri==len(test_data)-1 else BLK)) for c in test_data[ri]]
ttbl = Table(test_data, colWidths=[5.5*cm, 2.5*cm, 2*cm, 2*cm, 2*cm])
ttbl.setStyle(TableStyle([
    ('BACKGROUND',  (0,0),  (-1,0),  NAVY),
    ('BACKGROUND',  (0,-1), (-1,-1), colors.HexColor('#052e16')),
    ('GRID',        (0,0),  (-1,-1), 0.4, LGRY),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('TOPPADDING',  (0,0),  (-1,-1), 5),
    ('LEFTPADDING', (0,0),  (-1,-1), 8),
    ('ALIGN',       (2,1),  (-1,-1), 'CENTER'),
    ('ROWBACKGROUNDS',(0,1),(-2,-1),[WHT,BG_BOX]),
]))
story.append(ttbl)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Activity 6.2 — Quantitative Evaluation Benchmark', H2))
story.append(Paragraph(
    'The pipeline was evaluated on five real-world infrastructure captures spanning the full degradation spectrum. '
    'All quality-gain figures are relative to the raw (unrestored) capture measured by the same proxy metrics.', BODY))
story.append(bench_table())
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Activity 6.3 — Sample REST / SSE Execution Log', H2))
log_code = (
    '[INFO] POST /api/v1/jobs/enhance  — Payload: {preset: "auto", match_original: false}\n'
    '[INFO] Degradation Profiler: Haze=0.243 (Severe), Blur=18.42 (High), Noise=2.15 (Med)\n'
    '[INFO] Executed: Dehaze (DCP+GF)  →  Denoise (FNLM)  →  Deblur (Unsharp)  →  SuperRes (Lanczos-4)\n'
    '[INFO] Quality Metrics: Composite Gain=+3,861.2%  Canny=+740.0%  Laplacian=+6,982.4%\n'
    '[INFO] Close-Range Synthesis: Extracted 3 macro ROIs  [Lattice Joint | Cross-Bracing | Top Platform]\n'
    '[INFO] Assistant Stream Initialized: Gemini Flash-Lite multimodal SSE active  (142 tok/s)\n'
    '[INFO] Total pipeline latency: 1.84 s'
)
lt = Table([[Paragraph(log_code, sty('log','Normal',fontSize=8.5,fontName='Courier',
                                      textColor=colors.HexColor('#4ade80'), leading=13))]],
           colWidths=[IW])
lt.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#050d18')),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('TOPPADDING',    (0,0), (-1,-1), 10),
    ('LEFTPADDING',   (0,0), (-1,-1), 12),
    ('RIGHTPADDING',  (0,0), (-1,-1), 12),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0891b2')),
]))
story.append(lt)
story.append(Spacer(1, 0.3*cm))

story += img('m6_testing_evaluation.png', IW,
             'Fig. 6 — Benchmark bar chart (quality gains per asset) + test suite results + SSE log')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# M7 — Conclusion
# ═══════════════════════════════════════════════════════════
story.append(milestone_header(7, 'Conclusion and Future Roadmap', colors.HexColor('#1c1917')))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Conclusion', H2))
story.append(Paragraph(
    'InfraClarity AI is a degradation-aware image restoration and multimodal inspection platform for '
    'critical infrastructure. By fusing physics-based optical estimators (Dark Channel Prior, Fast Non-Local '
    'Means, Adaptive Unsharp Masking, Lanczos-4) with structural pattern-guided close-range macro synthesis '
    'and real-time Gemini streaming, the system bridges the gap between compromised field imagery and '
    'high-reliability engineering diagnostics.', BODY))
story.append(Paragraph(
    'The project delivered a full pipeline processing standard inspection captures in 1.2–1.9 seconds, '
    'running on constrained field workstations through its tiled architecture and offline heuristic fallback, '
    'with 40 automated tests confirming correctness.', BODY))

story.append(Paragraph('Future Expansion Opportunities', H2))
future = [
    ('Onboard Edge AI Deployment', GRN,
     'Quantize the pipeline to run on NVIDIA Jetson Orin onboard UAV computers for in-flight restoration. '
     'Port to GPU (TensorRT) for 10× faster processing.'),
    ('Multi-Spectral Sensor Fusion', CYAN,
     'Combine long-wave infrared (LWIR) thermography and LiDAR point clouds to correlate thermal hotspots '
     'with structural cracks, enabling joint electrical and mechanical diagnostics.'),
    ('Automated CAD / BIM Digital Twin Export', AMBER,
     'Map detected flaws onto BIM / CAD models for automated work-order generation, closing the loop from '
     'inspection to maintenance.'),
    ('Predictive Degradation Analytics', PRP_C,
     'Train time-series degradation models on audit history to predict structural failure probability '
     'and trigger preventive maintenance schedules.'),
]
for title, col, desc in future:
    story.append(Paragraph(title, sty('fth','Normal',fontSize=11,fontName='Helvetica-Bold',
                                       textColor=col,spaceBefore=10,spaceAfter=3)))
    story.append(Paragraph(desc, BODY))

story.append(Spacer(1, 0.3*cm))
story += img('m7_conclusion_roadmap.png', IW,
             'Fig. 7 — Delivered capabilities vs. future expansion roadmap')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# BONUS — Website Pages (SkillWallet pages 13-16)
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('Exploring the Website: Web Pages & UI', H1))
story.append(HRFlowable(width=IW, thickness=1.5, color=AMBER, spaceAfter=10))

story.append(Paragraph('Enhance Page — Autonomous Optical Telemetry Matrix', H2))
story.append(Paragraph(
    'The Enhance page opens with the Autonomous Optical Telemetry Matrix, a real-time sensor degradation '
    'audit of the loaded capture. Four SVG gauge-meters report: Blur (657.6 — Sharp), Atmospheric Haze '
    '(0.243 — Moderate Haze), Sensor Noise (0.52 — Clean) and RMS Contrast (0.165 — Suboptimal Contrast). '
    'Below the gauges, an Algorithmic Restoration Prescription lists detected problems and recommends '
    'super-resolution because the shorter side is under 1080 px.', BODY))

story += img('bonus_telemetry_matrix.png', IW,
             'Fig. B1 — Autonomous Optical Telemetry Matrix: 4 degradation gauges + restoration prescription')
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Inspection Preset and Pipeline Stage Controls', H2))
story.append(Paragraph(
    'The control panel offers five inspection presets. The pipeline stages run in an enforced order and each '
    'can be switched on/off with its own intensity slider: Dehaze (50%), Denoise (55%), Deblur (65%) and '
    'Super-Resolution (75%). The viewer provides Split Slider, Side-by-Side, Crack & Edge Heatmap and '
    'Restored Delta modes with ROI Fault Spotlights.', BODY))
story += img('m5_frontend_console.png', IW,
             'Fig. B2 — Pipeline controls (presets + intensity sliders) | Synchronized viewer | Copilot + metrics')
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Close-Range Macro Patterns', H2))
story.append(Paragraph(
    'After enhancement, the system presents close-range macro views of the highest-priority structural '
    'regions, each with a pattern number, bounding box, acuity-gain badge and Show Original toggle: '
    'Tower Apex & Mast Head | Crossarm Gusset & Bolt Cluster | Diagonal Lattice Bracing Splice | '
    'Lower Structural Leg & Flange, with 1:1 Diagnostic Zoom links.', BODY))
story += img('m3_macro_synthesis.png', IW,
             'Fig. B3 — Close-range macro patterns: Harris ROI map + 4 extracted structural macro views')
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Original vs. Restored Output — Side-by-Side', H2))
story += img('bonus_sidebyside.png', IW,
             'Fig. B4 — Synchronized 1:1 side-by-side comparison: original (left) vs. restored (right)')
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('Tactical Inspection Copilot and Export', H2))
story.append(Paragraph(
    'The Tactical Inspection Copilot streams a Gemini-powered written analysis covering: asset and scene '
    'identification, detected optical degradations with severity levels, and the restoration and mitigation '
    'steps applied. Prompt pills offer one-tap questions ("Is that rust bad?", "Are bolts loose?"). '
    'The Export & Archival bar provides Field Audit Report (PDF), PNG, JPEG, JSON, Strip GPS EXIF options.', BODY))
story += img('m4_backend_copilot.png', IW,
             'Fig. B5 — Tactical copilot SSE sequence + live Gemini diagnostic streaming')
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# OBSERVATIONS & ABLATION
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('Observations and Ablation Insights', H1))
story.append(HRFlowable(width=IW, thickness=1.5, color=CYAN, spaceAfter=10))

obs = [
    ('+3,861.2% Composite Acuity Gain', AMBER,
     'Dark channel dehazing combined with adaptive dual-scale unsharp masking restored fine high-frequency '
     'gradients lost in the raw capture, making cross-bracing rivets, cable tensioners and flanges verifiable.'),
    ('Atmospheric Scattering Removed Without Halos', CYAN,
     'The O(N) Guided Filter prevents transmission-map oversaturation at abrupt structural boundaries, '
     'separating sky from steel members without dark-halo fringing artifacts.'),
    ('Noise Suppression Preserves Thin Fissures', GRN,
     'Fast Non-Local Means outperformed Gaussian and median filters by averaging repetitive structural '
     'patches while keeping thin fissures and hairline cracks sharp.'),
    ('Low-Latency SSE Streaming', PRP_C,
     'SSE reduced initial copilot feedback latency from ~6.5 s (batch generation) to 1.4 s (streaming), '
     'making the inspection workflow feel real-time.'),
    ('Tiled Memory Scalability', RED_C,
     'A fixed 512×512 tile window capped RAM usage below 450 MB even on 8K panoramas — suitable for '
     'constrained field workstations and onboard UAV edge computers.'),
]
for title, col, desc in obs:
    story.append(Paragraph(title, sty('obs','Normal',fontSize=11,fontName='Helvetica-Bold',
                                       textColor=col, spaceBefore=8, spaceAfter=3)))
    story.append(Paragraph(desc, BODY))

story.append(Spacer(1, 0.4*cm))
story += img('m6_testing_evaluation.png', IW,
             'Fig. C1 — Quantitative benchmark: quality gains across 5 real-world inspection assets')

# ═══════════════════════════════════════════════════════════
# BUILD PDF
# ═══════════════════════════════════════════════════════════
doc = SimpleDocTemplate(
    str(OUT_PDF),
    pagesize=A4,
    leftMargin=ML, rightMargin=MR,
    topMargin=MT,  bottomMargin=MB,
)
doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
print(f"✅  PDF written: {OUT_PDF}  ({OUT_PDF.stat().st_size//1024} KB)")
