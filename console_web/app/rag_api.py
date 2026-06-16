from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
from typing import List
import hashlib
import json
import re
import time

router = APIRouter(prefix="/rag", tags=["rag"])

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "rag_storage"
DATA_DIR.mkdir(parents=True, exist_ok=True)

KB_FILE = DATA_DIR / "knowledge_chunks.jsonl"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_text(text: str, chunk_size: int = 700, overlap: int = 120) -> List[str]:
    text = clean_text(text)
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1)
    return chunks


def tokenize(text: str) -> set:
    text = text.lower()
    words = re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", text)
    return set(words)


def read_all_chunks() -> List[dict]:
    if not KB_FILE.exists():
        return []

    chunks = []
    with KB_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                chunks.append(json.loads(line))
            except Exception:
                continue
    return chunks


def append_chunks(filename: str, chunks: List[str]) -> int:
    count = 0
    with KB_FILE.open("a", encoding="utf-8") as f:
        for idx, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{filename}-{idx}-{chunk}".encode("utf-8")).hexdigest()
            record = {
                "id": chunk_id,
                "filename": filename,
                "chunk_index": idx,
                "text": chunk,
                "created_at": time.time(),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


@router.post("/upload")
async def upload_knowledge_file(file: UploadFile = File(...)):
    filename = file.filename or "unknown.txt"
    suffix = Path(filename).suffix.lower()

    allowed = {".txt", ".md", ".csv", ".json", ".html", ".htm"}
    if suffix not in allowed:
        return {
            "error": "当前轻量版知识库建议上传 TXT、MD、CSV、JSON、HTML。PDF/Word 需要后续增加解析库。"
        }

    raw = await file.read()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("gbk")
        except UnicodeDecodeError:
            return {"error": "文件编码无法识别，请另存为 UTF-8 后再上传。"}

    chunks = split_text(text)
    if not chunks:
        return {"error": "文件内容为空，未写入知识库。"}

    count = append_chunks(filename, chunks)

    return {
        "message": "上传成功",
        "filename": filename,
        "chunks": count,
    }


@router.post("/search")
async def search_knowledge(req: SearchRequest):
    query = clean_text(req.query)
    if not query:
        return {"context": "", "results": []}

    all_chunks = read_all_chunks()
    if not all_chunks:
        return {"context": "", "results": []}

    q_tokens = tokenize(query)

    scored = []
    for item in all_chunks:
        text = item.get("text", "")
        t_tokens = tokenize(text)

        overlap = len(q_tokens & t_tokens)
        bonus = 0

        for key in ["儿童", "证书", "误判", "申诉", "商品", "页面", "平台", "toy", "children", "adult", "not a toy"]:
            if key.lower() in query.lower() and key.lower() in text.lower():
                bonus += 2

        score = overlap + bonus
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [item for _, item in scored[: max(1, req.top_k)]]

    context_parts = []
    for i, item in enumerate(top, 1):
        context_parts.append(
            f"【资料{i}｜来源：{item.get('filename', '未知文件')}】\n{item.get('text', '')}"
        )

    return {
        "context": "\n\n".join(context_parts),
        "results": top,
    }


@router.post("/clear")
async def clear_knowledge():
    if KB_FILE.exists():
        KB_FILE.unlink()
    return {"message": "知识库已清空"}
