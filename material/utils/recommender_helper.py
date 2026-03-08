import spacy
from ..models import Material, UserActivity

nlp = spacy.load("en_core_web_md")

def get_recommendations_for_user(user, top_k=5):
    # Get recent user activities
    recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:5]
    interacted_materials = []

    for activity in recent_activities:
        interacted_materials += list(Material.objects.filter(
            subject=activity.subject,
            level=activity.level
        ))

    if not interacted_materials:
        return []  # cold start user

    # Get all other materials not yet interacted with
    all_materials = Material.objects.exclude(id__in=[m.id for m in interacted_materials])

    # Compute NLP similarity scores
    scored_materials = []
    for candidate in all_materials:
        candidate_doc = nlp(candidate.description.lower())
        total_score = 0
        count = 0
        for seen in interacted_materials:
            seen_doc = nlp(seen.description.lower())
            total_score += seen_doc.similarity(candidate_doc)
            count += 1
        avg_score = total_score / count if count > 0 else 0
        scored_materials.append((candidate, avg_score))

    # Sort and return top-k
    scored_materials.sort(key=lambda x: x[1], reverse=True)
    recommended = [item[0] for item in scored_materials[:top_k]]
    return recommended