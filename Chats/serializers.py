from rest_framework import serializers
from .models import User, chat, participant, message


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    photo_user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name_user',
            'photo_user',
            'token'
        ]

    def get_token(self, obj):
        return self.context.get('token')

    def get_photo_user(self, obj):

        request = self.context.get('request')

        if obj.photo_user:

            return request.build_absolute_uri(
                obj.photo_user.url
            )

        return None



#-------------------------------------------------------------Mensajes Consultar Todos

class participantsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name_user')
    email = serializers.CharField(source='user.email')
    photo = serializers.SerializerMethodField()
    is_online = serializers.BooleanField(source='user.is_online')

    class Meta: 
        model = participant
        fields = [
            'user', 
            'name', 
            'email', 
            'photo', 
            'is_online'
            ]

    def get_photo(self, obj):
        request = self.context.get('request')
        photo = obj.user.photo_user

        if photo:
            return request.build_absolute_uri(photo.url)
        return None    


class messageSerializer(serializers.ModelSerializer):

    image_message = serializers.SerializerMethodField()

    file_message = serializers.SerializerMethodField()

    class Meta:
        model = message

        fields = [
            'id',
            'text_message',
            'time_message',
            'view_message',
            'file_message',
            'image_message',
            'resend_message',
            'user'
        ]

    def get_image_message(self, obj):

        request = self.context.get('request')

        if obj.image_message:

            return request.build_absolute_uri(
                obj.image_message.url
            )

        return None

    def get_file_message(self, obj):

        request = self.context.get('request')

        if obj.file_message:

            return request.build_absolute_uri(
                obj.file_message.url
            )

        return None


class chatSerializer(serializers.ModelSerializer):

    participants = participantsSerializer(
        source='participant_set',
        many=True
    )

    last_message = serializers.SerializerMethodField()

    class Meta:
        model = chat

        fields = [
            'id',
            'name_chat',
            'chat_grupal',
            'block_chat',
            'admin',
            'participants',
            'last_message'
        ]

    def get_last_message(self, obj):

        last = obj.message_set.order_by(
            '-time_message'
        ).first()

        if last:

            return messageSerializer(
                last,
                context=self.context
            ).data

        return None


#-------------------------------------------------------Usuarios consultar especificos

class buscarUsuarioGrupalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 
            'email',
            'name_user',
            'photo_user'
            ]





















#--------------------------------------Ejemplo de Serializer
# class juegosSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = juegos
#         fields = '__all__'
