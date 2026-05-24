from django.conf import settings
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_staff or u.is_superuser)

class StaffStepUpRequiredMixin(StaffRequiredMixin):
    stepup_session_key = 'staff_stepup_verified_at'

    def dispatch(self, request, *args, **kwargs):
        # اول: حتماً استاف باشد
        if not self.test_func():
            return self.handle_no_permission()

        # دوم: Step-Up اخیر دارد؟
        ts = request.session.get(self.stepup_session_key)
        max_age_min = int(getattr(settings, 'STAFF_STEPUP_MAX_AGE_MINUTES', 30))
        now_ts = timezone.now().timestamp()

        if not ts or (now_ts - float(ts)) > (max_age_min * 60):
            # مقصد بعد از تأیید
            request.session['staff_next'] = request.get_full_path()
            return redirect('staff_stepup')

        return super().dispatch(request, *args, **kwargs)