import json
import aiohttp
from django.shortcuts import redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from asgiref.sync import async_to_sync, sync_to_async

from calender_api.constants.constants import *
from .utils import *


class GoogleCalendarInitView(APIView):
    """
    This view creates oauth url and redirects user to same
    """
    def get(self, request):
        # Construct the Google OAuth2 authorization URL
        authorization_url = f'{GOOGLE_AUTHORIZATION_ENDPOINT}?' \
                            f'scope=https://www.googleapis.com/auth/calendar%20https://www.googleapis.com/auth/userinfo.email&' \
                            f'access_type=offline&' \
                            f'response_type=code&' \
                            f'client_id={CLIENT_ID}&' \
                            f'redirect_uri={REDIRECT_URI}'

        # Redirect the user to the Google OAuth2 authorization page
        return redirect(authorization_url)

init_view = GoogleCalendarInitView.as_view()


@method_decorator(csrf_exempt, name='dispatch')
class GoogleCalendarRedirectView(APIView):
    """
    This view gets the calendar events and also generates refresh token if required
    """
    @async_to_sync
    async def get(self, request):
        
        # check if cookie is stored in users browser for access token        
        access_token = request.COOKIES.get('access_token', None)

        flag = True

        # if it is stored
        if access_token is not None:
            # get refresh all the token data from database
            user = asyncio.ensure_future(get_refresh_token_async(access_token))
            user_details = await asyncio.gather(user)

            if user_details is not None:
                
                flag = False

                # extract refresh token from GoogleTokens model
                refresh_token = user_details[0].refresh_token

                # if we get a valid token then make a http request for refreshing the access token
                if refresh_token:
                    async with aiohttp.ClientSession() as session:
                        # get request for refreshing the access token
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

                            # if we didn't got token means we need to sign in again
                            if access_token is None:
                                response = Response('Cookie unset')
                                response.delete_cookie('access_token')
                                return redirect(reverse('events:init'))

                            # else if we got the correct token then get calendar events
                            async with session.get(GOOGLE_CALENDAR_ENDPOINT, headers={
                                    'Authorization': f'Bearer {access_token}'
                                }) as calendar_response:
                                    calendar_data = await calendar_response.json()
                                    response = Response(calendar_data)
                                    t = asyncio.ensure_future(save_tokens_async(access_token, refresh_token,\
                                        user_details[0].email, user_details[0].email))
                                    await asyncio.gather(t)
                                    response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True)
                                    # Return the calendar events as a JSON response
                                    return response
                # user cookies is invalid
                else:
                    return Response({'message': 'Invalid user'})
        # if token is not set in cookies
        elif flag:
            # Get the authorization code from the query parameters
            authorization_code = request.GET.get('code')

            # if authorization_code in invalid promopt user
            if not authorization_code:
                return Response({'message':'No authorization code provided'})
            
            async with aiohttp.ClientSession() as session:
                # Exchange the authorization code for an access token and refresh token
                async with session.post(GOOGLE_TOKEN_ENDPOINT, data={
                    'code': authorization_code,
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'grant_type': 'authorization_code'
                }) as response:

                    response_data = await response.json()

                    if 'error' in response_data:
                        # return redirect(reverse('events:init'))
                        return Response(response_data)

                    access_token = response_data.get('access_token', 'None') 
                    refresh_token = response_data.get('refresh_token', 'None')

                    async with session.get(GOOGLE_USERINFO_ENDPOINT, headers={
                        'Authorization': f'Bearer {access_token}'
                    }) as userinfo_response:
                        userinfo_data = await userinfo_response.json()
                        email = userinfo_data.get('email','None')
                        ip = get_client_ip(request)
                        t = asyncio.ensure_future(save_tokens_async(access_token, refresh_token, email, ip))
                        await asyncio.gather(t)
                        # Use the access token to retrieve the user's calendar events
                        async with session.get(GOOGLE_CALENDAR_ENDPOINT, headers={
                            'Authorization': f'Bearer {access_token}'
                        }) as calendar_response:
                            calendar_data = await calendar_response.json()
                            response = Response(calendar_data)
                            response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True)
                            # Return the calendar events as a JSON response
                            return response

redirect_view = GoogleCalendarRedirectView.as_view()
