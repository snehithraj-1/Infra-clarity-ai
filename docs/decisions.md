# Decisions Log

## Architecture & Framework Choices

### 1. Storage & Job Lifecycle
- **Decision**: In-memory job state coupled with a file-based cache in `backend/data/jobs`.
- **Reasoning**: Requirement explicitly states "No database. Use the filesystem for job outputs with automatic cleanup." Jobs older than 1 hour are automatically evicted by a scheduled background reaper task.

### 2. Classical Fallbacks vs Deep Models
- **Decision**: Classical algorithms (Dark Channel Prior, NLM denoising, Unsharp Masking, Lanczos interpolation) are the primary baseline. Deep neural weights (NAFNet, Real-ESRGAN) are dynamically loaded from `backend/weights/` if present.
- **Reasoning**: Guarantees zero crashes on a fresh clone with no GPU and no pre-downloaded checkpoints.

### 3. Tiled Inference
- **Decision**: 512x512 tile size with 32px overlap and 2D Hann/feather blending. If memory pressure or out-of-memory is detected, the tiling engine automatically halves tile dimensions down to 256px.
- **Reasoning**: Allows processing 24MP+ drone images (e.g. 6000x4000) on resource-constrained laptop memory.

### 4. Color Management & Float32 Precision
- **Decision**: Intermediate enhancement stages operate strictly on float32 arrays normalized to [0, 1]. Tone clipping is prevented via soft saturation knee curves. Quantization to uint8 (0-255) is performed only during final image serialization.
- **Reasoning**: Preserves high-dynamic-range detail in rusted or shadowed metallic structures without blowing out bright sky highlights.
