# nams-ai-agent-test

AI Agent phân tích UX website từ ảnh chụp màn hình — mô phỏng hành vi người dùng tương tự Microsoft Clarity nhưng chạy bằng AI Vision.

## Tính năng

- 👁️ **Attention Heatmap** — dự đoán vùng người dùng nhìn vào đầu tiên
- ⏱️ **Time-on-Element** — ước tính thời gian dừng lại ở từng khu vực
- 📐 **Reading Pattern** — phát hiện F-pattern, Z-pattern, Gutenberg diagram
- 📏 **Fold Analysis** — đánh giá nội dung above/below the fold
- 🎯 **CTA Effectiveness** — kiểm tra độ nổi bật của các nút kêu gọi hành động
- 🔍 **UX Audit** — phát hiện lỗi UX theo Nielsen's Heuristics & Gestalt Principles
- 💡 **Recommendations** — đề xuất cải tiến cụ thể theo thứ tự ưu tiên

## Prerequisites

- Python 3.10+
- GreenNode IAM Service Account ([tạo tại đây](https://iam.console.vngcloud.vn/service-accounts))
- API key của Vision LLM (GreenNode AIP hoặc OpenAI)

## Setup

1. Tạo và kích hoạt virtual environment:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   ```

2. Cài dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Cấu hình credentials:
   ```bash
   cp .env.example .env
   # Chỉnh sửa .env với credentials của bạn
   ```

## Configure LLM

Set các biến sau trong `.env`:

```
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://api.openai.com/v1   # hoặc GreenNode AIP
LLM_MODEL=gpt-4o
```

- **GreenNode AIP**: dùng `/agentbase-llm` để lấy API key, `LLM_BASE_URL=https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1`
- **OpenAI**: `LLM_BASE_URL=https://api.openai.com/v1`, model `gpt-4o`

## Run Locally

```bash
python3 main.py
```

Agent chạy tại `http://127.0.0.1:8080`.

### Test với ảnh PNG:

```bash
# Encode ảnh sang base64
IMAGE_B64=$(base64 -i screenshot.png)

curl -X POST http://127.0.0.1:8080/invocations \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$IMAGE_B64\", \"file_type\": \"png\", \"context\": \"Landing page for SaaS product\"}"
```

### Test với PDF:

```bash
PDF_B64=$(base64 -i website.pdf)

curl -X POST http://127.0.0.1:8080/invocations \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$PDF_B64\", \"file_type\": \"pdf\"}"
```

### Health check:

```bash
curl http://127.0.0.1:8080/health
```

## Payload Format

```json
{
  "image_base64": "<base64 string của PNG hoặc PDF>",
  "file_type": "png",
  "context": "Mô tả trang web (tuỳ chọn, giúp AI phân tích chính xác hơn)"
}
```

## Response Format

```json
{
  "status": "success",
  "analysis": {
    "summary": "...",
    "reading_pattern": "F-pattern",
    "attention_hotspots": [...],
    "fold_analysis": {...},
    "cta_evaluation": [...],
    "ux_issues": [...],
    "section_time_estimates": [...],
    "recommendations": [...],
    "overall_ux_score": 72,
    "scores": {
      "visual_hierarchy": 80,
      "cta_effectiveness": 65,
      "information_architecture": 70,
      "accessibility_estimate": 60,
      "mobile_friendliness_estimate": 75
    }
  }
}
```

## Deploy to AgentBase Runtime

Dùng `/agentbase-deploy` để build Docker image và deploy lên GreenNode AgentBase.

## Project Structure

- `main.py` — Agent entrypoint, vision analysis logic
- `Dockerfile` — Container image (python:3.11-slim + poppler)
- `requirements.txt` — Python dependencies
- `.env.example` — Template biến môi trường
- `.greennode.json` — AgentBase configuration
