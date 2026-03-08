from django.shortcuts import render, redirect, get_object_or_404
from .form import MaterialFilterForm
from .models import Material, UserActivity, SearchHistory, SavedMaterial
from django.db.models import Q
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from random import sample
from django.db.models import Count
from django.utils.timezone import now 
import spacy



nlp = spacy.load("en_core_web_md")

def index(request):
  context = {
    'timestamp': datetime.now().timestamp()
  }
  return render(request, 'index.html', context)


RELATED_SUBJECTS = {
  "maths": ["physics", "chemistry"],
  "physics": ["maths", "chemistry"],
  "chemistry": ["physics", "maths"],
  "english": []
}

@login_required
def home(request):
  context = {
    'timestamp': datetime.now().timestamp()
  }
  
  form = MaterialFilterForm()
  materials = []
  recommended_materials = []
  cold_start = False
  
  # Load recent search history from session
  recent_searches = []
  if request.user.is_authenticated:
    recent_searches = list(
      SearchHistory.objects.filter(user=request.user).order_by('-timestamp').values_list('query', flat=True)[:4]
    )
  
  saved_material_ids = list(
    SavedMaterial.objects.filter(user=request.user).values_list('material_id', flat=True)
  )  
  
  if request.method == "POST":
    form = MaterialFilterForm(request.POST)
    if form.is_valid():
      subject = form.cleaned_data['subject']
      level = form.cleaned_data['level']
      material_types = form.cleaned_data['material_types']
      
      # Here we save user activity
      UserActivity.objects.create(
        user = request.user,
        subject = subject,
        level = level
      )
      
      # filter materials
      materials = Material.objects.filter(subject = subject, level = level)
      if material_types:
        materials = materials.filter(material_types__in=material_types)
      materials = materials.distinct()
  
  """
    else: 
    # Phase 1: Get recent user activities      
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:5]
    interacted_materials = []
    
    for activity in recent_activities:
      interacted_materials += list(Material.objects.filter(
        subject = activity.subject,
        level = activity.level
      ))
    
    if interacted_materials:
      # Phase 2: NLP similarity-based recommendation
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
    
      # Sort by similarity  
      scored_materials.sort(key=lambda x: x[1], reverse=True)  
      recommended_materials = [item[0] for item in scored_materials[:5]]
      
    else:
      # Phase 3: Cold start based on course of interest
      cold_start = True
      course = request.user.profile.course_of_interest.lower()
      
      beginner_qs = list(Material.objects.filter(subject=course, level='beginner'))
      beginner_sample = sample(beginner_qs, 2) if len(beginner_qs) >= 2 else beginner_qs
      
      # Get keywords from beginner materials
      seen_keywords = set()
      for mat in beginner_sample:
        if mat.keywords:
          seen_keywords.update([kw.strip() for kw in mat.keywords.lower().split(',')])
      
      # Try to find 1 progressive material (intermediate or advanced) that matches beginner keywords  
      next_levels = ['intermediate', 'advanced']  
      next_material = Material.objects.filter(
        subject = course,
        level__in=next_levels
      ).filter(
        Q(keywords__iregex=r'(' + '|'.join(seen_keywords) + ')')
      ).exclude(id__in=[m.id for m in beginner_sample]).first() # type: ignore
      
      recommended_materials = beginner_sample
      if next_material:
        recommended_materials.append(next_material)
  """    
  
        
  return render(request, 'home.html', {
    "form": form,
    "materials": materials,
    "recommended_materials": recommended_materials, # harmless for template reuse
    "cold_start": cold_start,
    "recent_searches": recent_searches,
    "saved_material_ids": saved_material_ids,
    "context": context
  })


def track_activity(request, material_id, type):
  try:
    material = Material.objects.get(id=material_id)
    
    UserActivity.objects.create(
      user = request.user,
      subject = material.subject,
      level = material.level
    )  
    
    if type == "pdf" and material.pdf_file:
      return redirect(material.pdf_file.url)
    elif type == "video" and material.video_link:
      return redirect(material.video_link)
    else:
      return redirect('/home/')
  except Material.DoesNotExist:
    return redirect('/home/')


@login_required
def recommended(request):
  saved_material_ids = []
  if request.user.is_authenticated:
    saved_material_ids = list(
      SavedMaterial.objects.filter(user=request.user).values_list('material_id', flat=True)
    )
  
  if request.method == "POST": 
    subject = request.POST.get('subject') # Get subject
    level = request.POST.get('level')     # Get level
    
    material_types = request.POST.getlist('material_types') # gets list of selected materials [1, 2] or [1]
    # The code below checks if material_types is true,then converts the string, else it returns an empty list
    material_types = [int(mt) for mt in material_types] if material_types else []
    materials = Material.objects.filter(
      subject = subject,
      level = level
    )
    
    if material_types:
      materials = materials.filter(material_types__id__in = material_types)
      
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



