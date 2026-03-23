# PSMRS — Personalized Study Material Recommender System
## Overview
PSMRS (Personalized Study Material Recommender System) is a Django-based web application that delivers intelligent, personalized study material recommendations to users using Natural Language Processing (NLP) and user behavior analysis.
Let’s be honest, when studying online, there are too many resources. PDFs, videos, tutorials… it quickly becomes overwhelming.
This project solves that problem by recommending materials that actually match what a user needs, based on:
* What they’re studying (course of interest)
* What they’ve interacted with before
* How similar materials are (using NLP)
## Key Features
* Personalized Recommendations (NLP-Based)
* Cold Start Handling for New Users
* User Activity Tracking (Behavior-Based Filtering)
* Search System with Suggestions & History
* Filtering by Subject and Difficulty Level
* Saved Materials (Bookmarking System)
* Trending Materials Page
* AJAX-Powered Dynamic Updates
* Session-Based Caching (Optimized Performance)
* Modern UI with Bootstrap & Custom Styling
## How It Works (Recommendation Pipeline)
The system uses a 3-phase content-based recommendation approach:
### 1. Cold Start (New Users)
When a user has no interaction history:
* Uses course_of_interest
* Recommends:
  * Beginner-level materials
  * Slightly advanced materials using keyword matching
### 2. Activity-Based Filtering
As the user starts interacting:
* Their actions are stored in the UserActivity model
* The system picks up patterns like:
  * Preferred subject
  * Difficulty level
This helps narrow down better recommendations.
### 3. NLP-Based Recommendation (Main Engine)
This is where the real intelligence comes in:
* Uses spaCy to process material descriptions
* Compares materials using:
  * Text similarity
  * Keywords
Then recommends the most similar and relevant content
### Backend
* Django (Python)
### Database
* MySQL
### NLP / Machine Learning
* spaCy
* scikit-learn
### Frontend
* HTML, CSS
* Bootstrap
* JavaScript
### Other Tools
* AJAX (for dynamic content)
* python-decouple (for environment variables)
## Future Improvements
* Hybrid Recommendation System (Content + Collaborative Filtering)
* User Analytics Dashboard
* Advanced NLP Models (e.g., Transformers/BERT)
* Cloud Deployment (AWS / Azure)
* Notification System for new recommendations
## Acknowledgements
* Open educational resources (e.g., OpenStax)
* Public learning platforms for video content
* Django & NLP communities
## Author
### Patrick Obekpa
Final Year Project — Computer Science
### License
This project is for academic and educational purposes.
