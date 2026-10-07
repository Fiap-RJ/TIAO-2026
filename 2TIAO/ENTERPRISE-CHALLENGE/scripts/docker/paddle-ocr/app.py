import uuid
from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
import numpy as np
import cv2
from contextlib import asynccontextmanager
from pathlib import Path
from pdf2image import convert_from_bytes

DATA_DIR = Path("/data/results")
DATA_DIR.mkdir(parents=True, exist_ok=True)

ocr = None
ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ocr, ready

    ocr = PaddleOCR(use_angle_cls=True, lang="pt")
    ready = True

    yield

    ready = False


app = FastAPI(title="PaddleOCR API", lifespan=lifespan)


@app.get("/health")
def health():
    if ready:
        return {"status": "OCR ok"}
    return {"status": "loading"}


@app.post("/ocr")
async def ocr_file(file: UploadFile = File(...)):
    if not ready or not ocr:
        return {"error": "OCR ainda não está pronto"}

    file_bytes = await file.read()
    ext = Path(file.filename).suffix.lower()

    all_texts = []

    if ext == ".pdf":
        pages = convert_from_bytes(file_bytes, dpi=300)

        for page_index, page in enumerate(pages):
            img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
            result = ocr.predict(img)
            all_texts.extend(result[0]["rec_texts"])

    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
        image_np = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image is None:
            return {"error": "Imagem inválida"}

        result = ocr.predict(image)
        all_texts = result[0]["rec_texts"]

    else:
        return {"error": f"Tipo de arquivo não suportado: {ext}"}

    request_id = str(uuid.uuid4())
    output_file = DATA_DIR / f"{request_id}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_texts))

    return {"request_id": request_id, "lines": len(all_texts), "texts": all_texts}
