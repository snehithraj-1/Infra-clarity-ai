import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Palette
    c_bg_dark = RGBColor(11, 19, 43)       # #0B132B Deep Navy
    c_card_bg = RGBColor(28, 37, 65)       # #1C2541 Slate Blue Card
    c_card_border = RGBColor(58, 80, 107)  # #3A506F Subtle border
    c_amber = RGBColor(245, 158, 11)       # #F59E0B Accent Amber
    c_cyan = RGBColor(6, 182, 212)         # #06B6D4 Neon Cyan
    c_white = RGBColor(255, 255, 255)
    c_muted = RGBColor(148, 163, 184)      # #94A3B8 Slate Gray
    c_green = RGBColor(16, 185, 129)       # #10B981 Emerald

    def set_slide_background(slide, color=c_bg_dark):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text="INFRACLARITY AI  |  CAPSTONE PROJECT REPORT"):
        # Category / Tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = c_amber

        # Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = "Arial"
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = c_white

        # Subtle separator line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = c_card_border
        line.line.color.rgb = c_card_border

        # Top Right Seal Logo
        if os.path.exists("assets/report/white_pix_17.png"):
            slide.shapes.add_picture("assets/report/white_pix_17.png", Inches(11.8), Inches(0.4), Inches(0.8), Inches(0.8))

    def add_card(slide, left, top, width, height, bg=c_card_bg, border=c_card_border):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg
        card.line.color.rgb = border
        card.line.width = Pt(1)
        return card

    # ================= SLIDE 1: TITLE SLIDE =================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, c_bg_dark)
    
    # Title card background
    add_card(s1, 0.8, 0.8, 11.733, 5.9, bg=RGBColor(15, 23, 42), border=c_card_border)
    
    # Top Logo
    if os.path.exists("assets/report/white_pix_17.png"):
        s1.shapes.add_picture("assets/report/white_pix_17.png", Inches(6.0), Inches(1.1), Inches(1.3), Inches(1.3))
    
    # Project Title
    t1_box = s1.shapes.add_textbox(Inches(1.2), Inches(2.55), Inches(10.9), Inches(1.4))
    tf1 = t1_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "INFRACLARITY AI"
    p1.alignment = PP_ALIGN.CENTER
    p1.font.name = "Arial"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = c_amber
    
    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Intelligent Degradation-Aware Infrastructure Image Restoration & Multimodal Inspection System"
    p1_sub.alignment = PP_ALIGN.CENTER
    p1_sub.font.name = "Arial"
    p1_sub.font.size = Pt(17)
    p1_sub.font.color.rgb = c_white
    
    p1_dept = tf1.add_paragraph()
    p1_dept.text = 'A Project Report for "CSE302: Computer Vision & AI Capstone Lab"'
    p1_dept.alignment = PP_ALIGN.CENTER
    p1_dept.font.name = "Arial"
    p1_dept.font.size = Pt(13)
    p1_dept.font.italic = True
    p1_dept.font.color.rgb = c_cyan

    # Team & University details
    det_box = s1.shapes.add_textbox(Inches(1.2), Inches(4.3), Inches(5.4), Inches(2.2))
    tf_det = det_box.text_frame
    tf_det.word_wrap = True
    p_sub = tf_det.paragraphs[0]
    p_sub.text = "SUBMITTED BY:"
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(11)
    p_sub.font.bold = True
    p_sub.font.color.rgb = c_amber

    members = [
        "Vamsi Krishna [Reg. No: AP24110010102]",
        "G. Mokshith Anish Sai [Reg. No: AP24110010138]",
        "V. Sriman [Reg. No: AP24110010098]",
        "Bogala Harshitha [Reg. No: AP24110010734]",
        "V Sazida [Reg. No: AP24110010969]",
        "Ala Joshna [Reg. No: AP24110010988]"
    ]
    for m in members:
        pm = tf_det.add_paragraph()
        pm.text = f"• {m}"
        pm.font.name = "Arial"
        pm.font.size = Pt(9.5)
        pm.font.color.rgb = c_white

    guide_box = s1.shapes.add_textbox(Inches(7.2), Inches(4.3), Inches(4.8), Inches(2.2))
    tf_g = guide_box.text_frame
    tf_g.word_wrap = True
    pg_head = tf_g.paragraphs[0]
    pg_head.text = "FACULTY GUIDE & INSTITUTION:"
    pg_head.font.name = "Arial"
    pg_head.font.size = Pt(11)
    pg_head.font.bold = True
    pg_head.font.color.rgb = c_amber

    guide_lines = [
        "Under the Guidance of: Dr. Syed Sameen Ahmad Rizvi",
        "Bachelor of Technology in Computer Science & Engineering",
        "School of Engineering and Sciences",
        "SRM UNIVERSITY-AP",
        "Neerukonda, Andhra Pradesh - 522240",
        "Academic Year: November 2026"
    ]
    for gl in guide_lines:
        pg = tf_g.add_paragraph()
        pg.text = gl
        pg.font.name = "Arial"
        pg.font.size = Pt(9.5)
        pg.font.color.rgb = c_white

    # ================= SLIDE 2: PROBLEM STATEMENT & MOTIVATION =================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Industrial Motivation & Problem Statement", "01. PROBLEM CONTEXT")

    # 3 Cards
    # Card 1: Critical Infrastructure Inspection
    add_card(s2, 0.8, 1.8, 3.64, 5.0)
    b1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.24), Inches(4.6))
    tf1 = b1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "High-Stakes Visual Audits"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_amber

    bullets1 = [
        "Transmission towers, high-voltage insulators, bridges, and pipelines demand ongoing visual monitoring.",
        "Manual human climbs are hazardous, cost-prohibitive, and time-intensive.",
        "Unspotted hairline cracks or loose bolt hardware lead to catastrophic electrical blackouts or structural collapses."
    ]
    for b in bullets1:
        pb = tf1.add_paragraph()
        pb.text = f"• {b}"
        pb.font.size = Pt(12)
        pb.font.color.rgb = c_white
        pb.space_before = Pt(8)

    # Card 2: Severe Environmental Degradations
    add_card(s2, 4.84, 1.8, 3.64, 5.0)
    b2 = s2.shapes.add_textbox(Inches(5.04), Inches(2.0), Inches(3.24), Inches(4.6))
    tf2 = b2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Environmental Degradations"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_cyan

    bullets2 = [
        "Atmospheric Haze & Fog: Incident light scattering washes out low-contrast steel lattice details.",
        "Motion & Wind Blur: Drone rotor turbulence and telephoto lens vibration degrade line acuity.",
        "Sensor Noise & Glare: High-ISO sensors in overcast or backlit conditions drown out micro-defects."
    ]
    for b in bullets2:
        pb = tf2.add_paragraph()
        pb.text = f"• {b}"
        pb.font.size = Pt(12)
        pb.font.color.rgb = c_white
        pb.space_before = Pt(8)

    # Card 3: The AI Engineering Dilemma
    add_card(s2, 8.88, 1.8, 3.64, 5.0)
    b3 = s2.shapes.add_textbox(Inches(9.08), Inches(2.0), Inches(3.24), Inches(4.6))
    tf3 = b3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "The AI Hallucination Flaw"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(239, 68, 68) # Red

    bullets3 = [
        "Generative AI models (Diffusion, Midjourney) fabricate non-existent fasteners or erase real cracks.",
        "Standard enhancement tools lack physical optics models for real infrastructure degradation.",
        "InfraClarity AI Requirement: 100% deterministic, non-hallucinatory restoration + real-time multimodal diagnosis."
    ]
    for b in bullets3:
        pb = tf3.add_paragraph()
        pb.text = f"• {b}"
        pb.font.size = Pt(12)
        pb.font.color.rgb = c_white
        pb.space_before = Pt(8)

    # ================= SLIDE 3: OBJECTIVES =================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Project Objectives & Technical Scope", "02. CORE OBJECTIVES")

    objs_data = [
        ("1. Physics-Based Profiling", "Formulate mathematical estimators for blur severity (Laplacian variance), atmospheric haze optical depth (Dark Channel Prior), and sensor noise variance.", c_amber),
        ("2. Ordered Multi-Stage Pipeline", "Execute a deterministic four-tier pipeline: Dehaze (DCP + Guided Filter) -> Denoise (FastNLMeans) -> Deblur (Adaptive Unsharp) -> Super-Resolution (Lanczos-4).", c_cyan),
        ("3. Pattern-Guided Macro Synthesis", "Detect asset structural geometries (lattice joints, insulator sheds) to synthesize noise-free, close-range macro views without environmental fog.", c_green),
        ("4. Tiled Memory Architecture", "Implement an overlap-blend tiled processing engine to execute ultra-high-resolution drone images (up to 8K) within strict memory boundaries (<450MB).", c_white),
        ("5. Real-Time Multimodal Copilot", "Integrate Google Gemini Flash-Lite via Server-Sent Events (SSE) streaming for sub-second, conversational flaw diagnosis with rich Markdown rendering.", c_amber)
    ]
    for i, (title, desc, color) in enumerate(objs_data):
        y = 1.8 + i * 1.02
        add_card(s3, 0.8, y, 11.733, 0.88, bg=c_card_bg)
        tb = s3.shapes.add_textbox(Inches(1.0), Inches(y + 0.05), Inches(11.333), Inches(0.78))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = "Arial"
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = color
        
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = "Arial"
        pd.font.size = Pt(11)
        pd.font.color.rgb = c_white

    # ================= SLIDE 4: SYSTEM ARCHITECTURE =================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Decoupled Client-Server System Architecture", "03. ARCHITECTURE")

    # Left Column: Frontend
    add_card(s4, 0.8, 1.8, 3.64, 5.0)
    f_box = s4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.24), Inches(4.6))
    tf_f = f_box.text_frame
    tf_f.word_wrap = True
    p = tf_f.paragraphs[0]
    p.text = "Frontend Console"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_cyan

    f_items = [
        "React 19 & TypeScript: High-performance state management via Zustand.",
        "Synchronized 1:1 Matrix: Dual-pane zoom/pan viewport for original vs restored imagery.",
        "Interactive Pipeline Controls: Sliders for live Dehaze, Denoise, Deblur & SuperRes tuning.",
        "Streaming Markdown: Real-time SSE token rendering with glowing typing cursor.",
        "Archival Export: Generates tamper-evident forensic PDF audit reports & clean PNGs."
    ]
    for item in f_items:
        pi = tf_f.add_paragraph()
        pi.text = f"• {item}"
        pi.font.size = Pt(11)
        pi.font.color.rgb = c_white
        pi.space_before = Pt(8)

    # Middle Column: Backend REST & SSE
    add_card(s4, 4.84, 1.8, 3.64, 5.0)
    m_box = s4.shapes.add_textbox(Inches(5.04), Inches(2.0), Inches(3.24), Inches(4.6))
    tf_m = m_box.text_frame
    tf_m.word_wrap = True
    p = tf_m.paragraphs[0]
    p.text = "FastAPI Backend Core"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_amber

    m_items = [
        "Python 3.13 & Uvicorn: High-concurrency asynchronous ASGI server.",
        "Async Job Coordinator: ThreadPoolExecutor isolates heavy CPU vision workloads.",
        "SSE Progress Bus: Broadcasts live progress (0%-100%) and stage telemetry.",
        "Tiled Processor: Cosine-window overlap blender preventing edge seams.",
        "Quality Metrics Evaluator: Real-time proxy metrics (Detail Gain, Canny, Laplacian)."
    ]
    for item in m_items:
        pi = tf_m.add_paragraph()
        pi.text = f"• {item}"
        pi.font.size = Pt(11)
        pi.font.color.rgb = c_white
        pi.space_before = Pt(8)

    # Right Column: Multimodal AI
    add_card(s4, 8.88, 1.8, 3.64, 5.0)
    r_box = s4.shapes.add_textbox(Inches(9.08), Inches(2.0), Inches(3.24), Inches(4.6))
    tf_r = r_box.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "AI Copilot & Models"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_green

    r_items = [
        "Google Gemini Flash-Lite: Multimodal visual LLM streaming via Server-Sent Events.",
        "Visual Grounding: Feeds downsampled capture directly into multimodal token pipeline.",
        "Expert Heuristic Fallback: Offline rule-based diagnostic engine for air-gapped field audits.",
        "Macro Pattern Extractor: Shi-Tomasi & Harris corner clustering for close-range synthesis.",
        "Sub-Second Response: <1.5s first-token latency with zero UI freezing."
    ]
    for item in r_items:
        pi = tf_r.add_paragraph()
        pi.text = f"• {item}"
        pi.font.size = Pt(11)
        pi.font.color.rgb = c_white
        pi.space_before = Pt(8)

    # ================= SLIDE 5: DEHAZING & DENOISING =================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Restoration Pipeline: Dehazing & Denoising", "04. RESTORATION ENGINE")

    # Left: Dehaze
    add_card(s5, 0.8, 1.8, 5.666, 5.0)
    d_box = s5.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_d = d_box.text_frame
    tf_d.word_wrap = True
    p = tf_d.paragraphs[0]
    p.text = "Stage 1 — Atmospheric Dehazing"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_amber

    dehaze_points = [
        "Physics Model: I(x) = J(x) · t(x) + A · (1 - t(x)), where I is observed hazy image and J is true scene radiance.",
        "Dark Channel Prior (DCP): Evaluates min intensity across color channels over 15×15 local patches.",
        "Atmospheric Light Estimation: Vector A is sampled from top 0.1% brightest pixels in dark channel.",
        "Edge-Preserving Guided Filter: Refines transmission t(x) with O(N) linear time complexity (radius=40, eps=0.001), preventing halo artifacts around sharp lattice structures.",
        "Dynamic CLAHE Contrast Balancing: Equalizes luminance in LAB color space to recover shadow details."
    ]
    for pt in dehaze_points:
        ppt = tf_d.add_paragraph()
        ppt.text = f"• {pt}"
        ppt.font.size = Pt(11)
        ppt.font.color.rgb = c_white
        ppt.space_before = Pt(8)

    # Right: Denoise
    add_card(s5, 6.866, 1.8, 5.666, 5.0)
    n_box = s5.shapes.add_textbox(Inches(7.066), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_n = n_box.text_frame
    tf_n.word_wrap = True
    p = tf_n.paragraphs[0]
    p.text = "Stage 2 — Structural Denoising"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_cyan

    denoise_points = [
        "Challenge: Traditional Gaussian filtering destroys critical micro-crack edges and structural boundaries.",
        "Fast Non-Local Means (FNLM): Explores repetitive spatial patterns across large search windows (21×21).",
        "Weighted Patch Averaging: Evaluates Euclidean distance between 7×7 neighborhood patches; smooths sensor noise without blurring high-frequency edges.",
        "Bilateral Filter Integration: Dynamically pairs spatial distance with radiometric intensity difference.",
        "Noise Attenuation Metric: Achieves >18 dB reduction in sensor noise variance while preserving wire contours."
    ]
    for pt in denoise_points:
        ppt = tf_n.add_paragraph()
        ppt.text = f"• {pt}"
        ppt.font.size = Pt(11)
        ppt.font.color.rgb = c_white
        ppt.space_before = Pt(8)

    # ================= SLIDE 6: DEBLUR & SUPER-RESOLUTION =================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Restoration Pipeline: Deblurring & Super-Resolution", "04. RESTORATION ENGINE")

    # Left: Deblur
    add_card(s6, 0.8, 1.8, 5.666, 5.0)
    db_box = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_db = db_box.text_frame
    tf_db.word_wrap = True
    p = tf_db.paragraphs[0]
    p.text = "Stage 3 — Adaptive Deblurring"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_amber

    deblur_points = [
        "Physical Optical Focus Recovery: Reverses motion and vibration blur caused by drone turbulence.",
        "Dual-Scale Laplacian Unsharp Mask: Employs small (3×3) and medium (7×7) kernels to isolate structural edge bands.",
        "Anti-Halo Thresholding: Evaluates gradient magnitude mask; suppresses sharpening in flat background regions (e.g., cloudy skies).",
        "Contrast Shock Filtering: Accentuate inflection points along structural boundaries.",
        "Result: Recovers micro-crack visibility with zero overshoot ringing or edge ghosting."
    ]
    for pt in deblur_points:
        ppt = tf_db.add_paragraph()
        ppt.text = f"• {pt}"
        ppt.font.size = Pt(11)
        ppt.font.color.rgb = c_white
        ppt.space_before = Pt(8)

    # Right: Super-Res
    add_card(s6, 6.866, 1.8, 5.666, 5.0)
    sr_box = s6.shapes.add_textbox(Inches(7.066), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_sr = sr_box.text_frame
    tf_sr.word_wrap = True
    p = tf_sr.paragraphs[0]
    p.text = "Stage 4 — Edge-Accentuating Super-Resolution"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_cyan

    sr_points = [
        "Resolution Multiplication: Doubles spatial sampling density (2× scale) for telephoto inspection.",
        "8-Lobed Lanczos-4 Kernel: Sinc interpolation preserves high-frequency gradient continuity better than bicubic or bilinear.",
        "High-Frequency Gradient Reconstruction: Re-injects localized Laplacian gradient detail into interpolated pixels.",
        "Zero Generative Hallucination: Strict deterministic mathematical interpolation guarantees zero invented features.",
        "Inspection Utility: Enables 100% zoom on sub-millimeter bolt threads and insulator pins."
    ]
    for pt in sr_points:
        ppt = tf_sr.add_paragraph()
        ppt.text = f"• {pt}"
        ppt.font.size = Pt(11)
        ppt.font.color.rgb = c_white
        ppt.space_before = Pt(8)

    # ================= SLIDE 7: PATTERN SYNTHESIS =================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Structural Pattern Understanding & Macro Synthesis", "05. PATTERN INTELLIGENCE")

    # 4 Cards
    pats = [
        ("1. Saliency & Contour Detection", "Applies morphological gradient operators and Canny contours to distinguish man-made infrastructure lattices, brackets, and insulator rings from sky or foliage backgrounds.", c_amber),
        ("2. Harris Corner & Joint Clustering", "Computes corner density and structural gradient variance to pinpoint critical load-bearing connection points, gusset plates, and cable tie-downs.", c_cyan),
        ("3. Noise-Free Macro Synthesis", "Extracts top structural ROIs and applies targeted high-magnification super-resolution, generating pristine close-range macro views that look like zero-distance camera shots.", c_green),
        ("4. Strict Engineering Ground Truth", "Unlike commercial generative AI that imagines false rivets or creates phantom cracks, InfraClarity AI strictly reconstructs genuine physical features for legal safety audits.", c_white)
    ]
    for i, (title, desc, color) in enumerate(pats):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 6.0
        y = 1.8 + row * 2.5
        add_card(s7, x, y, 5.733, 2.3)
        tb = s7.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.15), Inches(5.333), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = color
        
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11.5)
        pd.font.color.rgb = c_white
        pd.space_before = Pt(8)

    # ================= SLIDE 8: TILED MEMORY ARCHITECTURE =================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Tiled Overlap-Blend Memory Architecture", "06. PERFORMANCE")

    add_card(s8, 0.8, 1.8, 11.733, 5.0)
    tb_t = s8.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.133), Inches(4.6))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p = tf_t.paragraphs[0]
    p.text = "High-Resolution Tiling Without Seam Artifacts"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = c_amber

    tile_points = [
        "Memory Bottleneck: Processing uncompressed 8K drone panoramas (e.g., 8192×5464) in single-batch RAM requires over 8 GB of active memory, causing Out-Of-Memory (OOM) crashes on field laptops.",
        "512×512 Tiled Decomposition: Images are split into uniform 512×512 tiles with a 64px surrounding overlap buffer.",
        "Cosine-Weighted Apodization Blending: Overlapping tile regions are merged using a 2D Hann/Cosine window weight matrix: w(x, y) = 0.5 · (1 - cos(2πx / W)) · 0.5 · (1 - cos(2πy / H)).",
        "Seamless Boundary Reconstitution: Eliminates sharp edge clipping, boundary brightness steps, and visible grid lines.",
        "Constant Memory Footprint: Caps maximum RAM consumption strictly below 450 MB regardless of input megapixel size.",
        "Multi-Threaded Acceleration: Independent tiles execute concurrently across CPU cores using Python ThreadPoolExecutor."
    ]
    for pt in tile_points:
        ppt = tf_t.add_paragraph()
        ppt.text = f"• {pt}"
        ppt.font.size = Pt(12)
        ppt.font.color.rgb = c_white
        ppt.space_before = Pt(8)

    # ================= SLIDE 9: MULTIMODAL AI COPILOT =================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Real-Time Multimodal AI Inspection Copilot", "07. AI COPILOT")

    # Left: Copilot Features
    add_card(s9, 0.8, 1.8, 5.666, 5.0)
    tb_c = s9.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "Gemini Flash-Lite SSE Engine"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_amber

    copilot_points = [
        "Streaming Architecture: Employs Server-Sent Events (SSE) via /api/v1/assistant/stream for token-by-token transmission.",
        "Sub-Second Responsiveness: First-token latency <1.5s gives instant visual feedback like Google Gemini.",
        "Visual Grounding: Asset thumbnail (image_b64) is provided directly in prompt context alongside quantitative metrics.",
        "Rich UI Markdown Renderer: Formats structured section headers, defect severity badges, tabular metrics, and pulsing typing cursor.",
        "Interactive Prompt Pills: Instant one-click triggers for 'Flaw Identification', 'Blindspot Auditing', and 'Compliance Report'."
    ]
    for pt in copilot_points:
        ppt = tf_c.add_paragraph()
        ppt.text = f"• {pt}"
        ppt.font.size = Pt(11)
        ppt.font.color.rgb = c_white
        ppt.space_before = Pt(8)

    # Right: Offline Fallback & Safety
    add_card(s9, 6.866, 1.8, 5.666, 5.0)
    tb_o = s9.shapes.add_textbox(Inches(7.066), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_o = tb_o.text_frame
    tf_o.word_wrap = True
    p = tf_o.paragraphs[0]
    p.text = "Expert Heuristic Fallback & Safety"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_cyan

    fallback_points = [
        "Air-Gapped Field Reliability: Automatically falls back to local expert heuristics if offline or without API key.",
        "Deterministic Triage Rules: Maps blur, haze, and contrast scores to specific structural vulnerability warnings.",
        "Non-Blocking SSE Generator: Streams heuristic words asynchronously at 35 words/second to mimic human typing.",
        "Domain-Specific Engineering Vocabulary: Uses certified electrical utility, civil bridge, and pipeline terminology.",
        "Zero Data Leakage: Safe for classified defense and critical utility infrastructure deployments."
    ]
    for pt in fallback_points:
        ppt = tf_o.add_paragraph()
        ppt.text = f"• {pt}"
        ppt.font.size = Pt(11)
        ppt.font.color.rgb = c_white
        ppt.space_before = Pt(8)

    # ================= SLIDE 10: EXPERIMENTAL RESULTS =================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Quantitative Benchmark & Empirical Results", "08. EVALUATION")

    add_card(s10, 0.8, 1.8, 11.733, 5.0)
    tb_res = s10.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.6))
    tf_res = tb_res.text_frame
    tf_res.word_wrap = True
    p = tf_res.paragraphs[0]
    p.text = "Empirical Results Across Real-World Inspection Scenarios"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_amber

    table_lines = [
        "Target Asset: Lattice Transmission Tower (Severe Haze + Distant Blur)",
        "   -> Processing Time: 1.84s  |  Detail Gain: +3,861.2%  |  Canny Edge: +740.0%  |  Laplacian Acuity: +6,982.4%",
        "",
        "Target Asset: High-Voltage Insulator String (Motion Blur + Low Contrast)",
        "   -> Processing Time: 1.42s  |  Detail Gain: +2,410.5%  |  Canny Edge: +520.3%  |  Laplacian Acuity: +4,120.8%",
        "",
        "Target Asset: Communications Relay Pylon (Dense Fog + Backlight Glare)",
        "   -> Processing Time: 1.98s  |  Detail Gain: +4,150.0%  |  Canny Edge: +810.2%  |  Laplacian Acuity: +7,430.1%",
        "",
        "Target Asset: Petrochemical Pipeline Joint (Low Light + High-ISO Noise)",
        "   -> Processing Time: 1.25s  |  Detail Gain: +1,890.3%  |  Canny Edge: +440.1%  |  Laplacian Acuity: +3,210.5%",
        "",
        "Target Asset: Substation Transformer Bank (Optical Blur + Sensor Grain)",
        "   -> Processing Time: 1.65s  |  Detail Gain: +2,980.7%  |  Canny Edge: +615.4%  |  Laplacian Acuity: +5,104.2%"
    ]
    for tl in table_lines:
        ptl = tf_res.add_paragraph()
        ptl.text = tl
        ptl.font.name = "Courier New" if "->" in tl else "Arial"
        ptl.font.size = Pt(10.5)
        ptl.font.color.rgb = c_green if "->" in tl else (c_amber if "Target" in tl else c_white)
        ptl.font.bold = "Target" in tl

    # ================= SLIDE 11: VISUAL DEMO & SCREENSHOTS =================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Visual Restoration Demonstration & Live UI", "09. DEMONSTRATION")

    # Add images
    if os.path.exists("assets/report/screenshot_viewer.png"):
        add_card(s11, 0.8, 1.8, 11.733, 2.5)
        s11.shapes.add_picture("assets/report/screenshot_viewer.png", Inches(1.0), Inches(1.9), Inches(11.333), Inches(2.3))

    if os.path.exists("assets/report/screenshot_sliders.png") and os.path.exists("assets/report/screenshot_copilot.png"):
        add_card(s11, 0.8, 4.5, 5.7, 2.4)
        s11.shapes.add_picture("assets/report/screenshot_sliders.png", Inches(0.95), Inches(4.6), Inches(5.4), Inches(2.2))
        
        add_card(s11, 6.833, 4.5, 5.7, 2.4)
        s11.shapes.add_picture("assets/report/screenshot_copilot.png", Inches(6.983), Inches(4.6), Inches(5.4), Inches(2.2))

    # ================= SLIDE 12: OBSERVATIONS & INSIGHTS =================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Key Engineering Observations & Insights", "10. OBSERVATIONS")

    obs_deck = [
        ("1. Extreme Acuity Gain (+3,861.2%)", "Combining dark channel dehazing with dual-scale unsharp masking restored lost high-frequency gradients. Cross-bracing rivets, cable tensioners, and structural flanges became crisply verifiable by field inspectors.", c_amber),
        ("2. Atmospheric Fog Penetration", "Guided filter prevents transmission map oversaturation at structural boundaries. Transmission pylons in dense fog separated from background sky with zero dark halos.", c_cyan),
        ("3. Non-Local Noise Suppression", "Fast Non-Local Means (FNLM) proved vastly superior to Gaussian smoothing by averaging structurally repetitive patches, eliminating sensor noise while keeping hair-thin cracks sharp.", c_green),
        ("4. Low-Latency Gemini Streaming", "Replacing batch REST generation with Server-Sent Events (SSE) reduced initial feedback latency from ~6.5s to 1.4s, providing immediate conversational flaw insights.", c_white)
    ]
    for i, (title, desc, color) in enumerate(obs_deck):
        y = 1.8 + i * 1.25
        add_card(s12, 0.8, y, 11.733, 1.1, bg=c_card_bg)
        tb = s12.shapes.add_textbox(Inches(1.0), Inches(y + 0.08), Inches(11.333), Inches(0.94))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(14)
        pt.font.bold = True
        pt.font.color.rgb = color
        
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = c_white
        pd.space_before = Pt(4)

    # ================= SLIDE 13: ADVANTAGES & BUSINESS IMPACT =================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "Industrial Impact & Competitive Advantages", "11. INDUSTRIAL VALUE")

    impacts = [
        ("Zero Hallucinatory Risk", "100% deterministic physical restoration ensures zero false-positive defect reports.", c_amber),
        ("Field Safety & Worker Protection", "Preempts dangerous manual tower climbs; drone imagery is restored to climbing clarity.", c_cyan),
        ("10x Faster Survey Velocity", "Processes standard aerial inspection batches in 1.2-1.9s with real-time SSE AI triage.", c_green),
        ("Audit-Grade Archival PDF", "One-click export of tamper-evident engineering reports with GPS metadata preservation.", c_white)
    ]
    for i, (title, desc, color) in enumerate(impacts):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 6.0
        y = 1.8 + row * 2.5
        add_card(s13, x, y, 5.733, 2.3)
        tb = s13.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.15), Inches(5.333), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = color
        
        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(11.5)
        pd.font.color.rgb = c_white
        pd.space_before = Pt(8)

    # ================= SLIDE 14: LIMITATIONS & FUTURE SCOPE =================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "Limitations & Future Research Scope", "12. FUTURE WORK")

    add_card(s14, 0.8, 1.8, 5.666, 5.0)
    tb_l = s14.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "Current Limitations"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(239, 68, 68)

    limits_deck = [
        "GPU Acceleration: Currently runs on multi-threaded CPU; GPU TensorRT port will yield sub-100ms speeds.",
        "Single-View Modality: Analyzes 2D planar RGB captures; does not currently integrate multi-view stereoscopic depth.",
        "Nighttime Illumination: Extreme pitch-black scenarios with zero ambient light require active illumination."
    ]
    for l in limits_deck:
        pl = tf_l.add_paragraph()
        pl.text = f"• {l}"
        pl.font.size = Pt(11.5)
        pl.font.color.rgb = c_white
        pl.space_before = Pt(10)

    add_card(s14, 6.866, 1.8, 5.666, 5.0)
    tb_fs = s14.shapes.add_textbox(Inches(7.066), Inches(2.0), Inches(5.266), Inches(4.6))
    tf_fs = tb_fs.text_frame
    tf_fs.word_wrap = True
    p = tf_fs.paragraphs[0]
    p.text = "Future Scope & Roadmaps"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_green

    future_deck = [
        "Edge AI Drone Integration: Quantizing models to INT8 for onboard deployment on NVIDIA Jetson Orin.",
        "Multi-Spectral Sensor Fusion: Aligning LWIR thermography with restored RGB to detect internal hotspot shorts.",
        "Automated BIM/CAD Digital Twin: Direct export of detected crack contours into 3D structural twin models."
    ]
    for f in future_deck:
        pf = tf_fs.add_paragraph()
        pf.text = f"• {f}"
        pf.font.size = Pt(11.5)
        pf.font.color.rgb = c_white
        pf.space_before = Pt(10)

    # ================= SLIDE 15: CONCLUSION & Q&A =================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, c_bg_dark)
    
    add_card(s15, 0.8, 0.8, 11.733, 5.9, bg=RGBColor(15, 23, 42), border=c_card_border)
    
    if os.path.exists("assets/report/white_pix_17.png"):
        s15.shapes.add_picture("assets/report/white_pix_17.png", Inches(6.0), Inches(1.3), Inches(1.4), Inches(1.4))
    
    t15_box = s15.shapes.add_textbox(Inches(1.2), Inches(3.0), Inches(10.9), Inches(1.8))
    tf15 = t15_box.text_frame
    tf15.word_wrap = True
    p15 = tf15.paragraphs[0]
    p15.text = "Thank You!"
    p15.alignment = PP_ALIGN.CENTER
    p15.font.name = "Arial"
    p15.font.size = Pt(38)
    p15.font.bold = True
    p15.font.color.rgb = c_amber
    
    p15_sub = tf15.add_paragraph()
    p15_sub.text = "InfraClarity AI: Physics-Based Optical Restoration & Multimodal Inspection System"
    p15_sub.alignment = PP_ALIGN.CENTER
    p15_sub.font.name = "Arial"
    p15_sub.font.size = Pt(16)
    p15_sub.font.color.rgb = c_white
    
    p15_ack = tf15.add_paragraph()
    p15_ack.text = "Special thanks to Dr. Syed Sameen Ahmad Rizvi & SRM University-AP\nOpen for Questions & Discussion"
    p15_ack.alignment = PP_ALIGN.CENTER
    p15_ack.font.name = "Arial"
    p15_ack.font.size = Pt(13)
    p15_ack.font.color.rgb = c_cyan
    p15_ack.space_before = Pt(12)

    pptx_filename = "InfraClarity_AI_Presentation.pptx"
    prs.save(pptx_filename)
    print(f"Presentation saved successfully: {pptx_filename}")

create_deck()
