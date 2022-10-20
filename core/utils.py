import jwt    
import re

from django.conf            import settings
from django.core.exceptions import ValidationError
from django.http            import JsonResponse

from users.models           import User

def signin_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token        = request.headers.get('Authorization')   
            payload      = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
            request.user = User.objects.get(id = payload['id'])
            
            return func(self, request, *args, **kwargs)
            
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status=400)
        
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message':'INVALID_TOKEN'}, status=400)
    return wrapper

def check_first_name(value):
    if not re.match('^[ㄱ-ㅎ|가-힣]+$', value):
        raise ValidationError("CHECK_FIRST_NAME")
    
def check_last_name(value):
    if not re.match('^[ㄱ-ㅎ|가-힣]+$', value):
        raise ValidationError("CHECK_LAST_NAME")
    
def check_phone_number(value):
    if not re.match('^01([0|1|6|7|8|9])-([0-9]{3,4})-([0-9]{4})$', value):
        raise ValidationError("CHECK_PHONE_NUMBER")
    
def check_email(value):
    if not re.match('^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$', value):
        raise ValidationError("CHECK_EMAIL")
    
def check_password(value):
    if not re.match('^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$', value):
        raise ValidationError("CHECK_PASSWORD")
