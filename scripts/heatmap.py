import os
import sys
import django
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

# ✅ STEP 1: Register project root and configure Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")
django.setup()

# ✅ STEP 2: Import Django models and helper
from django.contrib.auth.models import User
from material.models import UserActivity, Material
from material.utils.recommender_helper import get_recommendations_for_user

# ================== RELATED SUBJECT AND LEVEL LOGIC ==================
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
    return LEVEL_ORDER[pred_lvl] >= LEVEL_ORDER[true_lvl]


# ================== EVALUATION DATA PREPARATION ==================
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

            if (
                is_relevant(pred_subj, pred_lvl, true_subj, true_lvl)
                and level_progression_allowed(pred_lvl, true_lvl)
            ):
                y_true.append(1)
                y_pred.append(1)
            else:
                y_true.append(1)
                y_pred.append(0)

# ================== CONFUSION MATRIX VISUALIZATION ==================
cm = confusion_matrix(y_true, y_pred, labels=[1, 0])

plt.figure(figsize=(6, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="coolwarm",
    linewidths=1,
    linecolor='gray',
    xticklabels=["Relevant", "Irrelevant"],
    yticklabels=["Relevant", "Irrelevant"]
)
plt.title("Heatmap of the NLP-Based Recommender Evaluation", fontsize=14, weight='bold')
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.tight_layout()

# ✅ Save the heatmap image to the project root
output_path = os.path.join(BASE_DIR, "evaluation_heatmap.png")
plt.savefig(output_path, dpi=300)
plt.show()

print(f"\n✅ Heatmap successfully generated and saved at: {output_path}")
