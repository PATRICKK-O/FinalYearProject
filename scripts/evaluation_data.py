import os
import django
import csv
import spacy

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")
django.setup()

from django.contrib.auth.models import User
from material.models import Material, UserActivity
from material.utils.recommender_helper import get_recommendations_for_user

nlp = spacy.load("en_core_web_md")

# Relevance rules
RELATED_SUBJECTS = {
    "maths": ["physics", "chemistry"],
    "physics": ["maths", "chemistry"],
    "chemistry": ["physics", "maths"],
    "english": []
}
LEVEL_ORDER = {"beginner": 1, "intermediate": 2, "advanced": 3}


def is_relevant(pred_subj, pred_lvl, true_subj, true_lvl):
    """Decide if predicted material is relevant given the true activity."""
    if pred_subj == true_subj:
        return True
    if true_subj in RELATED_SUBJECTS and pred_subj in RELATED_SUBJECTS[true_subj]:
        return True
    return False


def level_progression_allowed(pred_lvl, true_lvl):
    """Allow same or higher level (progression)."""
    return LEVEL_ORDER.get(pred_lvl, 1) >= LEVEL_ORDER.get(true_lvl, 1)

# CSV output setup
output_file = "evaluation_data.csv"
fields = [
    "username", "user_id",
    "activity_subject", "activity_level", "activity_timestamp",
    "recommended_material_id", "recommended_name",
    "recommended_subject", "recommended_level",
    "similarity_score",   # decimal between 0..1
    "y_true", "y_pred"
]

# 6) Build dataset and write CSV
rows_written = 0
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fields)

    users = User.objects.all()
    for user in users:
        # fetch recent activities
        recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:5]
        if not recent_activities.exists():
            continue

        # Build list of materials user interacted with (for similarity calculations)
        interacted_materials = []
        for act in recent_activities:
            # We will also store the timestamp for context
            interacted_materials += list(Material.objects.filter(subject=act.subject, level=act.level))

        if not interacted_materials:
            continue

        # Get recommendations from your recommender (top_k degree handled in that function)
        recommended_materials = get_recommendations_for_user(user)

        # For each recommended material compute the avg similarity vs user's seen materials
        for rec in recommended_materials:
            # compute average similarity between this recommended material and the seen materials
            candidate_doc = nlp(rec.description.lower())
            total_score = 0.0
            count = 0
            for seen in interacted_materials:
                seen_doc = nlp(seen.description.lower())
                total_score += seen_doc.similarity(candidate_doc)
                count += 1
            avg_score = total_score / count if count > 0 else 0.0

            # Evaluate relevance using your rule functions.
            # Note: y_true is 1 because we are evaluating for a real user activity case (we compare recommended vs actual recent activities)
            # y_pred = 1 if considered relevant by our criteria, else 0
            # To be explicit: loop through each recent activity and mark a match if any recent activity validates the recommendation.
            matched = False
            for act in recent_activities:
                true_subj = act.subject.lower()
                true_lvl = act.level.lower()
                pred_subj = rec.subject.lower()
                pred_lvl = rec.level.lower()

                if is_relevant(pred_subj, pred_lvl, true_subj, true_lvl) and level_progression_allowed(pred_lvl, true_lvl):
                    matched = True
                    break

            y_true = 1
            y_pred = 1 if matched else 0

            row = [
                user.username,
                user.id, # type: ignore
                # Use fields from the most recent activity for context (you can extend to record each activity separately)
                recent_activities[0].subject if recent_activities else "",
                recent_activities[0].level if recent_activities else "",
                recent_activities[0].timestamp.isoformat() if recent_activities else "",
                rec.id,
                rec.name,
                rec.subject,
                rec.level,
                f"{avg_score:.6f}",  # similarity score (0..1)
                y_true,
                y_pred
            ]
            writer.writerow(row)
            rows_written += 1

print(f"✅ Done — wrote {rows_written} rows to {output_file}")
print(f"File location: {os.path.abspath(output_file)}")
