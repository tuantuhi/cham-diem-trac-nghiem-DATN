from __future__ import annotations
import os
import tempfile
from pathlib import Path
import multipart
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List

from templates import OMR50Detector, OMR20Detector
from yolo_pipeline import YOLOPipeline

app = FastAPI(title="OMR Checker API", version="1.0.0")
detector = OMR50Detector()
detector_20 = OMR20Detector()

base_dir = os.path.dirname(os.path.abspath(__file__))
yolo_detector = YOLOPipeline(
    yolo_model_path=os.path.join(base_dir, "models", "best_v9.pt"),
    ocr_model_path=os.path.join(base_dir, "models", "abcd_ocr.pth")
)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict/omr")
async def predict_omr(file: UploadFile = File(...)) -> JSONResponse:
    suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(await file.read())

    try:
        result = detector.process_with_visualization(tmp_path)
        return JSONResponse(content={"results": result})
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@app.post("/predict/omr_20")
async def predict_omr_20(file: UploadFile = File(...)) -> JSONResponse:
    suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(await file.read())

    try:
        result = detector_20.process_with_visualization(str(tmp_path))
        return JSONResponse(content={"results": result})
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@app.post("/predict/yolo")
async def predict_yolo(file: UploadFile = File(...)) -> JSONResponse:
    suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(await file.read())

    try:
        result = yolo_detector.process_api(str(tmp_path))
        return JSONResponse(content={"results": result})
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

@app.post("/predict/yolo/batch")
async def predict_yolo_batch(files: List[UploadFile] = File(...)) -> JSONResponse:
    tmp_paths = []
    try:
        for file in files:
            suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(await file.read())
                tmp_paths.append(str(tmp_path))
                
        result = yolo_detector.process_api_batch(tmp_paths)
        return JSONResponse(content={"results": result})
    finally:
        for path in tmp_paths:
            p = Path(path)
            if p.exists():
                p.unlink()
