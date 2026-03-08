"""
Views for browsing and filtering materials
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from ..models import Material, UserActivity, SearchHistory, SavedMaterial
from ..form import MaterialFilterForm
from .utils import get_timestamp_context, get_saved_material_ids


def index(request):
    """Landing page view"""
    context = get_timestamp_context()
    return render(request, 'index.html', context)


@login_required
def home(request):
    """Main home page with material filtering"""
    context = get_timestamp_context()
    
    form = MaterialFilterForm()
    materials = []
    recommended_materials = []
    cold_start = False
    
    # Load recent search history from session
    recent_searches = []
    if request.user.is_authenticated:
        recent_searches = list(
            SearchHistory.objects.filter(user=request.user)
            .order_by('-timestamp')
            .values_list('query', flat=True)[:4]
        )
    
    saved_material_ids = get_saved_material_ids(request.user)
    
    if request.method == "POST":
        form = MaterialFilterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            level = form.cleaned_data['level']
            material_types = form.cleaned_data['material_types']
            
            # Save user activity
            UserActivity.objects.create(
                user=request.user,
                subject=subject,
                level=level
            )
            
            # Filter materials
            materials = Material.objects.filter(subject=subject, level=level)
            if material_types:
                materials = materials.filter(material_types__in=material_types)
            materials = materials.distinct()
    
    return render(request, 'home.html', {
        "form": form,
        "materials": materials,
        "recommended_materials": recommended_materials,
        "cold_start": cold_start,
        "recent_searches": recent_searches,
        "saved_material_ids": saved_material_ids,
        "context": context
    })


@login_required
def recommended(request):
    """View for showing recommended materials based on filters"""
    saved_material_ids = get_saved_material_ids(request.user)
    
    if request.method == "POST": 
        subject = request.POST.get('subject')
        level = request.POST.get('level')
        
        material_types = request.POST.getlist('material_types')
        material_types = [int(mt) for mt in material_types] if material_types else []
        
        materials = Material.objects.filter(
            subject=subject,
            level=level
        )
        
        if material_types:
            materials = materials.filter(material_types__id__in=material_types)
            
        materials = materials.distinct()
        
        if not material_types:
            return redirect('/home/')  
            
        return render(request, 'recommended.html', {
            "materials": materials,
            "selected_types": material_types,
            "saved_material_ids": saved_material_ids
        })  
    
    return render(request, 'recommended.html', {
        "materials": [],
        "saved_material_ids": saved_material_ids
    })


@login_required
def trending_materials(request):
    """View for showing trending materials based on user activity"""
    # Get most interacted materials based on activity count
    trending = (
        UserActivity.objects.values('subject', 'level')
        .annotate(activity_count=Count('id'))
        .order_by('-activity_count')
    )
    
    trending_materials = []
    seen_pairs = set()
    
    for item in trending:
        subject = item['subject']
        level = item['level']
        if (subject, level) not in seen_pairs:
            materials = Material.objects.filter(subject=subject, level=level)[:1]
            trending_materials += list(materials)
            seen_pairs.add((subject, level))
        if len(trending_materials) >= 4:
            break
    
    saved_material_ids = get_saved_material_ids(request.user)
    
    return render(request, 'trending.html', {
        'trending_materials': trending_materials,
        'saved_material_ids': saved_material_ids
    })