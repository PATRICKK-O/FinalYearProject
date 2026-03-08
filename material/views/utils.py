"""
Shared utilities and constants for material views
"""
import spacy
from datetime import datetime

# Load spaCy model once
nlp = spacy.load("en_core_web_md")

# Related subjects mapping
RELATED_SUBJECTS = {
    "maths": ["physics", "chemistry"],
    "physics": ["maths", "chemistry"],
    "chemistry": ["physics", "maths"],
    "english": []
}

# Search stopwords
STOPWORDS = {'and', 'the', 'of', 'in', 'to', 'a', 'an'}


def get_timestamp_context():
    """Return a context dict with current timestamp"""
    return {'timestamp': datetime.now().timestamp()}


def normalize_course_name(course):
    """Normalize course name to standard format"""
    course = course.lower()
    if course in ["maths", "mathematics"]:
        return "maths"
    elif course in ["physics"]:
        return "physics"
    elif course in ["chemistry"]:
        return "chemistry"
    elif course in ["english"]:
        return "english"
    return course


def get_saved_material_ids(user):
    """Get list of saved material IDs for a user"""
    from ..models import SavedMaterial
    
    if not user.is_authenticated:
        return []
    
    return list(
        SavedMaterial.objects.filter(user=user).values_list('material_id', flat=True)
    )