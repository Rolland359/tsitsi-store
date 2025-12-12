from django.shortcuts import render
from .models import AboutPage

# Create your views here.
def about_view(request):
    info = AboutPage.objects.all().first()
    return render(request, 'aboutus/about.html', {'info': info})
