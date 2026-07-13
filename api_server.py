from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Any
from server import verify_disaster_text, verify_disaster_batch
import json
import time

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "api server is running"
    }


@app.post("/verify")
def verify(data: dict[str, Any]):
    start = time.perf_counter()

    try:
        result = verify_disaster_text(data["text"])
        elapsed = time.perf_counter() - start

        return {
            "status": "ok",
            "elapsed_seconds": round(elapsed, 3),
            "result": result,
        }

    except Exception as exc:
        elapsed = time.perf_counter() - start

        return {
            "status": "error",
            "elapsed_seconds": round(elapsed, 3),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def stream_verify_batch(texts: list[str]):
    total = len(texts)
    batch_start = time.perf_counter()

    success_count = 0
    error_count = 0

    for i, text in enumerate(texts, start=1):
        item_start = time.perf_counter()

        try:
            result = verify_disaster_text(text)

            item_elapsed = time.perf_counter() - item_start
            total_elapsed = time.perf_counter() - batch_start

            success_count += 1

            item = {
                "type": "item",
                "index": i,
                "total": total,
                "status": "ok",
                "text": text,
                "item_elapsed_seconds": round(item_elapsed, 3),
                "total_elapsed_seconds": round(total_elapsed, 3),
                "result": result,
            }

        except Exception as exc:
            item_elapsed = time.perf_counter() - item_start
            total_elapsed = time.perf_counter() - batch_start

            error_count += 1

            item = {
                "type": "item",
                "index": i,
                "total": total,
                "status": "error",
                "text": text,
                "item_elapsed_seconds": round(item_elapsed, 3),
                "total_elapsed_seconds": round(total_elapsed, 3),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

        # 每处理完一条，就返回一行 JSON
        yield json.dumps(item, ensure_ascii=False) + "\n"

    batch_elapsed = time.perf_counter() - batch_start

    summary = {
        "type": "summary",
        "total": total,
        "success_count": success_count,
        "error_count": error_count,
        "total_elapsed_seconds": round(batch_elapsed, 3),
        "average_elapsed_seconds": round(batch_elapsed / total, 3) if total > 0 else 0,
    }

    yield json.dumps(summary, ensure_ascii=False) + "\n"


@app.post("/verify_batch")
def verify_batch_stream(data: dict[str, Any]):
    texts = data.get("texts", [])

    if not isinstance(texts, list):
        error_item = {
            "type": "error",
            "status": "error",
            "reason": "texts must be a list",
        }

        return StreamingResponse(
            iter([json.dumps(error_item, ensure_ascii=False) + "\n"]),
            media_type="application/x-ndjson; charset=utf-8",
        )

    return StreamingResponse(
        stream_verify_batch(texts),
        media_type="application/x-ndjson; charset=utf-8",
    )
