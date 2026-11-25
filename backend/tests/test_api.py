import io
import time
from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import pytest

from app.main import app

client = TestClient(app)


@pytest.fixture
def test_image_bytes() -> bytes:
    img = Image.new("RGB", (120, 120), color=(180, 120, 90))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "InfraClarity" in data["app"]


def test_capabilities_endpoint():
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert "device" in data
    assert "installed_models" in data
    assert "available_stages" in data
    assert "dehaze" in data["available_stages"]


def test_analyze_endpoint(test_image_bytes: bytes):
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("test.png", test_image_bytes, "image/png")},
    )
    assert response.status_code == 200
    report = response.json()
    assert "blur" in report
    assert "haze" in report
    assert "noise" in report
    assert "contrast" in report
    assert "resolution_flag" in report
    assert report["resolution_flag"] is True  # 120px < 1080px


def test_invalid_file_rejection():
    # Corrupted / invalid file content
    fake_bytes = b"This is not a real image header"
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("bad.png", fake_bytes, "image/png")},
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_unsupported_mime_rejection():
    response = client.post(
        "/api/v1/analyze",
        files={"image": ("test.txt", b"hello world", "text/plain")},
    )
    assert response.status_code == 415


def test_enhance_job_lifecycle(test_image_bytes: bytes):
    # 1. Submit enhancement job
    response = client.post(
        "/api/v1/enhance",
        files={"image": ("inspect.png", test_image_bytes, "image/png")},
        data={"options": '{"preset": "Pipeline Close-up"}'},
    )
    assert response.status_code == 200
    res_data = response.json()
    assert "job_id" in res_data
    job_id = res_data["job_id"]

    # 2. Poll job status until completed
    max_wait = 30.0
    start = time.time()
    final_status = None

    while time.time() - start < max_wait:
        poll_resp = client.get(f"/api/v1/jobs/{job_id}")
        assert poll_resp.status_code == 200
        job_data = poll_resp.json()
        if job_data["status"] in ("completed", "failed"):
            final_status = job_data
            break
        time.sleep(0.3)

    assert final_status is not None, "Job timed out"
    assert final_status["status"] == "completed", f"Job failed with: {final_status.get('error')}"
    assert final_status["progress"] == 1.0
    assert final_status["metrics"] is not None
    assert "detail_gain" in final_status["metrics"]

    # 3. Fetch enhanced image result
    img_resp = client.get(f"/api/v1/jobs/{job_id}/result")
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] in ("image/png", "image/jpeg")
    assert len(img_resp.content) > 100


def test_nonexistent_job_404():
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
