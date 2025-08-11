from django.contrib.auth.mixins import UserPassesTestMixin
from kavenegar import *

from datetime import datetime
from django.utils import timezone
import pytz

def make_tehran_aware(dt: datetime) -> datetime:
    """تبدیل datetime naive به datetime با منطقه زمانی تهران"""
    if timezone.is_naive(dt):
        tehran_tz = pytz.timezone("Asia/Tehran")
        return tehran_tz.localize(dt)
    return timezone.localtime(dt, pytz.timezone("Asia/Tehran"))


def send_otp_code(phone_number, code):
	try:
		api = KavenegarAPI('666C3434664F5A5567696F674F46395966306D4A6D39394A71434976784F484C64443667716A68425159453D')
		params = {
			'sender': '2000660110',
			'receptor': phone_number,
			'message': f'{code} کد تایید شما '
		}
		response = api.sms_send(params)
		print(response)
	except APIException as e:
		print(e)
	except HTTPException as e:
		print(e)


class IsAdminUserMixin(UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_authenticated and self.request.user.is_admin


