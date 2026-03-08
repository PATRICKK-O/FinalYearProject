"""
Material app views package
Imports all view functions to maintain backward compatibility with URLs
"""

# Material browsing views
from .material_views import (
    index,
    home,
    recommended,
    trending_materials,
)

# Search views
from .search_views import (
    search,
    search_suggestions,
)

# Recommendation engine
from .recommendation_views import (
    load_recommendations,
)

# Saved materials
from .saved_material_views import (
    save_material,
    saved_materials,
    remove_saved_material,
)

# Activity tracking
from .activity_views import (
    track_activity,
)

# Make all views available at package level
__all__ = [
    # Material views
    'index',
    'home',
    'recommended',
    'trending_materials',
    
    # Search views
    'search',
    'search_suggestions',
    
    # Recommendation views
    'load_recommendations',
    
    # Saved material views
    'save_material',
    'saved_materials',
    'remove_saved_material',
    
    # Activity views
    'track_activity',
]