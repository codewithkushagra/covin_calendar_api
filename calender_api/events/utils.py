import asyncio
from .models import GoogleTokens


# get the user IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# get refresh token from database
def get_refresh_token(access_token):
    google = GoogleTokens.objects.filter(access_token = access_token)
    return google[0]



# async warpper for get_refresh_token function
async def get_refresh_token_async(access_token):
    return await asyncio.to_thread(get_refresh_token, access_token)


# save and updates tokens
def save_tokens(access_token, refresh_token, email, ip):
    if GoogleTokens.objects.filter(email=email):
        if access_token != 'None':
            GoogleTokens.objects.filter(email=email).update(access_token=access_token)
        if refresh_token != 'None':
            GoogleTokens.objects.filter(email=email).update(refresh_token=refresh_token)
        return
    GoogleTokens.objects.create(access_token=access_token, refresh_token=refresh_token, email=email, ip=ip)
    return


# async warpper for save_tokens function
async def save_tokens_async(access_token, refresh_token, email, ip):
    await asyncio.to_thread(save_tokens, access_token, refresh_token, email, ip)

