import os
import sys
import django
import spacy

# ✅ STEP 1: Register the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ✅ STEP 2: Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")
django.setup()

# ✅ STEP 3: Import Django models AFTER setup
from material.models import Material, UserActivity
from django.contrib.auth.models import User

# ✅ Load SpaCy model
nlp = spacy.load("en_core_web_md")

# ✅ Select a specific user
user = User.objects.get(username="secondguy")

# ✅ Fetch the user's last 5 activities
recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:5]
interacted_materials = []

for activity in recent_activities:
    interacted_materials += list(Material.objects.filter(
        subject=activity.subject,
        level=activity.level
    ))

# Handle cold-start users (no prior interactions)
if not interacted_materials:
    print("⚠️ No user activities found.")
    exit()

# ✅ Get materials not yet interacted with
all_materials = Material.objects.exclude(id__in=[m.id for m in interacted_materials])

# ✅ Compute semantic similarity
scores = []
for candidate in all_materials:
    candidate_doc = nlp(candidate.description.lower())
    total_score, count = 0, 0
    for seen in interacted_materials:
        seen_doc = nlp(seen.description.lower())
        total_score += seen_doc.similarity(candidate_doc)
        count += 1
    avg_score = total_score / count if count > 0 else 0
    scores.append((candidate, avg_score))

# ✅ Sort results by similarity
scores.sort(key=lambda x: x[1], reverse=True)

# ✅ Display the top-5 recommendations
print(f"\n🎯 Top {min(5, len(scores))} Recommendations for {user.username}:\n")
for i, (mat, score) in enumerate(scores[:5], 1):
    print(f"{i}. {mat.name} ({mat.subject.title()} - {mat.level.title()}) -> Similarity: {score*100:.2f}%")

# ✅ Debug view - see all similarity scores
print("\n--- All Scores (Debug View) ---")
for mat, score in scores:
    print(f"{mat.name:60} | {score*100:.2f}%")
