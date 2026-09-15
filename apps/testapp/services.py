import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'


def get_google_access_token(code: str) -> str:
    payload = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
    }
    
    response = requests.post(GOOGLE_TOKEN_URL, data=payload)
    
    if not response.ok:
        raise AuthenticationFailed('Неудачная попытка обменять code на access_token Google.')
        
    data = response.json()
    access_token = data.get('access_token')
    
    if not access_token:
        raise AuthenticationFailed('Google не вернул access_token.')
        
    return access_token


def get_google_user_info(access_token: str) -> dict:
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(GOOGLE_USER_INFO_URL, headers=headers)
    
    if not response.ok:
        raise AuthenticationFailed('Не удалось получить данные профиля из Google.')
        
    user_data = response.json()
    
    if not user_data.get('email'):
        raise AuthenticationFailed('Google профиль не содержит email.')
        
    return {
        'email': user_data.get('email'),
        'name': user_data.get('name', ''),
    }