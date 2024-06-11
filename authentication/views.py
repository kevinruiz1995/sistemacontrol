import cv2
import dlib
import numpy as np
from django.contrib import messages
from django.core.files.base import ContentFile
import base64
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from authentication.forms import CustomUserCreationForm, CustomLoginForm
from authentication.models import CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate

def extraer_landmarks(imagen):
    # Inicializa el detector de rostros de dlib (HOG)
    detector_rostros = dlib.get_frontal_face_detector()
    # Inicializa el predictor de landmarks de dlib
    predictor_landmarks = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Ajusta la ruta al archivo de landmarks

    # Convierte la imagen a escala de grises
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Detecta rostros en la imagen
    rostros = detector_rostros(imagen_gris)

    # Si se detecta al menos un rostro
    if rostros:
        # Obtiene los landmarks del primer rostro detectado
        landmarks = predictor_landmarks(imagen_gris, rostros[0])
        landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])

        return landmarks

    return None

def comparar_rasgos(imagen1, imagen2):
    # Carga las imágenes usando OpenCV
    imagen1 = cv2.imdecode(np.fromstring(imagen1.read(), np.uint8), cv2.IMREAD_COLOR)
    imagen2 = cv2.imread(imagen2.path)

    # Extrae landmarks de ambas imágenes
    landmarks1 = extraer_landmarks(imagen1)
    landmarks2 = extraer_landmarks(imagen2)

    # Comprueba si se pudieron extraer landmarks de ambas imágenes
    if landmarks1 is not None and landmarks2 is not None:
        # Puedes realizar comparaciones entre los landmarks según tus necesidades
        # Por ejemplo, podrías calcular la distancia euclidiana entre los puntos

        # Calcula la distancia euclidiana entre los landmarks de ambas imágenes
        distancia = np.linalg.norm(landmarks1 - landmarks2)

        # Define un umbral (ajústalo según tus necesidades)
        umbral_distancia = 1000

        # Compara la distancia con el umbral
        if distancia < umbral_distancia:
            return True  # Rostros similares
        else:
            return False  # Rostros diferentes
    else:
        return False  # No se pudieron extraer landmarks de una o ambas imágenes

# Función para comparar imágenes
def comparar_imagenes(img1, img2):
    # Carga las imágenes usando OpenCV
    imagen1 = cv2.imdecode(np.frombuffer(img1.read(), np.uint8), cv2.IMREAD_COLOR)

    imagen2 = cv2.imread(img2.path)

    # Comprueba si las imágenes tienen el mismo tamaño
    if imagen1.shape == imagen2.shape:
        # Calcula la diferencia absoluta entre las imágenes
        diferencia = cv2.absdiff(imagen1, imagen2)

        # Convierte la imagen de diferencia a escala de grises
        diferencia_grises = cv2.cvtColor(diferencia, cv2.COLOR_BGR2GRAY)

        # Calcula la media de la diferencia
        media_diferencia = np.mean(diferencia_grises)

        # Define un umbral (puedes ajustar este valor según tus necesidades)
        umbral = 100

        # Compara la media de la diferencia con el umbral
        if media_diferencia < umbral:
            return True  # Imágenes similares
        else:
            return False  # Imágenes diferentes
    else:
        return False  # Imágenes de tamaños diferentes

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Cambia 'home' a la página de inicio de tu aplicación
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        if 'reconocimiento_facial' not in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            form = CustomLoginForm(request, data=request.POST)
            if form.is_valid():
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        next_url = request.GET.get('next', '')  # Obtener la URL de redirección desde el parámetro 'next'
                        if next_url:
                            return HttpResponseRedirect(next_url)  # Redirigir a la URL especificada
                        return redirect('home')  # Redirigir al usuario a la página de inicio después del inicio de sesión
                    else:
                        return JsonResponse({"success": False, "mensaje": 'Tu cuenta está desactivada. Por favor, contacta al administrador.'})
                else:
                    return JsonResponse({"success": False, "mensaje": 'Tu cuenta no se encuentra autenticada.'})
            else:
                return JsonResponse({"success": False, "mensaje": 'Nombre de usuario o contraseña incorrectos.'})
        else:
            username = request.POST['username']
            usuario_reconocimiento = CustomUser.objects.filter(username=username, is_active=True)
            if usuario_reconocimiento.exists():
                user = usuario_reconocimiento.first()
                if user.imagen:
                    imagen_base64 = request.POST.get('imagen', None)

                    # Decodifica la imagen desde base64
                    imagen_decodificada = base64.b64decode(imagen_base64.split(',')[1])

                    imagen = ContentFile(imagen_decodificada)
                    if comparar_rasgos(imagen, user.imagen):
                        login(request, user)
                        return JsonResponse({"success": True})
                    else:
                        return JsonResponse({"success": False, "mensaje": 'Reconocimiento facial fallido.'})
                else:
                    return JsonResponse({"success": False, "mensaje": 'El usuario no tiene una imagen registrada.'})
            else:
                return JsonResponse({"success": False, "mensaje": 'El usuario no existe'})
    else:
        form = CustomLoginForm(request)

    context = {
        'page_titulo': 'Inicio de sesión',
        'form': form,
    }
    return render(request, 'registration/login.html',context)


def custom_logout(request):
    logout(request)
    return redirect(reverse('accounts:login'))  # Cambia 'login' a la página de inicio de sesión de tu aplicación