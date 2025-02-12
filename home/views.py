from django.shortcuts import render
from django.views.generic import ListView,TemplateView
# Create your views here.



class HomePageView(TemplateView):
    template_name = 'home_page/home_page.html'



class AboutUsView(TemplateView):
    pass