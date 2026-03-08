"""
Search and search suggestion views
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from ..models import Material, UserActivity, SearchHistory
from .utils import nlp, STOPWORDS, get_saved_material_ids


def search(request):
    """Main search view with NLP-powered search"""
    query = request.POST.get('query', '').strip()
    materials = []
    saved_material_ids = []
    
    if query:
        doc = nlp(query.lower())
        search_terms = [
            token.lemma_ for token in doc
            if not token.is_stop and not token.is_punct and token.text not in STOPWORDS
        ]
        search_terms = list(set(search_terms))
        
        if search_terms:
            search_filter = Q()
            for term in search_terms:
                search_filter |= Q(keywords__icontains=term)
                search_filter |= Q(description__icontains=term)
                
            materials = Material.objects.filter(search_filter).distinct()  
            
            # Rank the materials by relevance
            materials = sorted(
                materials,
                key=lambda x: sum(
                    2 * sum(term in x.keywords.lower() for term in search_terms) + # type: ignore
                    sum(term in x.description.lower() for term in search_terms)
                    for term in search_terms
                ),
                reverse=True
            )
            
            if request.user.is_authenticated and materials:
                top = materials[0]
                
                # Track search interaction
                UserActivity.objects.create(
                    user=request.user,
                    subject=top.subject,
                    level=top.level
                )
                
                # Save search history to database
                if not SearchHistory.objects.filter(user=request.user, query=top.name).exists():
                    SearchHistory.objects.create(
                        user=request.user,
                        query=top.name
                    )
    
    if request.user.is_authenticated:
        saved_material_ids = get_saved_material_ids(request.user)
    
    return render(request, 'search.html', {
        'query': query,
        'materials': materials,
        'saved_material_ids': saved_material_ids
    })


def search_suggestions(request):
    """AJAX endpoint for search autocomplete suggestions"""
    if request.method == "POST":
        query = request.POST.get('query', '').strip()
        suggestions = []
        
        if query:
            doc = nlp(query.lower())
            search_terms = [
                token.lemma_ for token in doc 
                if not token.is_stop and not token.is_punct
            ]
            
            materials = (
                Material.objects.filter(keywords__icontains=query) | 
                Material.objects.filter(description__icontains=query)
            )
            
            # Use set to avoid duplicates
            keyword_suggestions = set()
            
            for material in materials:
                for keyword in material.keywords.split(", "): # type: ignore
                    if all(term in keyword.lower() for term in search_terms):
                        keyword_suggestions.add(keyword)
            
            keyword_suggestions = sorted(
                list(keyword_suggestions),
                key=lambda x: sum(term in x.lower() for term in search_terms),
                reverse=True
            )      
            
            suggestions = keyword_suggestions[:7]
            
        return JsonResponse({"suggestions": suggestions})
        
    return JsonResponse({"suggestions": []})