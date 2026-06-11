from django.urls import path
from .views import login, create_user, crearChat, obtenerChat, buscarMensaje, crearFavorito, bloquear, salirChat, consultarUsuariosGrupal, crearChatGrupal, actualizarNombreChat, eliminarChatGrupal, consultarUsuariosChat, eliminarParticipante, obtenerChatFavoritos, eliminarFavorito, buscarChatFavoritos, obtenerChatBloqueado, buscarChatBloqueados, desbloquearChat,  actualizarPerfilUsuario, logout, eliminarMensajes, reenviarMensaje, obtenerMensajes, enviarMensaje, obtenerInfoChat

urlpatterns = [
    path('login/', login),
    path('crearUsuario/', create_user),
    path('crearChat/', crearChat),
    path('obtenerChat/', obtenerChat),
    path('obtenerInfoChat/', obtenerInfoChat),
    path('buscarMensaje/', buscarMensaje),
    path('crearFavorito/', crearFavorito),
    path('bloquear/', bloquear),
    path('salirChat/', salirChat),
    path('consultarUsuariosGrupal/', consultarUsuariosGrupal),
    path('crearChatGrupal/', crearChatGrupal),
    path('actualizarNombreChat/', actualizarNombreChat),
    path('eliminarChatGrupal/', eliminarChatGrupal),
    path('consultarUsuariosChat/', consultarUsuariosChat),
    path('eliminarParticipante/', eliminarParticipante),
    path('obtenerChatFavoritos/', obtenerChatFavoritos),
    path('eliminarFavorito/', eliminarFavorito),
    path('buscarChatFavoritos/', buscarChatFavoritos),
    path('obtenerChatBloqueado/', obtenerChatBloqueado),
    path('buscarChatBloqueados/', buscarChatBloqueados),
    path('desbloquearChat/', desbloquearChat),
    path('actualizarPerfilUsuario/', actualizarPerfilUsuario),
    path('logout/', logout),

    path('enviarMensaje/', enviarMensaje),
    path('eliminarMensajes/', eliminarMensajes),  
    path('reenviarMensaje/', reenviarMensaje),
    path('obtenerMensajes/', obtenerMensajes)

]










#-------------------Ejemplos de URL post
    # path('ModificarJuegos/<int:id>/', actualizar_juego),
    # path('GeneroJuegos/<str:genero>/', GeneroJuegos)