import os
import django
import spacy
from spacy import displacy

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")
django.setup()

from material.models import Material

# Load spaCy NLP model
nlp = spacy.load("en_core_web_md")

# Fetch a sample material
material = Material.objects.first()

if not material:
    print("⚠️ No materials found in the database.")
    exit()

text = material.description
doc = nlp(text)

# Print key info in terminal
print(f"\n--- Material: {material.name} ---")
print(f"Description:\n{text}\n")

# Dependency parse visualization (opens in browser)
print("🧩 Opening dependency tree visualization...")
displacy.serve(doc, style="dep", host="localhost", port=5000)

# For entity visualization, uncomment below:
# displacy.serve(doc, style="ent")


"""
  import os
import django
import spacy

# ==============================
# Django setup
# ==============================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")  # your project settings file
django.setup()

from material.models import Material

# ==============================
# Load spaCy NLP model
# ==============================
nlp = spacy.load("en_core_web_md")

# ==============================
# Fetch a material from your DB
# ==============================
material = Material.objects.first()

if not material:
    print("⚠️ No materials found in the database.")
    exit()

text = material.description
print("\n--- Sample Material Description ---")
print(text)
print("-----------------------------------")

# ==============================
# Process with spaCy
# ==============================
doc = nlp(text)

# ==============================
# Tokenization & POS tagging
# ==============================
print("\n--- Tokenization and Part-of-Speech (POS) Tags ---")
for token in doc:
    print(f"{token.text:15} | Lemma: {token.lemma_:15} | POS: {token.pos_:10} | Dep: {token.dep_}")

# ==============================
# Named Entity Recognition (NER)
# ==============================
print("\n--- Named Entities ---")
if doc.ents:
    for ent in doc.ents:
        print(f"{ent.text:25} | Label: {ent.label_}")
else:
    print("No named entities found.")

# ==============================
# Semantic Similarity Demo
# ==============================
print("\n--- Semantic Similarity Demo ---")
sentences = list(doc.sents)
if len(sentences) >= 2:
    similarity = sentences[0].similarity(sentences[1])
    print(f"Similarity between first two sentences: {similarity:.2f}")
else:
    print("Not enough sentences for similarity check.")

  
"""