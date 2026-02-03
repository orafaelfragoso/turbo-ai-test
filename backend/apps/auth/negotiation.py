"""
Custom content negotiation for API versioning.
"""

from rest_framework.negotiation import DefaultContentNegotiation


class VendorContentNegotiation(DefaultContentNegotiation):
    """
    Custom content negotiation that handles vendor-specific media types.
    
    Allows vendor media types like application/vnd.noteapp.v1+json to
    be handled by the JSONRenderer.
    """

    def select_renderer(self, request, renderers, format_suffix=None):
        """
        Select the appropriate renderer for the request.
        
        If the Accept header contains our vendor media type, treat it as
        application/json for renderer selection.
        """
        accept_header = request.META.get("HTTP_ACCEPT", "")
        
        # If vendor media type is requested, normalize it to application/json
        if "vnd.noteapp" in accept_header and "+json" in accept_header:
            # Temporarily modify the Accept header for content negotiation
            original_accept = request.META.get("HTTP_ACCEPT")
            request.META["HTTP_ACCEPT"] = "application/json"
            
            try:
                result = super().select_renderer(request, renderers, format_suffix)
                return result
            finally:
                # Restore original Accept header
                if original_accept:
                    request.META["HTTP_ACCEPT"] = original_accept
                else:
                    request.META.pop("HTTP_ACCEPT", None)
        
        return super().select_renderer(request, renderers, format_suffix)
