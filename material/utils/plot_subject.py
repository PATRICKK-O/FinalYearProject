import os
import sys
import django
import matplotlib.pyplot as plt
from collections import Counter

# ==========================
# Django Environment Setup
# ==========================

# Add the project root directory to the system path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmrs.settings")
django.setup()

from material.models import Material


def plot_subject_distribution(output_path="subject_distribution.png"):
    """
    Generates a pie chart showing the distribution of study materials by subject.
    Saves the chart as a PNG file and displays it.
    """

    # Fetch all materials
    materials = Material.objects.all()
    if not materials.exists():
        print("⚠️ No materials found in the database.")
        return

    # Count subjects
    subjects = [m.subject.capitalize() for m in materials]
    subject_counts = Counter(subjects)

    # Prepare data
    labels = list(subject_counts.keys())
    values = list(subject_counts.values())

    # Create pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=['#3498db', '#2ecc71', '#f1c40f', '#9b59b6']
    )
    plt.title('Distribution of Study Materials by Subject', fontsize=13, fontweight='bold')
    plt.tight_layout()

    # Save and show
    plt.savefig(output_path, dpi=300)
    plt.show()

    print(f"✅ Subject distribution plot saved successfully as '{output_path}'.")


if __name__ == "__main__":
    plot_subject_distribution()
