from api import models


class SiteSelectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before  the view (and later middleware) are called.
        try:
            domain = request.META['HTTP_HOST']
            site = models.Site.objects.get(domain=domain)
        except:
            site = models.Site.objects.filter(active=True).first()
        request.site = site

        response = self.get_response(request)
        # Code to be executed for each request/response after the view is called.

        return response
