import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from .serializers import RegisterSerializer


def read_json(request):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            return None
        return data
    except (ValueError, UnicodeDecodeError):
        return None


@csrf_protect
@require_POST
def register_view(request):
    data = read_json(request)

    if data is None:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)

    serializer = RegisterSerializer(data=data)

    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)

    user = serializer.save()

    return JsonResponse({
        "id": user.id, 
        "username": user.username, 
        "message": "Регистрация успешна"
        }, status=201)

@csrf_protect
@require_POST
def login_view(request):
    data = read_json(request)

    if data is None:
        return JsonResponse(
            {"error": "Некорректный JSON"},
            status=400
        )

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse(
            {"error": "Укажите логин и пароль"},
            status=400
        )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return JsonResponse(
            {"error": "Неверный логин или пароль"},
            status=400
        )

    login(request, user)

    return JsonResponse({
        "message": "Вход выполнен",
        "username": user.username
    })


@csrf_protect
@require_POST
def logout_view(request):
    logout(request)

    return JsonResponse({
        "message": "Выход выполнен"
    })


@require_GET
def me_view(request):
    get_token(request)

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Пользователь не авторизован"},
            status=401
        )

    user = request.user

    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    })
        
