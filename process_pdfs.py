import fitz
import os
import json
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load model for semantic embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_pdf_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("blocks")
        text = " ".join([block[4] for block in blocks])
        sections.append({'page': page_num, 'text': text})
    return sections

def semantic_rank(sections, query, top_k=5):
    corpus = [sec['text'] for sec in sections]
    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    actual_top_k = min(top_k, len(sections))
    top_results = np.argpartition(-scores, range(actual_top_k))[:actual_top_k]

    ranked_sections = sorted(
        [(sections[idx], scores[idx].item()) for idx in top_results],
        key=lambda x: x[1],
        reverse=True
    )
    return ranked_sections


def generate_output(collection_path):
    input_path = os.path.join(collection_path, 'challenge1b_input.json')
    with open(input_path, 'r', encoding='utf-8') as f:
        input_config = json.load(f)

    persona = input_config['persona']['role']
    task = input_config['job_to_be_done']['task']
    documents = input_config['documents']

    all_sections = []
    subsection_analysis = []

    for doc_info in documents:
        pdf_file = os.path.join(collection_path, 'PDFs', doc_info['filename'])
        sections = extract_pdf_sections(pdf_file)
        ranked_sections = semantic_rank(sections, task)

        for rank, (section, _) in enumerate(ranked_sections, 1):
            all_sections.append({
                "document": doc_info['filename'],
                "section_title": doc_info['title'],
                "importance_rank": rank,
                "page_number": section['page']
            })
            subsection_analysis.append({
                "document": doc_info['filename'],
                "refined_text": section['text'],
                "page_number": section['page']
            })

    output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in documents],
            "persona": persona,
            "job_to_be_done": task
        },
        "extracted_sections": all_sections,
        "subsection_analysis": subsection_analysis
    }

    output_path = os.path.join(collection_path, 'challenge1b_output.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"Output generated at {output_path}")

# Process each collection
collections = ['Collection 1', 'Collection 2', 'Collection 3']
base_dir = '.'  # Current directory for Windows compatibility

for col in collections:
    collection_dir = os.path.join(base_dir, col)
    if os.path.exists(collection_dir):
        generate_output(collection_dir)
    else:
        print(f"Collection directory {collection_dir} not found.")