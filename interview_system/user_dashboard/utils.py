import torch
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
import re
import json

# Ensure NLTK resources are downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

from transformers import AutoTokenizer, AutoModel

# Global tokenizer and model
TOKENIZER = AutoTokenizer.from_pretrained('microsoft/deberta-v3-base')
MODEL = AutoModel.from_pretrained('microsoft/deberta-v3-base')

def evaluate_technical_answer(expected_answer, candidate_answer, keywords):
    """
    Evaluate a technical answer based on expected answer, candidate answer, and keywords.
    
    Args:
    - expected_answer (str): The correct/reference answer
    - candidate_answer (str): The answer provided by the candidate
    - keywords (dict): Dictionary of keywords categorized by importance
    
    Returns:
    - float: Final score out of 10
    """
    # Initialize text processing tools
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    # Keyword importance weights
    keyword_weights = {
        'technical_terms': 0.4,
        'concepts': 0.3,
        'implementation': 0.2,
        'best_practices': 0.1
    }
    
    def preprocess_text(text):
        """Advanced text preprocessing"""
        print("Step: Preprocessing candidate answer")
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text)
        tokens = [lemmatizer.lemmatize(token) for token in tokens 
                  if token not in stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def get_embeddings(text, tokenizer, model):
        """Get embeddings using DeBERTa"""
        
        
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1)
    
    # Evaluate technical accuracy
    print("Step: Start processing user input")
    processed_answer = preprocess_text(candidate_answer)
    keyword_score = 0
    
    for category, weight in keyword_weights.items():
        category_keywords = keywords.get(category, [])
        matches = sum(1 for keyword in category_keywords 
                      if keyword.lower() in processed_answer)
        category_score = (matches / len(category_keywords)) if category_keywords else 0
        keyword_score += category_score * weight
    
    # Semantic similarity
    tokenizer = AutoTokenizer.from_pretrained('microsoft/deberta-v3-base')
    model = AutoModel.from_pretrained('microsoft/deberta-v3-base')
    print("Step: Generating embeddings")
    exp_embedding = get_embeddings(expected_answer, tokenizer, model)
    cand_embedding = get_embeddings(candidate_answer, tokenizer, model)
    
    semantic_score = cosine_similarity(
        exp_embedding.numpy(),
        cand_embedding.numpy()
    )[0][0]
    print("Step: Final score calculation")
    # Detect exact or paraphrase
    processed_expected = preprocess_text(expected_answer)
    processed_candidate = preprocess_text(candidate_answer)
    similarity_ratio = SequenceMatcher(None, processed_expected, processed_candidate).ratio()
    
    # Final score calculation
    if similarity_ratio >= 0.9:
        # Exact match or very close paraphrase - minimal score
        return 3.0
    elif similarity_ratio >= 0.75:
        # Paraphrase - reduce scores
        final_score = (keyword_score * 0.8 + semantic_score * 0.8) * 5
    else:
        # Different answer - full scoring
        final_score = (keyword_score + semantic_score) * 5
    
    # Ensure score is between 0 and 10
    return max(0, min(10, final_score))

# # Example usage
# if __name__ == "__main__":
#     # Example keywords dictionary
#     example_keywords = {
#         "technical_terms": ["machine learning", "algorithm", "neural network"],
#         "concepts": ["classification", "training", "prediction"],
#         "implementation": ["numpy", "scikit-learn", "pytorch"],
#         "best_practices": ["feature scaling", "cross-validation", "regularization"]
#     }
    
#     # Example usage
#     expected_answer = "Machine learning is a subset of artificial intelligence that focuses on developing algorithms that can learn from and make predictions or decisions based on data."
#     candidate_answer = "ML is an AI technique where algorithms learn patterns from data to make predictions."
    
#     score = evaluate_technical_answer(expected_answer, candidate_answer, example_keywords)
#     print(f"Answer Score: {score:.2f}/10")