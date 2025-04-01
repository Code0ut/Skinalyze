import os
import json
import re
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# Optional: Uncomment if you wish to enable spell correction
# from spellchecker import SpellChecker

import torch
from torch.nn.functional import cosine_similarity
from sentence_transformers import SentenceTransformer

# ---------------------
# 1. Download NLTK Data
# ---------------------
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

# ---------------------
# 2. Load Dataset
# ---------------------
dataset_path = "datasets/Chatbot_dataset.json"
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"{dataset_path} not found. Please ensure the file is in the current directory.")

with open(dataset_path, "r") as f:
    data = json.load(f)

# Convert dataset into a dictionary: disease name -> details
disease_data = {d["name"]: d for d in data["diseases"]}
print("Sample Disease (Acne):")
print(json.dumps(disease_data.get("Acne", {}), indent=2))

# ---------------------
# 3. Advanced Preprocessing Functions
# ---------------------
# Initialize objects once
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
# Optional: spell = SpellChecker()
# Optionally, extend the spell-checker's dictionary with common medical terms if using spell correction.

# Define a mapping for common medical synonyms to standardize terminology
medical_synonyms = {
    "itchy": "itch",
    "pruritic": "itch",
    "rash": "eruption",
    "redness": "red",
    "swollen": "swelling",
    "bumps": "lesion"
}

def advanced_preprocess_text(text):
    # Lowercase the text and remove unwanted characters (keep only letters and spaces)
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    # Tokenize text
    tokens = word_tokenize(text)

    # Optional: Spell correction (uncomment if desired)
    # tokens = [spell.correction(word) for word in tokens]

    # Replace tokens using the medical synonym mapping
    tokens = [medical_synonyms.get(token, token) for token in tokens]

    # Remove stopwords
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize tokens
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return " ".join(tokens)

# ---------------------
# 4. Prepare Disease Descriptions & Embeddings Using BERT
# ---------------------
# For each disease, we combine its symptoms, causes, cure, and home remedies into a detailed description.
disease_names = []
disease_descriptions = []

for disease_name, details in disease_data.items():
    disease_names.append(disease_name)
    description = ""
    # Include symptoms, causes, cure, and home remedies if available
    if "symptoms" in details:
        description += "Symptoms: " + " ".join(details["symptoms"]) + ". "
    if "causes" in details:
        description += "Causes: " + " ".join(details["causes"]) + ". "
    if "cure" in details:
        description += "Cure: " + " ".join(details["cure"]) + ". "
    if "home_remedies" in details:
        description += "Home Remedies: " + " ".join(details["home_remedies"]) + ". "
    # Preprocess the combined description for consistency
    processed_desc = advanced_preprocess_text(description)
    disease_descriptions.append(processed_desc)

# Initialize SentenceTransformer (BERT-based model)
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings for each disease description
disease_embeddings = bert_model.encode(disease_descriptions, convert_to_tensor=True)
print("Computed disease embeddings for", len(disease_embeddings), "diseases.")

# ---------------------
# 5. Gather Detailed User Input via Multiple Queries
# ---------------------
def get_detailed_user_input():
    print("\nPlease answer the following questions to help us better understand your symptoms:")
    primary_symptom = input("1. What is your primary symptom? ")
    location = input("2. Where on your body is this symptom located? ")
    associated_symptoms = input("3. Are there any associated symptoms (e.g., itching, swelling, redness)? ")
    duration = input("4. How long have you been experiencing these symptoms? ")
    severity = input("5. How severe are these symptoms on a scale from 1 to 10? ")
    additional_info = input("6. Any additional observations or triggers (e.g., recent exposure, diet changes)? ")

    # Combine all responses into one detailed description.
    combined_input = " ".join([primary_symptom, location, associated_symptoms, duration, severity, additional_info])
    return combined_input

# ---------------------
# 6. Chatbot Prediction Function Using BERT Similarity
# ---------------------
def chatbot_response(user_input):
    # Preprocess the user input
    processed_input = advanced_preprocess_text(user_input)
    # Compute embedding for the user input
    user_embedding = bert_model.encode(processed_input, convert_to_tensor=True)
    # Compute cosine similarity between user input and each disease description
    similarities = cosine_similarity(user_embedding, disease_embeddings)
    # Get the index of the highest similarity
    best_match_idx = torch.argmax(similarities).item()
    predicted_disease = disease_names[best_match_idx]
    # Extract details safely
    symptoms = ", ".join(details.get("symptoms", ["Not available"]))
    causes = ", ".join(details.get("causes", ["Not available"]))
    cure = ", ".join(details.get("cure", ["Not available"]))
    home_remedies = ", ".join(details.get("home_remedies", ["Not available"]))

    # Format output properly
    response = f"""
        🔍 Predicted Disease: {predicted_disease}\n\n🏥 Symptoms: {symptoms}\n⚠️Causes: {causes}\n💊Cure: {cure}\n🌿Home Remedies: {home_remedies}"""

    return response


