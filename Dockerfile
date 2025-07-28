FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install pymupdf sentence-transformers faiss-cpu pandas

CMD ["python", "process_pdfs.py"]
