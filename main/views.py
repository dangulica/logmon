from django.shortcuts import render

# Create your views here.


def homepage(request):
    return render(request, 'main/homepage.html', {})


def faq(request):
    return render(request, 'main/faq.html', {'title': 'FAQ Page'})


def denied(request):
    return render(request, 'main/denied.html')
