"""
Tenant Isolation Middleware
───────────────────────────
Attaches the current landlord to the request so views can
filter querysets without repeating the FK check everywhere.
"""


class TenantIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach landlord context to every authenticated request
        if request.user.is_authenticated:
            if request.user.role == 'landlord':
                request.landlord = request.user
            elif request.user.role == 'tenant':
                request.landlord = None   # tenant sees only their own data
            else:
                request.landlord = None
        else:
            request.landlord = None

        response = self.get_response(request)
        return response
