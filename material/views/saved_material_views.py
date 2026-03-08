"""
Views for managing saved materials (bookmarks)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Material, SavedMaterial


@login_required
def save_material(request, material_id):
    """Save/bookmark a material for the current user"""
    material = get_object_or_404(Material, id=material_id)
    SavedMaterial.objects.get_or_create(user=request.user, material=material)
    
    return redirect(request.META.get('HTTP_REFERER', '/home/'))


@login_required
def saved_materials(request):
    """View all saved materials for the current user"""
    saved = SavedMaterial.objects.filter(
        user=request.user
    ).select_related('material').order_by('-saved_at')
    
    return render(request, 'saved_materials.html', {
        'saved_materials': saved
    })


@login_required
def remove_saved_material(request, material_id):
    """Remove a material from user's saved list"""
    material = get_object_or_404(Material, id=material_id)
    SavedMaterial.objects.filter(user=request.user, material=material).delete()
    
    return redirect(request.META.get('HTTP_REFERER', '/home/'))