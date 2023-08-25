import os
import sys
import django
import jwt
from asgiref.sync import sync_to_async
from django.conf import settings

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EasyChannel.settings.dev")
django.setup()
from apps.account.models import UserInfo
from typing import Optional


@sync_to_async
def decode_jwt(token: str) -> Optional[UserInfo]:
    salt = settings.JWT_CONF.get('salt', settings.SECRET_KEY)  # 盐
    typ = settings.JWT_CONF.get('typ', 'HS256')  #
    payload = jwt.decode(
        token, salt, typ
    )
    payload.pop('exp')
    try:
        user = UserInfo.objects.get(**payload)
        return user
    except UserInfo.DoesNotExist:
        return None