STOPWORDS = {'and', 'the', 'of', 'in', 'to', 'a', 'an'}
def search(request):
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
      
      # Here we rank the materials   
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
          user = request.user,
          subject = top.subject,
          level = top.level
        )
        
        # Save search history to database
        if not SearchHistory.objects.filter(user=request.user, query=top.name).exists():
          SearchHistory.objects.create(
            user = request.user,
            query = top.name
          )
  
  if request.user.is_authenticated:
    saved_material_ids = list(
      SavedMaterial.objects.filter(user=request.user).values_list('material_id', flat=True)
    )
  
  # Fetch saved material IDs if logged in  
  return render(request, 'search.html', {
    'query': query,
    'materials': materials,
    'saved_material_ids': saved_material_ids
  })  
  
def search_suggestions(request):
  if request.method == "POST":
    query = request.POST.get('query', '').strip()
    suggestions = []
    
    if query:
      doc = nlp(query.lower())
      search_terms = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
      
      materials = Material.objects.filter(keywords__icontains=query) | Material.objects.filter(description__icontains=query)
      # We use set to avoid duplicates
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


@login_required
def trending_materials(request):
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
      materials = Material.objects.filter(subject = subject, level = level)[:1]
      trending_materials += list(materials)
      seen_pairs.add((subject, level))
    if len(trending_materials) >= 4:
      break
  
  saved_material_ids = []
  if request.user.is_authenticated:
    saved_material_ids = list(
      SavedMaterial.objects.filter(user=request.user).values_list('material_id', flat=True)
    )
  
  return render(request, 'trending.html', {
    'trending_materials': trending_materials,
    'saved_material_ids': saved_material_ids
  }) 
  

@login_required
def load_recommendations(request):
  recommended_materials = [] 
  cold_start = False
  context = {
    'timestamp': datetime.now().timestamp()
  }
  
  # For save button logic
  saved_material_ids = list(
    SavedMaterial.objects.filter(user=request.user).values_list('material_id', flat=True)
  )
  
  # Check if recommendations are already cached in session
  if 'cached_recommendations' in request.session:
    ids = request.session['cached_recommendations']
    recommended_materials = list(Material.objects.filter(id__in=ids))
    cold_start = request.session.get('cold_start', False)
  else:  
    # Phase 1: Get last 5 interactions
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:5]
    interacted_materials = []
    
    for activity in recent_activities:
      interacted_materials += list(Material.objects.filter(
        subject = activity.subject,
        level = activity.level
      )) 
    
    if interacted_materials:
      # Phase 2: NLP similarity-based recommendation
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
      recommended_materials = [item[0] for item in scored_materials[:5]]
    else:
      # Phase 3: Cold Start using course_of_interest
      cold_start = True
      course = request.user.profile.course_of_interest.lower()
      if course in ["maths", "mathematics"]:
        course = "maths"
      elif course == "physics":
          course = "physics"
      elif course == "chemistry":
          course = "chemistry"
      elif course == "english":
          course = "english"
      
      beginner_qs = list(Material.objects.filter(subject__iexact=course, level='beginner'))
      beginner_sample = sample(beginner_qs, 2) if len(beginner_qs) >= 2 else beginner_qs    
      
      seen_keywords = set()
      for mat in beginner_sample:
        if mat.keywords:
          seen_keywords.update([kw.strip() for kw in mat.keywords.lower().split(',')])
      
      next_levels = ['intermediate', 'advanced']
      next_material = Material.objects.filter(
        subject = course,
        level__in=next_levels
      ).filter(
        Q(keywords__iregex=r'(' + '|'.join(seen_keywords) + ')')
      ).exclude(id__in=[m.id for m in beginner_sample]).first() # type: ignore
      
      recommended_materials = beginner_sample
      if next_material:
        recommended_materials.append(next_material)
    
    # Cache the recommendations in session    
    request.session['cached_recommendations'] = [m.id for m in recommended_materials] # type: ignore
    request.session['cold_start'] = cold_start    
    
  return render(request, 'partials/recommendations_block.html', {
    'recommended_materials': recommended_materials,
    'cold_start': cold_start,
    'saved_material_ids': saved_material_ids,
    'context': context
  })         


@login_required
def save_material(request, material_id):
  material = get_object_or_404(Material, id=material_id)
  SavedMaterial.objects.get_or_create(user=request.user, material=material)
  
  return redirect(request.META.get('HTTP_REFERER', '/home/'))         


@login_required
def saved_materials(request):
  saved = SavedMaterial.objects.filter(user=request.user).select_related('material').order_by('-saved_at')
  
  return render(request, 'saved_materials.html', {'saved_materials': saved}) 


@login_required
def remove_saved_material(request, material_id):
  material = get_object_or_404(Material, id=material_id)
  SavedMaterial.objects.filter(user=request.user, material=material).delete()
  
  return redirect(request.META.get('HTTP_REFERER', '/home/'))
     