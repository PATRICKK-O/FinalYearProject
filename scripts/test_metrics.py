import os
import sys
import django

# ✅ Dynamically set the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ✅ Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")

# ✅ Initialize Django
django.setup()

# 2️⃣ Now it's safe to import Django models
from django.contrib.auth.models import User
from material.models import UserActivity, Material
from material.utils.recommender_helper import get_recommendations_for_user
from sklearn.metrics import precision_score, recall_score, f1_score

# ---------------- Cross-domain and level mapping ----------------
RELATED_SUBJECTS = {
    "maths": ["physics", "chemistry"],
    "physics": ["maths", "chemistry"],
    "chemistry": ["physics", "maths"],
    "english": []
}

LEVEL_ORDER = {"beginner": 1, "intermediate": 2, "advanced": 3}


def is_relevant(pred_subj, pred_lvl, true_subj, true_lvl):
    """Determines if a predicted material is relevant to a user's real interest."""
    if pred_subj == true_subj:
        return True
    if true_subj in RELATED_SUBJECTS and pred_subj in RELATED_SUBJECTS[true_subj]:
        return True
    return False


def level_progression_allowed(pred_lvl, true_lvl):
    """Allows progression from lower to higher levels."""
    if LEVEL_ORDER[pred_lvl] >= LEVEL_ORDER[true_lvl]:
        return True
    return False


# ---------------- MAIN TEST LOGIC ----------------
y_true = []  # was there a relevant material that should be recommended?
y_pred = []  # did the system recommend it correctly?

users = User.objects.all()

for user in users:
    recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:5]
    if not recent_activities.exists():
        continue

    recommended_materials = get_recommendations_for_user(user)

    for activity in recent_activities:
        true_subj = activity.subject.lower()
        true_lvl = activity.level.lower()

        for mat in recommended_materials:
            pred_subj = mat.subject.lower()
            pred_lvl = mat.level.lower()

            if is_relevant(pred_subj, pred_lvl, true_subj, true_lvl) and level_progression_allowed(pred_lvl, true_lvl):
                # True positive (1, 1)
                y_true.append(1)
                y_pred.append(1)
            else:
                # False positive (1, 0)
                y_true.append(1)
                y_pred.append(0)

# ---------------- METRICS ----------------
precision = precision_score(y_true, y_pred, zero_division=0)
recall = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)

print("\n--- Refined Evaluation Metrics ---")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1-Score: {f1:.2f}")
