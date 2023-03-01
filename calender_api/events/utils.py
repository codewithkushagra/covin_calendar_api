import asyncio
import aiohttp


from .models import GoogleTokens
from calender_api.constants.constants import *

# get the user IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# get refresh token from database
def get_refresh_token(email):
    google = GoogleTokens.objects.filter(email = email)
    if google:
        return google
    return None


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


async def get_tokens(authorization_code):
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                'code': authorization_code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )
        response_data = await response.json()
        if 'error' in response_data:
            raise ValueError('Unable to get tokens')
        access_token = response_data.get('access_token', 'None')
        refresh_token = response_data.get('refresh_token', 'None')
        return access_token, refresh_token


async def refresh_access_token(refresh_token):
    async with aiohttp.ClientSession() as session:
        # send a post request to refresh the access token
        async with session.post(GOOGLE_TOKEN_ENDPOINT, data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }) as response:
            # await for the response and convert the response into python dict
            response_data = await response.json()

            # extract the access token from response_data
            access_token = response_data.get('access_token', None)

            # if we got the correct token then return it
            return access_token