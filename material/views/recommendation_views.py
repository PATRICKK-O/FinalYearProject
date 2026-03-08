"""
AI-powered recommendation engine views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from random import sample

from ..models import Material, UserActivity
from .utils import nlp, get_timestamp_context, get_saved_material_ids, normalize_course_name


@login_required
def load_recommendations(request):
    """
    Load personalized recommendations using NLP similarity.
    Falls back to cold start logic if no user activity exists.
    """
    recommended_materials = []
    cold_start = False
    context = get_timestamp_context()

    # For save button logic
    saved_material_ids = get_saved_material_ids(request.user)

    # ✅ Use cached recommendations if available
    if 'cached_recommendations' in request.session:
        ids = request.session['cached_recommendations']
        recommended_materials = list(Material.objects.filter(id__in=ids))
        cold_start = request.session.get('cold_start', False)
    else:
        # Phase 1: Get last 5 interactions
        recent_activities = UserActivity.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:5]

        interacted_materials = [
            material for activity in recent_activities
            for material in Material.objects.filter(
                subject=activity.subject,
                level=activity.level
            )
        ]

        # Phase 2: NLP similarity recommendations (if history exists)
        if interacted_materials:
            recommended_materials = get_nlp_recommendations(interacted_materials)
        else:
            # Phase 3: Cold Start for new users
            cold_start = True
            recommended_materials = get_cold_start_recommendations(request.user)

        # ✅ Cache the recommendations for reuse
        request.session['cached_recommendations'] = [m.id for m in recommended_materials]  # type: ignore
        request.session['cold_start'] = cold_start

    return render(request, 'partials/recommendations_block.html', {
        'recommended_materials': recommended_materials,
        'cold_start': cold_start,
        'saved_material_ids': saved_material_ids,
        'context': context
    })


def get_nlp_recommendations(interacted_materials):
    """
    Generate recommendations based on NLP similarity to user's past interactions.

    Args:
        interacted_materials (list): List of Material objects user has interacted with.

    Returns:
        list: Top recommended Material objects.
    """
    all_materials = Material.objects.exclude(
        id__in=[m.id for m in interacted_materials]
    )

    scored_materials = []
    for candidate in all_materials:
        candidate_doc = nlp(candidate.description.lower())
        total_score = 0
        count = 0

        for seen in interacted_materials:
            seen_doc = nlp(seen.description.lower())
            score = seen_doc.similarity(candidate_doc)
            total_score += score
            count += 1

        avg_score = total_score / count if count > 0 else 0
        scored_materials.append((candidate, avg_score))

    scored_materials.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in scored_materials[:5]]


def get_cold_start_recommendations(user):
    """
    Generate recommendations for new users (cold start phase)
    based on their selected course of interest.

    Args:
        user (User): The current user.

    Returns:
        list: Recommended Material objects for new users.
    """
    course = normalize_course_name(user.profile.course_of_interest)

    # Step 1: Fetch beginner-level materials
    beginner_qs = list(Material.objects.filter(
        subject__iexact=course,
        level='beginner'
    ))
    beginner_sample = sample(beginner_qs, 2) if len(beginner_qs) >= 2 else beginner_qs

    # Step 2: Collect keywords from beginner materials
    seen_keywords = set()
    for mat in beginner_sample:
        if mat.keywords:
            seen_keywords.update([kw.strip() for kw in mat.keywords.lower().split(',')])

    # Step 3: Recommend next-level materials with similar keywords
    next_levels = ['intermediate', 'advanced']
    next_material = Material.objects.filter(
        subject=course,
        level__in=next_levels
    ).filter(
        Q(keywords__iregex=r'(' + '|'.join(seen_keywords) + ')')
    ).exclude(id__in=[m.id for m in beginner_sample]).first()  # type: ignore

    recommended_materials = beginner_sample
    if next_material:
        recommended_materials.append(next_material)

    return recommended_materials
