"""
Custom renderers for API responses.
"""

from rest_framework.renderers import JSONRenderer


class VendorJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that supports vendor-specific media types.
    
    Supports both standard application/json and our custom vendor media type
    for versioning: application/vnd.noteapp.vX+json
    """

    media_type = "application/json"
    format = "json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render data to JSON, supporting custom vendor media types.
        """
        # If the accepted media type is our vendor format, we still render as JSON
        if accepted_media_type and "vnd.noteapp" in accepted_media_type:
            # Override to render as standard JSON
            accepted_media_type = "application/json"
        
        return super().render(data, accepted_media_type, renderer_context)
