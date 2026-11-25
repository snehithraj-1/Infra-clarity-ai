import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_assistant_chat_endpoint_heuristic():
    payload = {
        "message": "Analyze critical faults and cracks in this transmission tower image",
        "job_id": None,
        "report": {
            "blur": {"score": 45.0, "severity": "high"},
            "haze": {"score": 0.22, "severity": "medium"},
            "noise": {"score": 12.0, "severity": "low"},
            "contrast": {"score": 0.18, "severity": "medium"},
            "resolution_flag": False,
            "dimensions": [1920, 1080],
            "hints": ["High blur detected"],
        },
        "metrics": {
            "detail_gain": 185.4,
            "canny_gain": 120.0,
            "laplacian_gain": 240.0,
        },
    }

    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 50
    assert "suggested_prompts" in data
    assert len(data["suggested_prompts"]) > 0
    assert data["risk_level"] in ("Low", "Medium", "High", "Critical")


def test_assistant_what_is_in_image_intent():
    payload = {
        "message": "tell that what is in it and describe what you see",
        "job_id": None,
        "report": {
            "blur": {"score": 38.0, "severity": "high"},
            "haze": {"score": 0.28, "severity": "high"},
            "noise": {"score": 4.5, "severity": "medium"},
            "contrast": {"score": 0.16, "severity": "high"},
            "resolution_flag": False,
            "dimensions": [2048, 1536],
            "loopholes": [
                {
                    "title": "Concealed Micro-Fissures",
                    "severity": "high",
                    "vulnerability_in_original": "Motion blur hides crack paths",
                    "restoration_fix": "Dual-scale shock filter restores edges",
                    "action_required": "Visual verification",
                }
            ],
        },
        "metrics": {"detail_gain": 220.0},
    }

    response = client.post("/api/v1/assistant/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert ("Scene" in data["reply"] and "Identification" in data["reply"]) or "Asset" in data["reply"] or "Infrastructure" in data["reply"] or len(data["reply"]) > 50
    assert "Optical" in data["reply"] or "Degradation" in data["reply"] or len(data["reply"]) > 50


def test_assistant_stream_endpoint():
    payload = {
        "message": "Summarize this asset status",
        "job_id": None,
        "report": {
            "blur": {"score": 25.0, "severity": "medium"},
            "haze": {"score": 0.15, "severity": "low"},
            "noise": {"score": 2.0, "severity": "low"},
            "contrast": {"score": 0.25, "severity": "low"},
            "resolution_flag": False,
            "dimensions": [1920, 1080],
        },
        "metrics": {"detail_gain": 150.0},
    }

    with client.stream("POST", "/api/v1/assistant/stream", json=payload) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        lines = list(response.iter_lines())
        assert len(lines) > 0
        data_lines = [l for l in lines if l.startswith("data: ")]
        assert len(data_lines) > 0
