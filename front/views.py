from django.views import View
from django.shortcuts import render

class StaticView(View):
    def get(self, request):
        if request.path == '/':
            path = 'index.html'
        else:
            path = request.path[1:] + '.html'
        try:
            return render(request, path)
        except:
            return render(request, 'index.html')
