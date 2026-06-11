from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.db.models import Max
from django.db.models import Count

from .models import User, chat, favorite, message, participant
from .serializers import UserSerializer, chatSerializer, buscarUsuarioGrupalSerializer, messageSerializer


#------------------------------API login
@csrf_exempt
def login(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            email_traido = data.get("email")
            password_traido = data.get("password")
           
            user = authenticate(email=email_traido, password=password_traido)

            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                user.is_online = True
                user.save()

                serializer = UserSerializer(user, context={'token': token.key, 'request': request})

                return JsonResponse(serializer.data)

            else:
                return JsonResponse({'error': 'Usuario o contraseña incorrectos'})

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#---------------------------------Crear cuenta
@csrf_exempt
def create_user(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            
            email_traido= data.get("email")
            password_traido= data.get("password")
            name_traido= data.get("name_user")
            lastName_traido= data.get("lastName_user")
            image_traido= data.get("photo_user")
            
            if User.objects.filter(email = email_traido).exists():
                return JsonResponse({'Mensaje': 'Este email ya tiene una cuenta'})



            user= User.objects.create_user(
                email= email_traido,
                password= password_traido,
                name_user= name_traido,
                lastName_user= lastName_traido,
                username= email_traido
            )

            token, created = Token.objects.get_or_create(user=user)

            return JsonResponse({
                'Mensaje': 'Usuario creado correctamente',
                'token': token.key,
                'email': user.email,
                "name_user": user.name_user
            })

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#---------------------------------Crear Chat
@api_view(['POST'])
def crearChat(request):
    try:
        data = request.data
        id_usuario2 = data.get("id_usuario2")

        usuario1 = request.user
        usuario2 = User.objects.get(id=id_usuario2)

        chat_existente = chat.objects.filter(
            chat_grupal=False,
            participant__user=usuario1
        ).filter(
            participant__chat__participant__user=usuario2
        ).annotate(
            num_participants=Count('participant')
        ).filter(
            num_participants=2
        ).first()

        if chat_existente:
            return JsonResponse({
                'mensaje': 'El chat ya existe',
                'chat_id': chat_existente.id
            })

        chat_obj = chat.objects.create(
            name_chat=f"{usuario1.name_user} - {usuario2.name_user}",
            admin=usuario1,
            block_chat=False,
            chat_grupal=False   
        )

        participant.objects.create(user=usuario1, chat=chat_obj)
        participant.objects.create(user=usuario2, chat=chat_obj)

        return JsonResponse({
            'mensaje': 'Chat creado correctamente',
            'chat_id': chat_obj.id
        })

    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#---------------------------------obtenerChat del usuario
@api_view(['GET'])
def obtenerChat(request):
    try:
        if request.method== 'GET':
            user= request.user

            chat_e = chat.objects.filter(
                participant__user=user
            ).annotate(
                last_time=Max('message__time_message')
            ).order_by('-last_time').distinct()

           
            serializer= chatSerializer(chat_e, many= True, context={'request': request})
            
            return JsonResponse(serializer.data, safe=False)

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})



#---------------------------------Obtener info del chat
@api_view(['POST'])
def obtenerInfoChat(request):

    try:

        data = request.data

        id_chat = data.get("id")

        chat_obj = chat.objects.get(
            id=id_chat
        )

        serializer = chatSerializer(

            chat_obj,

            context={
                'request': request
            }
        )

        return JsonResponse(
            serializer.data,
            safe=False
        )

    except Exception as e:

        return JsonResponse({
            'error': str(e)
        })
        

#----------------------------Consultar un chat en especifico
@api_view(['POST'])
def buscarMensaje(request):
    
    try:
        if request.method == 'POST':

            data = json.loads(request.body)
            texto = data.get("text")

            chats = chat.objects.filter(
                participant__user=request.user  # 🔐 usuario logueado
            ).filter(
                participant__user__name_user__icontains=texto  # 🔍 otro usuario
            ).distinct().order_by('chat_grupal')
  

            usuarios_con_chat = User.objects.filter(
                participant__chat__participant__user=request.user,
                participant__chat__chat_grupal=False
            ).exclude(id=request.user.id).distinct()


            usuarios = User.objects.filter(
                name_user__icontains=texto
            ).exclude(
                id__in=usuarios_con_chat.values_list('id', flat=True)
            ).exclude(
                id=request.user.id
            )

            chat_serializer = chatSerializer(chats, many= True, context={'request': request})
            user_serializer = UserSerializer(usuarios, many=True, context={'request': request})

            return JsonResponse({
                "chats": chat_serializer.data,
                "users": user_serializer.data
            })
                
        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})



