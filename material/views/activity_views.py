"""
Views for tracking user activity and interactions
"""
from django.shortcuts import redirect

from ..models import Material, UserActivity


def track_activity(request, material_id, type):
    """
    Track user activity when accessing materials and redirect to content
    
    Args:
        material_id: ID of the material being accessed
        type: Type of content being accessed ('pdf' or 'video')
    """
    try:
        material = Material.objects.get(id=material_id)
        
        # Record the activity
        UserActivity.objects.create(
            user=request.user,
            subject=material.subject,
            level=material.level
        )  
        
        # Redirect to appropriate content
        if type == "pdf" and material.pdf_file:
            return redirect(material.pdf_file.url)
        elif type == "video" and material.video_link:
            return redirect(material.video_link)
        else:
            return redirect('/home/')
            
    except Material.DoesNotExist:
        return redirect('/home/')