from django.urls import path
from .views import (
    LegalChatView,
    CaseAnalysisView,
    LegalGlossaryView,
    SupportedLanguagesView,
    StatutoryTranslateView
)

urlpatterns = [
    path('chat/', LegalChatView.as_view(), name='knowledge-chat'),
    path('case-analysis/', CaseAnalysisView.as_view(), name='knowledge-case-analysis'),
    path('glossary/', LegalGlossaryView.as_view(), name='knowledge-glossary'),
    path('languages/', SupportedLanguagesView.as_view(), name='knowledge-languages'),
    path('translate/', StatutoryTranslateView.as_view(), name='knowledge-translate'),
]

