"""
Views for Multilingual Legal AI and Localization Engine.
Endpoints:
- POST /api/knowledge/chat/       (Legal AI Multilingual Assistant)
- GET  /api/knowledge/glossary/   (Legal Terminology Glossary)
- GET  /api/knowledge/languages/  (Supported Indian Languages)
- POST /api/knowledge/translate/  (Statutory-guarded translation)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .services.language_detector import SUPPORTED_LANGUAGES, detect_language
from .services.statutory_guard import StatutoryGuard
from .services.terminology import get_all_terms_for_language
from .services.legal_ai_service import LegalAIService
from .services.gemini_client import GeminiClient

legal_ai_service = LegalAIService()


class CaseAnalysisView(APIView):
    """
    AI Legal Case Analysis API Endpoint.
    Takes a legal scenario or complaint text and returns a full 7-section structured JSON analysis.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="AI Legal Case Analysis",
        description="Comprehensive case analysis adhering to Indian statutory law, civil/criminal court procedure, timelines, and strategy.",
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        case_text = request.data.get('case_text') or request.data.get('query') or request.data.get('text', '')
        case_text = str(case_text).strip()
        if not case_text:
            return Response(
                {"error": "Legal case text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        lang = request.data.get('language') or request.data.get('preferred_language', 'en')
        gemini = GeminiClient()
        analysis = gemini.analyze_legal_case(case_text=case_text, language=lang)
        return Response(analysis, status=status.HTTP_200_OK)


class LegalChatView(APIView):
    """
    Multilingual Legal AI Conversation Endpoint.
    Accepts natural language legal questions in 10 Indian languages.
    Performs issue extraction, section retrieval, and returns dual-statute guidance.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Ask Multilingual Legal AI",
        description="Processes a legal question in any supported Indian language and returns remedies and verified sections.",
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        query_text = request.data.get('query', '').strip()
        if not query_text:
            return Response(
                {"error": "Legal question query is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # User's language preference
        user_lang = 'en'
        if request.user and request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_lang = request.user.profile.preferred_language or 'en'
        elif 'preferred_language' in request.data:
            user_lang = request.data.get('preferred_language', 'en')

        auto_detect = request.data.get('auto_detect_language', True)

        try:
            result = legal_ai_service.process_query(
                query_text=query_text,
                preferred_lang=user_lang,
                auto_detect_lang=auto_detect
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to process legal query: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LegalGlossaryView(APIView):
    """
    Returns legal terminology glossary across Indian languages.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get Legal Glossary",
        parameters=[
            OpenApiParameter('lang', OpenApiTypes.STR, description="Language code (e.g. kn, hi, ta)")
        ]
    )
    def get(self, request):
        lang = request.query_params.get('lang', 'en')
        terms = get_all_terms_for_language(lang)
        return Response({"language": lang, "terms": terms})


class SupportedLanguagesView(APIView):
    """
    Lists the 10 supported Indian languages with their native scripts.
    """
    permission_classes = [AllowAny]

    @extend_schema(summary="List Supported Indian Languages")
    def get(self, request):
        languages_list = [
            {'code': code, **meta}
            for code, meta in SUPPORTED_LANGUAGES.items()
        ]
        return Response({"languages": languages_list})


class StatutoryTranslateView(APIView):
    """
    Statutory-Guarded Machine Translation Endpoint.
    Never alters section numbers, penalties, fines, or statutory conditions.
    """
    permission_classes = [AllowAny]

    @extend_schema(summary="Translate Legal Text with Statutory Guard")
    def post(self, request):
        text = request.data.get('text', '')
        source_lang = request.data.get('source_language', 'en')
        target_lang = request.data.get('target_language', 'en')

        if not text:
            return Response({"error": "Text is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Mask statutory numbers
        masked, token_map = StatutoryGuard.mask_statutory_entities(text)

        # Attempt translation
        translated = None
        if legal_ai_service.bhashini.is_configured:
            translated = legal_ai_service.bhashini.translate(masked, source_lang, target_lang)
        elif legal_ai_service.indictrans.is_configured:
            translated = legal_ai_service.indictrans.translate(masked, source_lang, target_lang)

        final_translated = StatutoryGuard.unmask_statutory_entities(translated or text, token_map)
        is_preserved, missing = StatutoryGuard.validate_preservation(text, final_translated)

        return Response({
            "original": text,
            "translated": final_translated,
            "source_language": source_lang,
            "target_language": target_lang,
            "statutory_preserved": is_preserved,
            "engine": "bhashini" if legal_ai_service.bhashini.is_configured else "statutory_guard_local"
        })
