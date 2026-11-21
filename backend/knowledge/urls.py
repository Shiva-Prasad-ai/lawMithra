from django.urls import re_path
from .views import (
    LegalChatView,
    CaseAnalysisView,
    LegalGlossaryView,
    SupportedLanguagesView,
    StatutoryTranslateView,
    ChatSessionListView,
    ChatSessionDetailView,
)

urlpatterns = [
    re_path(r'^chat/?$', LegalChatView.as_view(), name='knowledge-chat'),
    re_path(r'^sessions/?$', ChatSessionListView.as_view(), name='knowledge-session-list'),
    re_path(r'^sessions/(?P<session_id>[0-9a-f-]+)/?$', ChatSessionDetailView.as_view(), name='knowledge-session-detail'),
    re_path(r'^case-analysis/?$', CaseAnalysisView.as_view(), name='knowledge-case-analysis'),
    re_path(r'^glossary/?$', LegalGlossaryView.as_view(), name='knowledge-glossary'),
    re_path(r'^languages/?$', SupportedLanguagesView.as_view(), name='knowledge-languages'),
    re_path(r'^translate/?$', StatutoryTranslateView.as_view(), name='knowledge-translate'),
]

