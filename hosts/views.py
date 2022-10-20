import json
import uuid
import boto3

from django.views       import View
from django.http        import JsonResponse
from django.db          import transaction
from django.db.models   import Count

from core.utils         import signin_decorator  
from hosts.models       import Host
from rooms.models       import Category, Room, Facility, RoomFacility, RoomType, Image

from my_settings        import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, IMAGE_URL, AWS_BUCKET_NAME
        
class RegisterHostView(View):
    @signin_decorator
    def post(self, request):
        
        user = request.user

        host_already_exist, is_created = Host.objects.get_or_create(
            user_id = user.id
        )        
        
        host_name = host_already_exist.user.last_name + host_already_exist.user.first_name
        
        if is_created:
            return JsonResponse({'message':'SUCCESS', 'data':{'HOST_NAME':f'{host_name}'}}, status=201)

        return JsonResponse({'message':'ALREADY_REGISTERED', 'data':{'HOST_NAME':f'{host_name}'}}, status=409)
    
class RegisterRoomView(View):
    @signin_decorator
    def post(self, request):
        data         = request.POST

        try:
            host = Host.objects.get(user=request.user)   
            
            name              = data['room_name']
            address           = data['state/province/region']
            detail_address    = data['detail_address']
            price             = data['price']
            description       = data['description']
            latitude          = data['latitude']
            longitude         = data['longitude']
            maximum_occupancy = data['maximum_occupancy']
            bedroom           = data['bedroom']
            bathroom          = data['bathroom']
            bed               = data['bed']
            category          = data['category_id']
            room_type         = data['room_type_id']
            facility_ids      = data.getlist('facility_ids')  # 리스트로 담김 ['1', '2', '4']
            files             = request.FILES.getlist('files')  # 이미지 첨부

            # 1. 키에러 => key error
            
            # 2. 호스트로 등록된 유저가 아닐 경우 => does not exist 
            
            # 3. category_id 존재여부
            if not Category.objects.filter(id=category).exists():
                return JsonResponse({'message':'CATEGORY_DOES_NOT_EXIST'}, status=404)    
            
            # 4. room_type_id 존재여부
            if not RoomType.objects.filter(id=room_type).exists():
                return JsonResponse({'message':'ROOM_TYPE_DOES_NOT_EXIST'}, status=404)
            
            # 5. facility_ids 존재여부
            count_exist_facility_ids = Facility.objects.filter(id__in=facility_ids).aggregate(count=Count('id')).get('count')
            
            if count_exist_facility_ids != len(facility_ids):
                return JsonResponse({'message':'FACILITY_DOES_NOT_EXIST'}, status=404)        
  
            with transaction.atomic():
                room, is_created = Room.objects.get_or_create(
                    name = name,
                    defaults = {
                        "address"           : address,
                        "detail_address"    : detail_address,
                        "price"             : price,
                        "description"       : description,
                        "latitude"          : latitude,
                        "longitude"         : longitude,
                        "maximum_occupancy" : maximum_occupancy,
                        "bedroom"           : bedroom,
                        "bathroom"          : bathroom,
                        "bed"               : bed,
                        "host"              : host,
                        "category"          : Category.objects.get(id=category),
                        "room_type"         : RoomType.objects.get(id=room_type)
                    }
                )
                
                # 6. 룸 이름 중복 불가
                if not is_created:
                    return JsonResponse({'message':'ROOM_NAME_ALREADY_EXIST'}, status=409)
                
                # 7. room생성하고 room_facilities도 생성해야함. => 트랜잭션 처리
                RoomFacility.objects.bulk_create([
                    RoomFacility(
                        room_id = room.id,
                        room_facility_id = facility_id
                    ) for facility_id in facility_ids ])
                
                # 집 이미지 등록하기
                for file in files:  
                    file._set_name(str(uuid.uuid4()))
                    s3 = boto3.resource('s3', 
                                        aws_access_key_id     = AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
                    
                    # S3에 object저장하기
                    s3.Bucket(AWS_BUCKET_NAME).put_object(Key         = str(host.id) + f'/{file}',    # 호스트 id별로 폴더 생성해서 관리
                                                          Body        = file,
                                                          ContentType = 'jpg')
                                        
                    # DB에 저장하기
                    Image.objects.create(                           
                        url     = IMAGE_URL + f'/{host.id}/{file}',   # 저장할 url 형식 지정
                        room_id = room.id
                    )
                    
                # 저장된 이미지 파일 가져와서 내보내주기
                images = Image.objects.filter(room_id = room.id).all()
                       
                room_info = {
                    "id"        : room.id,
                    "room_name" : room.name,
                    "address"   : room.address + room.detail_address,
                    "price"     : room.price,
                    "bedroom"   : room.bedroom,
                    "bathroom"  : room.bathroom,
                    "bed"       : room.bed,
                    "host_name" : room.host.user.last_name + room.host.user.first_name,
                    "category"  : room.category.name,
                    "room_type" : room.room_type.name,
                    "facilities": [room_facility.room_facility.name for room_facility in RoomFacility.objects.filter(room = room.id).all()],
                    "images"    : [image.url for image in images]
                }
            
                return JsonResponse({'message':'SUCCESS', 'data':{'room_info':room_info}}, status=201)         

        except Host.DoesNotExist:
            return JsonResponse({'message':'ONLY_HOST_CAN_REGISTER_HOUSE'}, status=403)
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)