#----------------------------Crear favoritos
@api_view(['POST'])
def crearFavorito(request):
    try:
        if request.method == 'POST':
            data = request.data
            id_chat = data.get("id")

            chat_obj = chat.objects.get(id=id_chat)

            favoritos, creado = favorite.objects.get_or_create(
                user=request.user,
                chat=chat_obj
            )
        
            if creado:
                return JsonResponse({'Mensaje': 'Guardado en favoritos'})
            else:
                return JsonResponse({'Mensaje': 'Ya estaba en favoritos'})

        return JsonResponse({'error': 'Método no permitido'})

    except chat.DoesNotExist:
        return JsonResponse({'error': 'Chat no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})



#---------------------------------bloquear Chat
@api_view(['POST'])
def bloquear(request):
    try:
        if request.method == 'POST':
            data = request.data
            id_chat = data.get("id")

            chat_obj = chat.objects.get(id=id_chat)

            chat_obj.block_chat = True
            chat_obj.save()
        
            return JsonResponse({'Mensaje': 'Chat bloqueado correctamente'})
         
        return JsonResponse({'error': 'Método no permitido'})

    except chat.DoesNotExist:
        return JsonResponse({'error': 'Chat no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})



#--------------------------------Salir del Chat
@api_view(['POST'])
def salirChat(request):
    try:
        if request.method == 'POST':
            id_chat = request.data.get("id")

            chat_obj = chat.objects.get(id=id_chat)

            # 🔥 eliminar al usuario del chat
            eliminado, _ = participant.objects.filter(
                chat=chat_obj,
                user=request.user
            ).delete()

            if eliminado > 0:
                return JsonResponse({'Mensaje': 'Saliste del chat'})
            else:
                return JsonResponse({'error': 'No perteneces a este chat'})
        
        return JsonResponse({'error': 'Método no permitido'})

    except chat.DoesNotExist:
        return JsonResponse({'error': 'Chat no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})
    

#--------------------------------Consultar usuarios para chat grupal
@api_view(['POST'])
def consultarUsuariosGrupal(request):
    try:
        if request.method == 'POST':
            data = request.data
            name = data.get("text")
            
            usuarios = User.objects.filter(name_user__icontains=name)

            serializer = buscarUsuarioGrupalSerializer(usuarios, many=True)

        
            return JsonResponse(serializer.data, safe=False)
         
        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#--------------------------------Nombre para chat Grupal
@api_view(['POST'])
def crearChatGrupal(request):
    try:
        data = request.data

        name_chat = data.get("name_chat")
        emails_ids = data.get("emails", [])

        #crear chat
        chat_obj = chat.objects.create(
            name_chat=name_chat,
            block_chat=False,
            admin=request.user
        )

        #Crear un participante (Participante logueado)
        participant.objects.create(
            user=request.user,
            chat=chat_obj
        )

        #agregar participantes
        for email_id in emails_ids:
            try:
                user_all = User.objects.get(email=email_id)

                participant.objects.create(
                    user=user_all,
                    chat=chat_obj
                )

            except User.DoesNotExist:
                continue  # ignora ids inválidos

        return JsonResponse({
            'Mensaje': 'Chat creado correctamente',
        })

    except Exception as e:
        return JsonResponse({'error': str(e)})



#-----------------------------------------------Cambiar el nombre del Chat
@api_view(['POST'])
def actualizarNombreChat(request):
    try:
        if request.method == 'POST':
            
            data = request.data
            id_chat = data.get("id")
            name = data.get("text")

            if not name:
                return JsonResponse({'Mensaje': 'Necesitas un nombre de chat'})


            chat_all = chat.objects.get(id= id_chat)
            chat_all.name_chat = name
            chat_all.save()
            
            return JsonResponse({'Mensaje': 'Nombre actualizado correctamente'})

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#------------------------------------------------Eliminar chat grupal
@api_view(['POST'])
def eliminarChatGrupal(request):
    try:
        if request.method == 'POST':
            id_chat = request.data.get("id")

            chat_obj = chat.objects.get(id=id_chat)

            # 🔥 eliminar mensajes
            message.objects.filter(chat=chat_obj).delete()

            # 🔥 eliminar participantes
            participant.objects.filter(chat=chat_obj).delete()

            # 🔥 eliminar chat
            chat_obj.delete()

            return JsonResponse({'Mensaje': 'Eliminado correctamente'})

        return JsonResponse({'error': 'Método no permitido'})

    except chat.DoesNotExist:
        return JsonResponse({'error': 'Chat no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#-------------------------------------Consultar Usuarios que pertenecen al chat
@api_view(['POST'])
def consultarUsuariosChat(request):
    try:
        if request.method == 'POST':
            data = request.data
            id_chat = data.get("id")
            
            usuarios = User.objects.filter(
            participant__chat__id=id_chat
            ).distinct()

            serializer = buscarUsuarioGrupalSerializer(usuarios, many=True)

            return JsonResponse(serializer.data, safe=False)
         
        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#-------------------------------------------Eliminar participantes del chat grupal
@api_view(['POST'])
def eliminarParticipante(request):
    try:
        if request.method == 'POST':
            id_chat = request.data.get("id")
            email_id = request.data.get("email")
            

            user_all = User.objects.get(email= email_id)
            chat_obj = chat.objects.get(id=id_chat)

            # 🔥 eliminar al usuario del chat
            eliminado, _ = participant.objects.filter(
                chat=chat_obj,
                user= user_all
            ).delete()

            if eliminado > 0:
                return JsonResponse({'Mensaje': 'Eliminado del chat'})
            else:
                return JsonResponse({'error': 'No pertenece a este chat'})
        
        return JsonResponse({'error': 'Método no permitido'})

    except chat.DoesNotExist:
        return JsonResponse({'error': 'Chat no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})

#-------------------------------------------Consultar Favoritos del usuario
@api_view(['GET'])
def obtenerChatFavoritos(request):
    try:
        if request.method== 'GET':
            user= request.user

            chat_favoritos= chat.objects.filter(
                participant__user=user,
                favorite__user=user
            ).annotate(
                last_time=Max('message__time_message')
            ).order_by('-last_time').distinct()
           
            serializer = chatSerializer(chat_favoritos, many= True, context={'request': request})
            
            return JsonResponse(serializer.data, safe=False)

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#------------------------------------------------Eliminar chat favorito
@api_view(['POST'])
def eliminarFavorito(request):
    try:
        if request.method == 'POST':
            id_chat = request.data.get("id")

            chat_obj = chat.objects.get(id=id_chat)

            user = request.user

            favorito = favorite.objects.get(
                user=user,
                chat=chat_obj
            )
            favorito.delete()  

            return JsonResponse({'Mensaje': 'Eliminado correctamente'})

        return JsonResponse({'error': 'Método no permitido'})

    except chat.DoesNotExist:
        return JsonResponse({'error': 'Favorito no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#----------------------------Buscar Favoritos
@api_view(['POST'])
def buscarChatFavoritos(request):
    
    try:
        if request.method == 'POST':
            user= request.user

            data = json.loads(request.body)
            texto = data.get("text")

            chats = chat.objects.filter(
                participant__user=user,
                favorite__user=user
            ).filter(
                participant__user__name_user__icontains=texto  # 🔍 otro usuario
            ).distinct()

            serializer = chatSerializer(chats, many= True)
           
            return JsonResponse(serializer.data, safe=False)
            

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#----------------------------------------Obtener Chats Bloqueados
@api_view(['GET'])
def obtenerChatBloqueado(request):
    try:
        if request.method== 'GET':
            user= request.user

            chat_bloqueados= chat.objects.filter(
                participant__user=user,
                block_chat=True
            ).annotate(
                last_time=Max('message__time_message')
            ).order_by('-last_time').distinct()
           
            serializer= chatSerializer(chat_bloqueados, many= True, context={'request': request})
            
            return JsonResponse(serializer.data, safe=False)

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})



#----------------------------Buscar bloqueados
@api_view(['POST'])
def buscarChatBloqueados(request):
    
    try:
        if request.method == 'POST':
            user= request.user

            data = json.loads(request.body)
            texto = data.get("text")

            chats = chat.objects.filter(
                participant__user=user,
                block_chat=True
            ).filter(
                participant__user__name_user__icontains=texto  # 🔍 otro usuario
            ).distinct()

            serializer = chatSerializer(chats, many= True)
           
            return JsonResponse(serializer.data, safe=False)
            

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#----------------------------desbloquear Chat
@api_view(['POST'])
def desbloquearChat(request):
    try:
        if request.method == 'POST':
            
            data = request.data
            id_chat = data.get("id")


            chat_all = chat.objects.get(id= id_chat)
            chat_all.block_chat = False
            chat_all.save()
            
            return JsonResponse({'Mensaje': 'Chat desbloqueado correctamente'})

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#-----------------------------------------------Cambiar el nombre y foto del usuario
@api_view(['POST'])
def  actualizarPerfilUsuario(request):
    try:

        user = request.user

        name = request.data.get("text")
        photo = request.FILES.get("photo_user")

        # Si no envía nada
        if not name and not photo:
            return JsonResponse({
                'error': 'Debes enviar un nombre o una foto'
            })

        # Actualizar nombre si viene
        if name:
            user.name_user = name

        # Actualizar foto si viene
        if photo:
            user.photo_user = photo

        user.save()

        return JsonResponse({
            'Mensaje': 'Perfil actualizado',
            'name_user': user.name_user,
            'email': user.email,
            'photo_user': request.build_absolute_uri(
                user.photo_user.url
            ) if user.photo_user else None
        })

    except Exception as e:

        return JsonResponse({
            'error': str(e)
        })

#----------------------------------------Cerrar sesión
@api_view(['POST'])
def logout(request):
    try:
        # eliminar token
        request.user.auth_token.delete()

        # opcional: marcar offline
        request.user.is_online = False
        request.user.save()

        return JsonResponse({'message': 'Sesión cerrada correctamente'})

    except Exception as e:
        return JsonResponse({'error': str(e)})





#------------------------------Enviar mensaje

@api_view(['POST'])
def enviarMensaje(request):

    try:

        user = request.user

        id_chat = request.data.get("id_chat")

        text_message = request.data.get("text_message")

        image_message = request.FILES.get("image_message")

        file_message = request.FILES.get("file_message")

        chat_obj = chat.objects.get(id=id_chat)

        nuevo_mensaje = message.objects.create(

            text_message=text_message,

            view_message=False,

            resend_message=False,

            image_message=image_message,

            file_message=file_message,

            chat=chat_obj,

            user=user
        )

        serializer = messageSerializer(
            nuevo_mensaje,
            context={'request': request}
        )

        return JsonResponse(serializer.data, safe=False)

    except chat.DoesNotExist:

        return JsonResponse({
            'error': 'Chat no existe'
        })

    except Exception as e:

        return JsonResponse({
            'error': str(e)
        })



#----------------------------Eliminar mensajes 
@api_view(['POST'])
def eliminarMensajes(request):
    try:
        if request.method == 'POST':
            id_mensaje = request.data.get("id")

            # 🔥 eliminar mensajes
            message.objects.get(id=id_mensaje).delete()

            return JsonResponse({'Mensaje': 'Eliminado correctamente'})

        return JsonResponse({'error': 'Método no permitido'})

    except message.DoesNotExist:
        return JsonResponse({'error': 'Mensaje no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#------------------------------Reenviar mensaje 
@api_view(['POST'])
def reenviarMensaje(request):
    try:
        if request.method == 'POST':
            data = request.data
            id_mensaje = data.get("id_mensaje")
            id_chat = data.get("id_chat")

            mensaje_obj = message.objects.get(id=id_mensaje)
            chat_obj = chat.objects.get(id=id_chat)

            # Crear nuevo mensaje con el mismo contenido pero diferente chat
            nuevo_mensaje = message.objects.create(
                chat=chat_obj,  
                user=request.user,                    
                text_message=mensaje_obj.text_message,          
                image_message=mensaje_obj.image_message,        
                file_message=mensaje_obj.file_message,  
                view_message=False,            
                resend_message=True                         
            )
                    

            return JsonResponse({'Mensaje': 'Mensaje reenviado correctamente'})

        return JsonResponse({'error': 'Método no permitido'})

    except chat.DoesNotExist:
        return JsonResponse({'error': 'Chat no existe'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


#-------------------------------Traer mensajes del chat
@api_view(['POST'])
def obtenerMensajes(request):
    try:
        if request.method== 'POST':
            user= request.user

            data = json.loads(request.body)
            id_chat = data.get("id")

            Chat_obj = chat.objects.get(id=id_chat)
            mensajes= message.objects.filter(
                chat=Chat_obj,
            ).order_by('time_message')
           
            serializer = messageSerializer(
                mensajes,
                many=True,
                context={'request': request}
            )
            
            return JsonResponse(serializer.data, safe=False)

        return JsonResponse({'error': 'Método no permitido'})

    except Exception as e:
        return JsonResponse({'error': str(e)})









#----------------------------------------------------EJEMPLOS DE CONSULTAS-------------------------

#----------------------------Consultar todos
# @csrf_exempt
# def VerJuegos(request):
    
#     try:
#         if request.method == 'GET':
#             biblioteca= juegos.objects.all()
#             serializer= juegosSerializer(biblioteca, many= True)
#             return JsonResponse(serializer.data, safe=False)
#         return JsonResponse({'error': 'Método no permitido'})

#     except Exception as e:
#         return JsonResponse({'error': 'Ha ocurrido un error'})   


# #----------------------------Consultar un tipo de dato
# @csrf_exempt
# def GeneroJuegos(request, genero):
    
#     try:
#         if request.method == 'POST':

#             JuegosGenero = juegos.objects.filter(genero_juegos=genero)
#             serializer = juegosSerializer(JuegosGenero, many=True)
#             return JsonResponse(serializer.data, safe=False)

#         return JsonResponse({'error': 'Método no permitido'})

#     except Exception as e:
#         return JsonResponse({'error': str(e)})



# #----------------------------Eliminar datos
# @csrf_exempt
# def EliminarJuego(request, id):
#     try:
#         if request.method == 'POST':
#             juego = juegos.objects.get(id=id)
#             juego.delete()
#             return JsonResponse({'mensaje': 'Juego eliminado correctamente'})

#     except juegos.DoesNotExist:
#         return JsonResponse({'error': 'Juego no encontrado'})


# #----------------------------Crear datos
# @csrf_exempt
# def crear_juego(request):
#     try:
#         if request.method == 'POST':
#             data = json.loads(request.body)
#             serializer= juegosSerializer(data= data)

#             if serializer.is_valid():
#                 serializer.save()   
#                 return JsonResponse({'Mensage': 'Creado correctamente'})

#         return JsonResponse({'error': 'Método no permitido'})

#     except Exception as e:
#         return JsonResponse({'error': str(e)})



# #----------------------------actualizar dato
# @csrf_exempt
# def actualizar_juego(request, id):
#     try:
#         if request.method == 'POST':

#             juego = juegos.objects.get(id=id)
#             data = json.loads(request.body)

#             serializer = juegosSerializer(juego, data=data)  

#             if serializer.is_valid():
#                 serializer.save()
#                 return JsonResponse({'Mensaje': 'Actualizado correctamente'})

#             return JsonResponse(serializer.errors)

#         return JsonResponse({'error': 'Método no permitido'})

#     except Exception as e:
#         return JsonResponse({'error': str(e)})


#--------------------------------Vaciar Chat
# @api_view(['POST'])
# def vaciarChat(request):
#     try:
#         if request.method == 'POST':
#             data = request.data
#             id_chat = data.get("id")

#             chat_obj = chat.objects.get(id=id_chat)

#             message.objects.filter(chat=chat_obj).delete()  # 🔥 eliminar todos los mensajes de ese chat
        
#             return JsonResponse({'Mensaje': 'Chat vaciado correctamente'})
         
#         return JsonResponse({'error': 'Método no permitido'})

#     except chat.DoesNotExist:
#         return JsonResponse({'error': 'Chat no existe'})
    
#     except Exception as e:
#         return JsonResponse({'error': str(e)})



#-----------------------------Consultar mensaje especifico

# Q(message__text_message__icontains=texto) |  # buscar en mensajes