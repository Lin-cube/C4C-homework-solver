#!/usr/bin/env python3
"""
Stage 1: Document Ingestion
读取作业文件（Markdown / PDF / Word / 图片），输出结构化文本。

Starter kit 仅实现 Markdown 读取。
PDF / Word / OCR 留给学生扩展（见 C4C.md Level 2）。

用法:
    python ingest.py input_file output.json
    python ingest.py homework.md problems.json
"""

import json
import re
import sys
from pathlib import Path


# ─────────────────────────────────────────────
# 核心函数：读取不同格式
# ─────────────────────────────────────────────

def read_markdown(filepath: str) -> str:
    """读取 Markdown 文件，返回原始文本。"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def read_pdf_text(filepath: str) -> str:
    """
    读取文本型 PDF（C4C Level 2 扩展：电子版 PDF 摄入）。

    依次尝试 pypdf → pdfplumber，均未安装时用标准库做最小文本提取。
    扫描型 PDF（纯图片）需要 OCR，见 read_image_ocr。
    """
    # 1) pypdf（轻量）
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        pages = [p.extract_text() or "" for p in reader.pages]
        text = "\n".join(pages).strip()
        if text:
            return text
    except Exception:
        pass

    # 2) pdfplumber（更精确）
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            text = "\n".join((page.extract_text() or "") for page in pdf.pages).strip()
        if text:
            return text
    except Exception:
        pass

    # 3) 标准库最小提取（BT...ET / Tj / TJ 文本算子）
    return _pdf_text_stdlib(filepath)


def _pdf_text_stdlib(filepath: str) -> str:
    """用标准库从 PDF 内容流里粗略抽取文本（无第三方依赖的兜底）。"""
    import re
    import zlib

    with open(filepath, "rb") as f:
        data = f.read()

    out = []
    # 解压所有 FlateDecode 流
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.DOTALL):
        raw = m.group(1)
        try:
            raw = zlib.decompress(raw)
        except Exception:
            pass
        # 提取 (text) Tj 与 [...] TJ 中的字符串
        for tm in re.finditer(rb"\((?:[^()\\]|\\.)*\)\s*Tj", raw):
            s = tm.group(0)
            s = re.sub(rb"\\[()\\]", lambda x: x.group(0)[1:2], s)
            s = re.sub(rb"\)\s*Tj", b"", s).lstrip(b"(")
            try:
                out.append(s.decode("latin-1"))
            except Exception:
                pass
    text = "\n".join(out).strip()
    if not text:
        raise NotImplementedError(
            "无法从该 PDF 提取文本（可能是扫描件）。请安装 pypdf 或对扫描件使用 OCR。")
    return text


def read_docx(filepath: str) -> str:
    """
    读取 Word 文档（C4C Level 2 扩展：python-docx）。
    提取段落与表格文本，按段落换行。
    """
    try:
        import docx
    except ImportError:
        raise NotImplementedError(
            "Word 摄入需要 python-docx。请运行: pip install python-docx")

    doc = docx.Document(filepath)
    parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            parts.append(" | ".join(cells))
    return "\n".join(parts)


def read_image_ocr(filepath: str) -> str:
    """
    OCR 读取图片/扫描件（C4C Level 2/3 扩展）。
    需要: pip install pytesseract Pillow（可选；也可改用国产模型 Vision API）。
    """
    try:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(filepath), lang="chi_sim+eng")
    except ImportError:
        raise NotImplementedError(
            "图片 OCR 需要 pytesseract + Pillow，并安装 Tesseract。"
            "替代方案：使用 Qwen-VL / Kimi Vision API 识别公式。")


# ─────────────────────────────────────────────
# 格式检测与路由
# ─────────────────────────────────────────────

FORMAT_HANDLERS = {
    ".md":   read_markdown,
    ".txt":  read_markdown,       # 纯文本同 Markdown 处理
    ".pdf":  read_pdf_text,
    ".docx": read_docx,
    ".png":  read_image_ocr,
    ".jpg":  read_image_ocr,
    ".jpeg": read_image_ocr,
}


def detect_format(filepath: str) -> str:
    """根据扩展名检测文件格式。"""
    ext = Path(filepath).suffix.lower()
    if ext not in FORMAT_HANDLERS:
        raise ValueError(f"不支持的文件格式: {ext}\n支持: {list(FORMAT_HANDLERS.keys())}")
    return ext


def ingest(filepath: str) -> dict:
    """
    主入口：读取任意格式的作业文件，返回结构化结果。

    返回:
        {
            "source_file": "homework.md",
            "format": ".md",
            "raw_text": "...",
            "sections": [
                {"title": "Section Title", "content": "..."},
                ...
            ]
        }
    """
    filepath = str(filepath)
    ext = detect_format(filepath)
    handler = FORMAT_HANDLERS[ext]

    raw_text = handler(filepath)

    # 基础分段：按 Markdown 标题或空行分段
    sections = split_into_sections(raw_text)

    return {
        "source_file": Path(filepath).name,
        "format": ext,
        "raw_text": raw_text,
        "sections": sections,
    }


def split_into_sections(text: str) -> list:
    """
    将文本按 Markdown 标题分段。
    如果没有标题，整个文本作为一个 section。
    """
    sections = []
    current_title = "Untitled"
    current_lines = []

    for line in text.split("\n"):
        # 检测 Markdown 标题
        heading_match = re.match(r"^(#{1,4})\s+(.+)", line)
        if heading_match:
            # 保存前一个 section
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    sections.append({
                        "title": current_title,
                        "content": content,
                    })
            current_title = heading_match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    # 保存最后一个 section
    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append({
                "title": current_title,
                "content": content,
            })

    return sections


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("用法: python ingest.py <输入文件> <输出.json>")
        print("示例: python ingest.py homework.md problems.json")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not Path(input_path).exists():
        print(f"错误: 文件不存在 — {input_path}")
        sys.exit(1)

    print(f"[Stage 1] 文档摄入: {input_path}")
    result = ingest(input_path)

    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  格式: {result['format']}")
    print(f"  分段: {len(result['sections'])} sections")
    print(f"  输出: {output_path}")


if __name__ == "__main__":
    main()
