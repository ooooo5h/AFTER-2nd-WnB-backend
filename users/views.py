import json
import requests
import jwt
import bcrypt

from django.conf        import settings
from django.forms       import ValidationError
from django.http        import JsonResponse
from django.views       import View
from core.utils         import check_email, check_first_name, check_last_name, check_password, check_phone_number, signin_decorator

from users.models       import User

class KakaoOauthView(View):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')

        KAKAO_URL = 'https://kapi.kakao.com/v2/user/me'
        HEADER    = {'Authorization': f'Bearer {token}'}

        user_info = requests.get(KAKAO_URL,headers=HEADER).json()
        
        kakao_id          = user_info['id']
        kakao_profile_img = user_info['kakao_account']['profile']['profile_image_url']
        email             = user_info['kakao_account']['email']
    
        user, created = User.objects.get_or_create(
            kakao_id = kakao_id,
            defaults = {
                'kakao_profile_img': kakao_profile_img,
                'email'            : email
            }
        ) 
    
        if not created:
            user.kakao_proifile_img = kakao_profile_img
            user.save()
                        
        token = jwt.encode({'id':user.id}, settings.SECRET_KEY, settings.ALGORITHM)
    
        return JsonResponse({'message':'SUCCESS', 'token':token}, status=201 if created else 200)

class UserAdditionalInfoView(View):
    @signin_decorator
    def patch(self, request):
        try: 
            user = request.user
            data = json.loads(request.body)
            
            first_name   = data['first_name']
            last_name    = data['last_name']
            phone_number = data['phone_number']
            birth_day    = data['birth_day']
                      
            check_first_name(first_name)
            check_last_name(last_name)
            check_phone_number(phone_number)
            
            if User.objects.filter(phone_number = phone_number):
                return JsonResponse({'message':'PHONE_NUMBER_ALREADY_EXIST'}, status=400)
            
            user.first_name   = first_name
            user.last_name    = last_name
            user.phone_number = phone_number
            user.birth_day    = birth_day
            user.save()

            return JsonResponse({'message':'USER_INFO_UPDATED'}, status=201)
            
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        
        except ValidationError as e:
            return JsonResponse({'message':f'{e}'}, status=400)
        
class SignUpView(View):
    def post(self, request):        
        try :
            data         = json.loads(request.body)

            first_name   = data['first_name']
            last_name    = data['last_name']
            email        = data['email']
            password     = data['password']
            phone_number = data['phone_number']

            check_first_name(first_name)
            check_last_name(last_name)
            check_email(email)
            check_password(password)
            check_phone_number(phone_number)
        
            email_exist_user = User.objects.filter(email=email)
            
            if email_exist_user:
                return JsonResponse({'message':'EMAIL_ALREADY_EXIST'}, status=409)
            
            phone_exist_user = User.objects.filter(phone_number=phone_number) 

            if phone_exist_user:
                return JsonResponse({'message':'PHONE_ALREADY_EXIST'}, status=409)
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            User.objects.create(
                first_name   = first_name,
                last_name    = last_name,
                email        = email,
                phone_number = phone_number,
                password     = hashed_password
            )
            
            return JsonResponse({'message':'USER_CREATED'}, status=201)
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        except ValidationError as e:
            return JsonResponse({'message': f'{e}'}, status=400)
        