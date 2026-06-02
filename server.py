"""
Nam's UX Agent — Web UI Server
Proxy giữa browser và AgentBase endpoint
"""
import os, base64, io, json, httpx
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

AGENT_ENDPOINT = os.environ.get(
    "AGENT_ENDPOINT",
    "https://endpoint-1c7d79ba-daca-4203-98c7-388896e7311f"
    ".agentbase-runtime.aiplatform.vngcloud.vn"
)

app = FastAPI(title="Nam UX Agent UI")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


def file_to_b64(data: bytes, filename: str) -> tuple[str, str]:
    """Convert uploaded file to base64. Returns (base64_str, file_type)."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        try:
            import fitz
            from PIL import Image
            doc = fitz.open(stream=data, filetype="pdf")
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            max_size = 1400
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=82)
            doc.close()
            return base64.b64encode(buf.getvalue()).decode(), "png"
        except Exception as e:
            raise HTTPException(400, f"PDF render failed: {e}")
    else:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        if img.mode != "RGB":
            img = img.convert("RGB")
        max_size = 1400
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            img = img.resize((int(img.size[0]*ratio), int(img.size[1]*ratio)))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82)
        return base64.b64encode(buf.getvalue()).decode(), "png"


async def call_agent(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(f"{AGENT_ENDPOINT}/invocations",
                              json=payload,
                              headers={"Content-Type": "application/json"})
        return r.json()


# ── API Routes ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{AGENT_ENDPOINT}/health")
        return {"ui": "ok", "agent": r.json()}


@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    lang: str = Form("vi"),
    context: str = Form("")
):
    data = await file.read()
    b64, ftype = file_to_b64(data, file.filename)
    result = await call_agent({
        "mode": "analyze", "image_base64": b64,
        "file_type": ftype, "lang": lang, "context": context
    })
    return JSONResponse(result)


@app.post("/api/ab_test")
async def ab_test(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    lang: str = Form("vi"),
    context: str = Form("")
):
    b64_a, _ = file_to_b64(await file_a.read(), file_a.filename)
    b64_b, _ = file_to_b64(await file_b.read(), file_b.filename)
    result = await call_agent({
        "mode": "ab_test",
        "image_a_base64": b64_a, "image_b_base64": b64_b,
        "lang": lang, "context": context
    })
    return JSONResponse(result)


@app.post("/api/responsive")
async def responsive(
    file: UploadFile = File(...),
    lang: str = Form("vi"),
    context: str = Form("")
):
    b64, ftype = file_to_b64(await file.read(), file.filename)
    result = await call_agent({
        "mode": "responsive", "image_base64": b64,
        "file_type": ftype, "lang": lang, "context": context
    })
    return JSONResponse(result)


@app.post("/api/component")
async def component(
    file: UploadFile = File(...),
    lang: str = Form("vi"),
    context: str = Form(""),
    components: str = Form("")
):
    b64, ftype = file_to_b64(await file.read(), file.filename)
    comp_list = [c.strip() for c in components.split(",") if c.strip()]
    result = await call_agent({
        "mode": "component", "image_base64": b64,
        "file_type": ftype, "lang": lang,
        "context": context, "components": comp_list
    })
    return JSONResponse(result)


# ── Health (phải đặt TRƯỚC static mount) ────────────────────────────────────
@app.get("/health")
async def health_check():
    return {"status": "Healthy"}

# ── Serve frontend (đặt CUỐI CÙNG) ──────────────────────────────────────────
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
