from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RulesPageView(TemplateView):
    template_name = 'pages/rules.html'


def custom500(request):
    return render(request, 'pages/500.html', status=500)


def custom404(request, exception=None):
    return render(request, 'pages/404.html', status=404)


def custom403(request, exception=None):
    return render(request, 'pages/403csrf.html', status=403)
