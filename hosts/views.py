import json
import boto3
import uuid

from django.views       import View
from django.http        import JsonResponse
from django.db          import transaction
from django.db          import IntegrityError
from django.db.models   import Count

from core.utils         import signin_decorator  
from hosts.models       import Host
from rooms.models       import Category, Room, Facility, RoomFacility, RoomType, Image

from my_settings        import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, IMAGE_URL, AWS_BUCKET_NAME

class HostingRoomView(View):
    @signin_decorator
    def post(self, request):
        data = request.POST 

        try:
            host = Host.objects.get(user=request.user)   
            
            name              = data['name']
            address           = data['address']
            detail_address    = data['detail_address']
            price             = data['price']
            description       = data['description']
            latitude          = data['latitude']
            longitude         = data['longitude']
            maximum_occupancy = data['maximum_occupancy']
            bedroom           = data['bedroom']
            bathroom          = data['bathroom']
            bed               = data['bed']
            host              = data['host_id']    
            category          = data['category_id']
            room_type         = data['room_type_id']
            facility_ids      = data.getlist('facility_id')  

            files = request.FILES.getlist('files')

            if not Category.objects.filter(id=category).exists():
                return JsonResponse({'message':'CATEGORY_DOES_NOT_EXIST'}, status=404)
                
            if not RoomType.objects.filter(id=room_type).exists():
                return JsonResponse({'message':'ROOM_TYPE_DOES_NOT_EXIST'}, status=404)
            
            
            if not Facility.objects.filter(id__in=facility_ids)\
                                   .aggregate(count=Count('id'))\
                                   .get('count') == len(facility_ids):
                return JsonResponse({'message':'FACILITY_DOES_NOT_EXIST'}, status=404)
                
            with transaction.atomic():
                room, created = Room.objects.get_or_create(
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
                        "host"              : Host.objects.get(id=host),
                        "category"          : Category.objects.get(id=category),
                        "room_type"         : RoomType.objects.get(id=room_type)
                    }
                )
                
                if not created:
                    return JsonResponse({'message':'ROOM_NAME_ALREADY_EXIST'}, status=400)
                    
                created_room_id = Room.objects.latest('id').id    
                    
                RoomFacility.objects.bulk_create([
                    RoomFacility(
                        room_id = Room.objects.latest('id').id, 
                        room_facility_id = facility_id
                    ) for facility_id in facility_ids  ])

                for file in files:
                    file._set_name(str(uuid.uuid4()))
                    s3r = boto3.resource('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, 
                                            aws_secret_access_key = AWS_SECRET_ACCESS_KEY)
                    s3r.Bucket(AWS_BUCKET_NAME).put_object(Key = host + '/%s'%(file), 
                                                           Body=file, 
                                                           ContentType='jpg')
                    Image.objects.create(
                        url     = IMAGE_URL + '/' + f'{host}/{file}',
                        room_id = created_room_id
                    )
                
            images = Image.objects.filter(room_id = created_room_id).all()

            data = {
                "id"            : room.id,
                "name"          : room.name,
                "room_images"   : [image.url for image in images]
            }
            
            return JsonResponse({'message':'SUCCESS', 'room':data}, status=201)

        except Host.DoesNotExist:
            return JsonResponse({'message':'HOST_DOES_NOT_EXIST'}, status=404)
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        
        except IntegrityError:
            return JsonResponse({'message':'UNKNOWN_DATA'}, status=400)
        
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