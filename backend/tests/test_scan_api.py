"""
QuishGuard — Scan API Endpoint Tests
"""

import io
import pytest
from PIL import Image

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_scan(async_client: AsyncClient):
    """Test POST /api/v1/scans — submit an image for scan."""
    # Create a test image
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    response = await async_client.post(
        "/api/v1/scans",
        files={"file": ("test.png", img_bytes, "image/png")},
        data={"scan_options": '{"ai_check": true, "qr_check": true}'},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
    assert "id" in data
    assert "ai_image_analysis" in data
    assert data["ai_image_analysis"]["verdict"] in ["real", "fake", "uncertain"]
    assert 0.0 <= data["ai_image_analysis"]["confidence"] <= 1.0
    assert "qr_analysis" in data
    assert "image_hash" in data


@pytest.mark.asyncio
async def test_get_scan_by_id(async_client: AsyncClient):
    """Test GET /api/v1/scans/{scan_id} — retrieve a scan result."""
    # First create a scan
    img = Image.new("RGB", (150, 150), color=(50, 50, 50))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    create_response = await async_client.post(
        "/api/v1/scans",
        files={"file": ("test2.png", img_bytes, "image/png")},
        data={"scan_options": '{"ai_check": true, "qr_check": true}'},
    )
    assert create_response.status_code == 201
    scan_id = create_response.json()["id"]

    # Then retrieve it
    get_response = await async_client.get(f"/api/v1/scans/{scan_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == scan_id


@pytest.mark.asyncio
async def test_get_scan_not_found(async_client: AsyncClient):
    """Test GET /api/v1/scans/{nonexistent_id} — should return 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await async_client.get(f"/api/v1/scans/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_scan_stats(async_client: AsyncClient):
    """Test GET /api/v1/scans/stats — dashboard statistics."""
    response = await async_client.get("/api/v1/scans/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "ai_fake_count" in data
    assert "ai_real_count" in data
    assert "quish_malicious_count" in data


@pytest.mark.asyncio
async def test_get_scan_history(async_client: AsyncClient):
    """Test GET /api/v1/scans/history — paginated history."""
    response = await async_client.get("/api/v1/scans/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "pages" in data


@pytest.mark.asyncio
async def test_invalid_file_type(async_client: AsyncClient):
    """Test POST /api/v1/scans with invalid file type — should return 400."""
    txt_bytes = io.BytesIO(b"this is not an image")
    response = await async_client.post(
        "/api/v1/scans",
        files={"file": ("test.txt", txt_bytes, "text/plain")},
        data={"scan_options": '{"ai_check": true, "qr_check": true}'},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test GET /health — health check endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
