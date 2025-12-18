from django.views import View
from django.views.generic import ListView, TemplateView, DetailView, FormView, CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404, render,redirect
from .models import ServiceCategory, ServiceItem, Tutorial, AboutGalleryImage
from django.urls import reverse, reverse_lazy
from .forms import ContactForm
from django.contrib import messages
from django.db.models import Count, Prefetch
from django.utils.functional import cached_property
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .forms import ServiceCategoryForm, ServiceItemForm
from services.views_staff import StaffStepUpRequiredMixin
from django.db.models import Q
from django.core.paginator import Paginator


# Home
class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # 6 دسته‌بندی اول + پیش‌بارگذاری تصویر و شمارش تعداد سرویس‌ها
        ctx['home_categories'] = (ServiceCategory.objects
                                  .prefetch_related('services')
                                  .all()[:6])
        # اگر خواستی سرویس‌های شاخص نشان دهی (اختیاری)
        ctx['featured_services'] = (ServiceItem.objects
                                    .select_related('category')
                                    .all()[:6])
        return ctx

# AboutUs

# class AboutUsView(TemplateView):
#     template_name = 'about.html'
class AboutUsView(View):
    def get(self, request):
        gallery = AboutGalleryImage.objects.filter(is_active=True).order_by('order', 'id')[:4]
        # map_link = "https://www.google.com/maps/dir/?api=1&destination=35.767272,51.365705"
        map_link = "https://www.google.com/maps/dir/?api=1&destination=35.77271102801292,51.37177763824688"

        return render(request, 'about.html', {'gallery': gallery, 'map_link': map_link})

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

# صفحات کاربری شما (بدون تغییر اساسی)
class ServiceCategoryListView(ListView):
    model = ServiceCategory
    template_name = "services_list.html"
    context_object_name = "service_categories"


class ServiceCategoryDetailView(DetailView):
    model = ServiceCategory
    template_name = "service_category_detail.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services"] = self.object.services.all()
        return ctx




class StaffCatalogManageView(StaffStepUpRequiredMixin, PermissionRequiredMixin, View):
    """
    صفحه یک‌پارچهٔ مدیریت کاتالوگ:
      - بالا: دو فرم ایجاد (کشویی)
      - پایین: لیست دسته‌ها و خدمت‌ها (کشویی)
      - ویرایش در صفحات جدا انجام می‌شود (دیگر اینجا نمایش داده نمی‌شود)
    """
    template_name = "services/staff/catalog_manage.html"
    permission_required = ("services.view_servicecategory", "services.view_serviceitem")

    def get(self, request):
        categories = ServiceCategory.objects.annotate(services_count=Count("services")).order_by("title")
        services   = ServiceItem.objects.select_related("category").order_by("name")

        cat_form = ServiceCategoryForm()
        srv_form = ServiceItemForm()

        return render(request, self.template_name, {
            "categories": categories,
            "services": services,
            "cat_form": cat_form,
            "srv_form": srv_form,
        })

    def post(self, request):
        action = request.POST.get("action")

        # ایجاد دسته
        if action == "create_category":
            # اجازهٔ add
            if not request.user.has_perm("services.add_servicecategory"):
                messages.error(request, "اجازهٔ ایجاد دسته را ندارید.")
                return redirect("staff_catalog")

            form = ServiceCategoryForm(request.POST, request.FILES)
            if form.is_valid():
                obj = form.save()
                messages.success(request, "دستهٔ خدمات ایجاد شد.")
                return redirect(reverse("staff_catalog"))
            messages.error(request, "فرم دسته معتبر نیست.")
            return self.get(request)

        # ایجاد خدمت
        if action == "create_service":
            if not request.user.has_perm("services.add_serviceitem"):
                messages.error(request, "اجازهٔ ایجاد خدمت را ندارید.")
                return redirect("staff_catalog")

            form = ServiceItemForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "خدمت جدید ایجاد شد.")
                return redirect(reverse("staff_catalog"))
            messages.error(request, "فرم خدمت معتبر نیست.")
            return self.get(request)

        # حذف دسته
        if action == "delete_category":
            if not request.user.has_perm("services.delete_servicecategory"):
                messages.error(request, "اجازهٔ حذف دسته را ندارید.")
                return redirect("staff_catalog")

            slug = request.POST.get("slug")
            obj  = get_object_or_404(ServiceCategory, slug=slug)
            name = obj.title
            obj.delete()
            messages.success(request, f"«{name}» حذف شد.")
            return redirect("staff_catalog")

        # حذف خدمت
        if action == "delete_service":
            if not request.user.has_perm("services.delete_serviceitem"):
                messages.error(request, "اجازهٔ حذف خدمت را ندارید.")
                return redirect("staff_catalog")

            pk   = request.POST.get("pk")
            obj  = get_object_or_404(ServiceItem, pk=pk)
            name = obj.name
            obj.delete()
            messages.success(request, f"«{name}» حذف شد.")
            return redirect("staff_catalog")

        messages.error(request, "اقدام نامعتبر است.")
        return redirect("staff_catalog")


# صفحات ویرایش جدا (دیگر داخل manage نمایش نمی‌دهیم)
class StaffCategoryUpdateView(StaffStepUpRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ServiceCategory
    form_class = ServiceCategoryForm
    template_name = "services/staff/category_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("staff_catalog")
    permission_required = ("services.change_servicecategory",)

    def form_valid(self, form):
        messages.success(self.request, "تغییرات دسته ذخیره شد.")
        return super().form_valid(form)


class StaffServiceItemUpdateView(StaffStepUpRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ServiceItem
    form_class = ServiceItemForm
    template_name = "services/staff/serviceitem_form.html"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("staff_catalog")
    permission_required = ("services.change_serviceitem",)

    def form_valid(self, form):
        messages.success(self.request, "تغییرات خدمت ذخیره شد.")
        return super().form_valid(form)





# Tutorials

class TutorialListView(ListView):
    template_name = "tutorials/list.html"
    context_object_name = "items"
    paginate_by = 12

    def get_queryset(self):
        q = (self.request.GET.get("q") or "").strip()
        qs = (Tutorial.objects
              .filter(is_published=True)
              .only("id","title","slug","description","cover","created_at"))
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(lessons__title__icontains=q) |
                Q(lessons__description__icontains=q)
            ).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()
        paginator = ctx.get("paginator")
        total_count = paginator.count if paginator else len(ctx["object_list"])
        ctx.update({
            "q": q,
            "total_count": total_count,  # برای شمارندهٔ «تعداد دسته‌ها»
        })
        return ctx


class TutorialDetailView(DetailView):
    template_name = "tutorials/detail.html"
    context_object_name = "tutorial"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # فقط آموزش‌های منتشرشده
        return Tutorial.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()

        # فهرست سرفصل‌ها با فیلتر و صفحه‌بندی
        lessons_qs = self.object.lessons.all().order_by('id')
        if q:
            lessons_qs = lessons_qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )

        paginator = Paginator(lessons_qs, 10)  # 10 سرفصل در هر صفحه
        page_number = self.request.GET.get("page")
        lessons_page = paginator.get_page(page_number)

        # اولین سرفصل فیلترشده برای پخش اولیه
        first_lesson = lessons_qs.first()

        ctx.update({
            "q": q,
            "lessons": lessons_page,            # صفحهٔ جاری سرفصل‌ها
            "lessons_total": paginator.count,   # شمارندهٔ «تعداد سرفصل‌ها»
            "is_paginated_lessons": lessons_page.has_other_pages(),
            "first_lesson": first_lesson,
        })
        return ctx