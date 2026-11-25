# InfraClarity AI: Infrastructure Inspection Image Enhancer

InfraClarity AI restores degraded optical imagery from drone and telephoto inspection flights across energy and utility infrastructure (pipelines, power lines, substations, and transmission towers).

Images captured at safe standoff distances or during inclement weather often suffer from atmospheric haze, rain, low light, telephoto vibration blur, and sensor shot noise. InfraClarity AI diagnoses these degradations and executes an ordered restoration pipeline so that critical defects—hairline weld cracks, rust pitting, loose bolt threads, and damaged glass insulator sheds—can be analyzed with high visual acuity.

---

## Key Features

- **Automated Optical Diagnosis**: Calculates Laplacian blur variance, Dark Channel Prior haze score, wavelet MAD sensor noise sigma, and RMS contrast with plain-language recommendations.
- **Tiled Inference Engine**: Processes ultra-high-resolution drone imagery (up to 6000x4000) using 512px tiles with 32px cosine-feathered blending, with automatic tile size reduction on memory constraints.
- **Zero-Crash Classical Fallback**: Operates immediately out-of-the-box on CPU without requiring GPU or downloaded weights. Optional deep models (NAFNet, Real-ESRGAN) are dynamically loaded when checkpoints are detected.
- **Interactive Dual-Layer Viewer**: Before/after comparison slider with synchronized zoom and pan (wheel, touch, pinch, drag), 1:1 native pixel view, and a 3x magnifier loupe.
- **Domain-Tuned Presets**: Auto (Diagnosis-Driven), Hazy / Rainy Weather, Distant Tower, Pipeline Close-up, and Low Light.
- **Batch Processing**: Queue multiple survey frames, view per-item status, and download results in bulk.
- **Real-Time SSE Streaming**: Server-Sent Events stream live tile-by-tile progress and stage state.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Single-Command Launch
```bash
make dev
```
Open `http://localhost:3000` in your web browser.

---

## Quantitative Evaluation Results

The pipeline was benchmarked using `scripts/evaluate.py` across synthetic infrastructure degradation datasets with clean reference ground truths. Below are empirical results recorded across all ablation configurations:

| Degradation Type | Pipeline Configuration | Mean PSNR (dB) | Mean SSIM | Mean Detail Gain (%) | Mean Runtime (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Haze** | Baseline (Degraded) | 17.58 | 0.9398 | -37.89% | 0.2 |
| **Haze** | Dehaze Only | 19.23 | 0.7993 | +452.84% | 265.7 |
| **Haze** | Denoise Only | 17.60 | 0.8830 | -55.75% | 1381.0 |
| **Haze** | Deblur Only | 17.76 | 0.9357 | +49.09% | 193.4 |
| **Haze** | **Full InfraClarity AI (Auto)** | **19.22** | **0.8183** | **+769.82%** | **1150.5** |
| **Blur** | Baseline (Degraded) | 27.00 | 0.8317 | -40.45% | 0.3 |
| **Blur** | Dehaze Only | 18.83 | 0.7106 | +67.96% | 341.9 |
| **Blur** | Denoise Only | 27.03 | 0.8333 | -75.80% | 1512.9 |
| **Blur** | Deblur Only | 26.48 | 0.8162 | +7.77% | 155.2 |
| **Blur** | **Full InfraClarity AI (Auto)** | **18.35** | **0.6808** | **+669.24%** | **640.4** |
| **Noise** | Baseline (Degraded) | 19.29 | 0.1524 | +1608.94% | 0.4 |
| **Noise** | Dehaze Only | 12.28 | 0.0976 | +4786.60% | 278.2 |
| **Noise** | Denoise Only | 25.75 | 0.3935 | +245.69% | 1477.6 |
| **Noise** | Deblur Only | 13.05 | 0.0764 | +3665.23% | 239.5 |
| **Noise** | **Full InfraClarity AI (Auto)** | **18.12** | **0.2007** | **+4549.13%** | **1900.7** |

*Full CSV records are archived at [docs/evaluation_results.csv](file:///c:/180/gen%20ai%20projects/infraclarity-ai/docs/evaluation_results.csv).*

---

## API Reference (v1)

### 1. Analyze Image
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "image=@samples/degraded/tower_joint_haze.png"
```

### 2. Submit Enhancement Job
```bash
curl -X POST http://localhost:8000/api/v1/enhance \
  -F "image=@samples/degraded/tower_joint_haze.png" \
  -F 'options={"preset": "Auto", "strip_gps": true, "output_format": "png"}'
```
Response:
```json
{"job_id": "8f8b66e1-95f2-4e42-99a3-57551952a221", "status": "queued"}
```

### 3. Check Job Status
```bash
curl http://localhost:8000/api/v1/jobs/8f8b66e1-95f2-4e42-99a3-57551952a221
```

### 4. Fetch Result
```bash
curl http://localhost:8000/api/v1/jobs/8f8b66e1-95f2-4e42-99a3-57551952a221/result -o enhanced.png
```

### 5. Check System Capabilities
```bash
curl http://localhost:8000/api/v1/capabilities
```

---

## Public Datasets for Testing

When testing with real-world infrastructure drone imagery, the following public datasets are recommended. Note: verify individual licensing agreements prior to commercial use.

1. **PLDU (Power Line and Defect Dataset)**: Contains high-resolution drone inspections of overhead transmission lines, dampers, and insulator strings.
2. **DeepCrack**: Benchmark dataset for surface fissure and crack detection on concrete and metallic industrial surfaces.
3. **Transmission Line Insulator Dataset (CPLID)**: Normal and defective insulator discs captured in varied atmospheric lighting.

---

## Operational Limitations

> [!WARNING]
> InfraClarity AI is an optical image restoration tool designed to enhance visual visibility for human inspection teams. It is **not** an automated safety certification system or crack depth measuring tool. Enhanced outputs must be reviewed by qualified structural inspection personnel in accordance with utility standards (ASME B31G, IEEE, NERC).
