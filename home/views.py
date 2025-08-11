from django.views import View
from django.views.generic import ListView,TemplateView,DetailView,FormView
from django.shortcuts import get_object_or_404, render,redirect
from .models import ServiceCategory, ServiceItem
from django.urls import reverse_lazy
from .forms import ContactForm
from django.contrib import messages
# Home
class HomePageView(TemplateView):
    template_name = 'home.html'

# AboutUs

# class AboutUsView(TemplateView):
#     template_name = 'about.html'
class AboutUsView(View):
    def get(self, request):
        team = [
            {"name": "الهام جعفری", "role": "مدیر سالن", "image": "team/elaham.jpg"},
            {"name": "سارا محمدی", "role": "متخصص پوست و مو", "image": "team/sara.jpg"},
            {"name": "نازنین احمدی", "role": "متخصص ناخن", "image": "team/nazanin.jpg"},
        ]
        # map_link = "https://www.google.com/maps/dir/?api=1&destination=35.767272,51.365705"
        map_link = "https://www.google.com/maps/dir/?api=1&destination=35.77271102801292,51.37177763824688"

        return render(request, 'about.html', {'team': team, 'map_link': map_link})

# ContactUs


class ContactUsView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد ✅")
            return redirect('contact')
        else:
            messages.error(request, "لطفاً تمام فیلدها را به درستی پر کنید.")
        return render(request, 'contact.html', {'form': form})




# Service

class ServiceCategoryListView(ListView):
    model = ServiceCategory
    template_name = 'services_list.html'
    context_object_name = 'service_categories'


class ServiceCategoryDetailView(DetailView):
    model = ServiceCategory
    template_name = 'service_category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.object.services.all()
        return context



# Tutorials

class TutorialsView(TemplateView):
    template_name = 'tutorials.html'