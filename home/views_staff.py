from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, FormView
from services.mixins import StaffStepUpRequiredMixin  # همانی که خودت داری
from .models import Tutorial, Lesson ,ContactMessage
from .forms import TutorialForm, LessonForm ,MessageReplyForm
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.mixins import PermissionRequiredMixin

class StaffTutorialCatalogView(StaffStepUpRequiredMixin, TemplateView):
    template_name = "staff/tutorials_catalog.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tutorial_form"] = TutorialForm()
        ctx["lesson_form"]   = LessonForm()
        ctx["tutorials"] = Tutorial.objects.all().prefetch_related("lessons")
        return ctx

# --- CRUD جداگانه برای ویرایش/حذف (خارج از کاتالوگ) ---
class StaffTutorialCreateView(StaffStepUpRequiredMixin, CreateView):
    template_name = "staff/tutorial_form.html"
    model = Tutorial
    form_class = TutorialForm
    success_url = reverse_lazy("staff_tutorials")
    def form_valid(self, form):
        messages.success(self.request,"آموزش ایجاد شد.")
        return super().form_valid(form)

class StaffTutorialUpdateView(StaffStepUpRequiredMixin, UpdateView):
    template_name = "staff/tutorial_form.html"
    model = Tutorial
    form_class = TutorialForm
    success_url = reverse_lazy("staff_tutorials")
    def form_valid(self, form):
        messages.success(self.request,"آموزش ویرایش شد.")
        return super().form_valid(form)

class StaffTutorialDeleteView(StaffStepUpRequiredMixin, DeleteView):
    template_name = "staff/tutorial_confirm_delete.html"
    model = Tutorial
    success_url = reverse_lazy("staff_tutorials")
    def delete(self, request, *a, **kw):
        messages.success(self.request,"آموزش حذف شد.")
        return super().delete(request,*a,**kw)

class StaffLessonCreateView(StaffStepUpRequiredMixin, CreateView):
    template_name = "staff/lesson_form.html"
    model = Lesson
    form_class = LessonForm
    success_url = reverse_lazy("staff_tutorials")
    def form_valid(self, form):
        messages.success(self.request,"سرفصل ایجاد شد.")
        return super().form_valid(form)

class StaffLessonUpdateView(StaffStepUpRequiredMixin, UpdateView):
    template_name = "staff/lesson_form.html"
    model = Lesson
    form_class = LessonForm
    success_url = reverse_lazy("staff_tutorials")
    def form_valid(self, form):
        messages.success(self.request,"سرفصل ویرایش شد.")
        return super().form_valid(form)

class StaffLessonDeleteView(StaffStepUpRequiredMixin, DeleteView):
    template_name = "staff/lesson_confirm_delete.html"
    model = Lesson
    success_url = reverse_lazy("staff_tutorials")
    def delete(self, request, *a, **kw):
        messages.success(self.request,"سرفصل حذف شد.")
        return super().delete(request,*a,**kw)



#       ContactMessage

class StaffMessageListView(StaffStepUpRequiredMixin, ListView):
    template_name = 'staff/messages_list.html'
    model = ContactMessage
    context_object_name = 'items'
    paginate_by = 20  # صفحه‌بندی
    # فیلترهای ساده: ?state=new|replied و جستجو: ?q=...
    def get_queryset(self):
        qs = ContactMessage.objects.all().order_by('-created_at')
        state = (self.request.GET.get('state') or 'all').lower()
        if state == 'new':
            qs = qs.filter(is_replied=False)
        elif state == 'replied':
            qs = qs.filter(is_replied=True)
        q = (self.request.GET.get('q') or '').strip()
        if q:
            qs = qs.filter(
                Q(full_name__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q) |
                Q(message__icontains=q)
            )
        return qs

class StaffMessageReplyView(StaffStepUpRequiredMixin, FormView):
    template_name = 'staff/message_reply.html'
    form_class = MessageReplyForm

    def dispatch(self, request, *args, **kwargs):
        self.obj = get_object_or_404(ContactMessage, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        ini = super().get_initial()
        ini['subject'] = self.obj.reply_subject or f'پاسخ به پیام شما - {self.obj.full_name}'
        return ini

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['obj'] = self.obj
        return ctx

    def form_valid(self, form):
        if not self.obj.email:
            messages.error(self.request, 'این پیام ایمیل ندارد؛ امکان پاسخ ایمیلی نیست.')
            return redirect('staff_messages')

        subject = form.cleaned_data['subject']
        body    = form.cleaned_data['body']
        recipients = [self.obj.email]
        if form.cleaned_data.get('send_copy_to_me'):
            if self.request.user and self.request.user.email:
                recipients.append(self.request.user.email)

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=recipients,
                fail_silently=False,
            )
        except Exception as e:
            messages.error(self.request, f'ارسال ایمیل ناموفق بود: {e}')
            return redirect('staff_message_reply', pk=self.obj.pk)

        # ذخیره وضعیت پاسخ (اگر فیلدها را در مدل گذاشته‌اید)
        self.obj.is_replied   = True
        self.obj.replied_at   = timezone.now()
        self.obj.replied_by   = getattr(self.request, 'user', None)
        self.obj.reply_subject = subject
        self.obj.reply_body    = body
        self.obj.save(update_fields=['is_replied','replied_at','replied_by','reply_subject','reply_body'])

        messages.success(self.request, 'پاسخ ایمیلی ارسال شد.')
        return redirect('staff_messages')


class StaffMessageDeleteView(StaffStepUpRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(ContactMessage, pk=pk)
        obj.delete()
        messages.success(request, "پیام کاربر حذف شد.")
        return redirect('staff_messages')


class StaffMessagesDeleteAllView(StaffStepUpRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        count = ContactMessage.objects.count()
        if count:
            ContactMessage.objects.all().delete()
            messages.success(request, f'تمام {count} پیام با موفقیت حذف شد.')
        else:
            messages.info(request, 'پیامی برای حذف وجود ندارد.')
        return redirect('staff_messages')