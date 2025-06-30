from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import os
import pdfplumber
import docx
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")  # можно заменить на другую

# В памяти: список эмбеддингов и метаданных
knowledge_index = []

# ------------ Утилиты ------------- #

def extract_text(file_path: str, ext: str) -> str:
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or '' for page in pdf.pages)
    elif ext == ".docx":
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

def split_text(text: str, chunk_size: int = 500) -> List[str]:
    # Примитивное разбиение по абзацам
    paragraphs = text.split('\n')
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < chunk_size:
            current += p + " "
        else:
            chunks.append(current.strip())
            current = p + " "
    if current:
        chunks.append(current.strip())
    return chunks

# ------------ Эндпоинты ------------- #

@app.post("/upload/files")
async def upload_files(files: List[UploadFile] = File(...)):
    saved = []
    for file in files:
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())
        saved.append(file.filename)
    return {"filenames": saved}

class FileList(BaseModel):
    files: List[str]

@app.post("/pipeline/process_uploaded_files")
async def process_pipeline(data: FileList):
    previews = {}
    for fname in data.files:
        path = os.path.join(UPLOAD_DIR, fname)
        ext = os.path.splitext(fname)[-1].lower()

        try:
            text = extract_text(path, ext)
            if not text:
                previews[fname] = "(пустой файл или не удалось извлечь текст)"
                continue

            # Предпросмотр
            previews[fname] = text[:100].replace("\n", " ") + "..."

            # Разбиение и векторизация
            chunks = split_text(text)
            embeddings = model.encode(chunks)

            # Сохраняем эмбеддинги и метаинфу
            for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                knowledge_index.append({
                    "file": fname,
                    "chunk_id": i,
                    "text": chunk,
                    "embedding": vector
                })

        except Exception as e:
            previews[fname] = f"(ошибка: {str(e)})"

    return {
        "status": "ok",
        "previews": previews,
        "total_chunks": len(knowledge_index)
    }

@app.get("/search")
def search(query: str, top_k: int = 3):
    if not knowledge_index:
        return {"error": "Индекс пуст"}

    query_vec = model.encode([query])[0]
    vectors = np.array([item["embedding"] for item in knowledge_index])
    
    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity([query_vec], vectors)[0]
    top_idxs = np.argsort(sims)[::-1][:top_k]

    return [
        {
            "file": knowledge_index[i]["file"],
            "chunk_id": knowledge_index[i]["chunk_id"],
            "text": knowledge_index[i]["text"],
            "score": float(sims[i])
        }
        for i in top_idxs
    ]
