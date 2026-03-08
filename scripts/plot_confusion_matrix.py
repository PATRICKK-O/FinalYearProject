import os
import sys
import django

# ✅ Dynamically locate the Django project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# ✅ Point to your project settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")

# ✅ Initialize Django
django.setup()

# === 2️⃣ Now safe to import Django models ===
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from django.contrib.auth.models import User
from material.models import UserActivity
from material.utils.recommender_helper import get_recommendations_for_user

# === 3️⃣ Define relationships and rules locally ===
RELATED_SUBJECTS = {
    "maths": ["physics", "chemistry"],
    "physics": ["maths", "chemistry"],
    "chemistry": ["physics", "maths"],
    "english": []
}

LEVEL_ORDER = {"beginner": 1, "intermediate": 2, "advanced": 3}


def is_relevant(pred_subj, pred_lvl, true_subj, true_lvl):
    """Check if a predicted material is relevant to user activity."""
    if pred_subj == true_subj:
        return True
    if true_subj in RELATED_SUBJECTS and pred_subj in RELATED_SUBJECTS[true_subj]:
        return True
    return False


def level_progression_allowed(pred_lvl, true_lvl):
    """Check if a higher level recommendation is valid."""
    return LEVEL_ORDER.get(pred_lvl, 1) >= LEVEL_ORDER.get(true_lvl, 1)


# === 4️⃣ Evaluate recommendations for each user ===
y_true = []
y_pred = []

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
                y_true.append(1)
                y_pred.append(1)
            else:
                y_true.append(1)
                y_pred.append(0)


# === 5️⃣ Generate Confusion Matrix ===
cm = confusion_matrix(y_true, y_pred, labels=[1, 0])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Relevant", "Irrelevant"])

# === 6️⃣ Plot Confusion Matrix ===
fig, ax = plt.subplots(figsize=(6, 5))
disp.plot(ax=ax, cmap='Blues', colorbar=False)

ax.set_title("Confusion Matrix of the NLP-Based Recommender System", fontsize=14, pad=20)
ax.set_xlabel("Predicted Label", fontsize=12)
ax.set_ylabel("True Label", fontsize=12)

plt.savefig("confusion_matrix_chart.png", dpi=300, bbox_inches='tight')
plt.show()
