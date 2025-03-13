import re
from typing import List

class TextProcessor:
    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 20):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def normalize_text(self, text: str) -> str:
        """Normalise le texte donné."""
        text = text.lower()  # Passe le texte en minuscules
        text = re.sub(r'\s+', ' ', text).strip()  # Supprime les espaces multiples
        return text
    
    def tokenize_text(self, text: str) -> List[str]:
        """Tokenise le texte mot par mot."""
        return re.findall(r"\b\w+\b", text)
    
    def split_text(self, text: str) -> List[List[str]]:
        """Découpe le texte en morceaux de taille définie avec chevauchement et retourne une liste de listes de tokens."""
        tokens = self.tokenize_text(text)
        chunks = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunks.append(tokens[start:end])
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def process_text(self, text: str) -> List[List[str]]:
        """Applique la normalisation, la tokenisation et le découpage du texte en liste de listes de tokens."""
        normalized_text = self.normalize_text(text)
        return self.split_text(normalized_text)
