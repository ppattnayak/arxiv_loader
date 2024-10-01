#Testing

import os
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import faiss
import json
from tinydb import TinyDB, Query
from tqdm import tqdm

class ArxivEmbedding:

    def __init__(self, db_path, embedding_model='nomic-ai/nomic-embed-text-v1'):
        # Load the embedding model
        self.embedding_model = SentenceTransformer(embedding_model, trust_remote_code=True)
        self.embedding_model.to(torch.device('cuda' if torch.cuda.is_available() else 'cpu'))

        # Load the database
        self.db_path = db_path
        self.db = TinyDB(f'{dbpath}/arxiv_papers.json')
        self.table = self.db.table('cs_paper_info')

        # Placeholder for FAISS index, will initialize in generate_embeddings
        self.title_index = None
        self.abs_index = None

        # Create mappings between ids and index values
        self.id_to_index = {}
        self.index_to_id = {}
        self.current_index = 0

    def generate_embeddings(self):
        paper_list = self.table.all()

        for paper in tqdm(paper_list, desc="Generating embeddings"):
            paper_id = paper['id']
            title = paper['title']
            abstract = paper['abs']

            # Generate embeddings for title and abstract
            title_embedding = self.embedding_model.encode([title], convert_to_tensor=True).cpu().numpy()
            abs_embedding = self.embedding_model.encode([abstract], convert_to_tensor=True).cpu().numpy()

            # Check dimensions of the embeddings
            title_dim = title_embedding.shape[1]
            abs_dim = abs_embedding.shape[1]

            # Initialize FAISS indices if not already initialized
            if self.title_index is None:
                print(f"Initializing FAISS index for title with dimension {title_dim}")
                self.title_index = faiss.IndexFlatL2(title_dim)  # Use correct dimension
            if self.abs_index is None:
                print(f"Initializing FAISS index for abstract with dimension {abs_dim}")
                self.abs_index = faiss.IndexFlatL2(abs_dim)  # Use correct dimension

            # Add to FAISS index
            try:
                self.title_index.add(title_embedding)
                self.abs_index.add(abs_embedding)
            except AssertionError as e:
                print(f"Error adding embeddings for paper ID {paper_id}: {e}")
                continue

            # Map paper ID to FAISS index
            self.id_to_index[paper_id] = self.current_index
            self.index_to_id[self.current_index] = paper_id
            self.current_index += 1

    def save_faiss_index(self):
        # Save the FAISS indexes
        faiss.write_index(self.title_index, f'{self.db_path}/faiss_paper_title_embeddings.bin')
        faiss.write_index(self.abs_index, f'{self.db_path}/faiss_paper_abs_embeddings.bin')

        # Save the ID mappings
        with open(f'{self.db_path}/arxivid_to_index.json', 'w') as f:
            json.dump(self.id_to_index, f)

    def load_faiss_index(self):
        # Load the FAISS indexes
        self.title_index = faiss.read_index(f'{self.db_path}/faiss_paper_title_embeddings.bin')
        self.abs_index = faiss.read_index(f'{self.db_path}/faiss_paper_abs_embeddings.bin')

        # Load the ID mappings
        with open(f'{self.db_path}/arxivid_to_index.json', 'r') as f:
            self.id_to_index = json.load(f)

        # Create reverse mapping
        self.index_to_id = {index: paper_id for paper_id, index in self.id_to_index.items()}

    def search_papers_by_embedding(self, query, top_k=5, search_by="title"):
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_tensor=True).cpu().numpy()

        # Search in FAISS index
        if search_by == "title":
            distances, indices = self.title_index.search(query_embedding, top_k)
        else:
            distances, indices = self.abs_index.search(query_embedding, top_k)

        # Retrieve paper IDs from indices
        results = [self.index_to_id[idx] for idx in indices[0] if idx != -1]
        return results
