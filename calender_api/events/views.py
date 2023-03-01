import json
from django.shortcuts import redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from asgiref.sync import async_to_sync, sync_to_async


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

    async def get_user_info(self, access_token, request):
        async with aiohttp.ClientSession() as session:
            userinfo_response = await session.get(
                GOOGLE_USERINFO_ENDPOINT,
                headers={
                    'Authorization': f'Bearer {access_token}'
                }
            )
            userinfo_data = await userinfo_response.json()
            email = userinfo_data.get('email', 'None')
            ip = get_client_ip(request)
            return email, ip

    async def get_calendar_events(self, access_token, refresh_token, email, ip):
        async with aiohttp.ClientSession() as session:
            async with session.get(GOOGLE_CALENDAR_ENDPOINT, headers={
                    'Authorization': f'Bearer {access_token}'
                }) as calendar_response:
                calendar_data = await calendar_response.json()
                response = Response(calendar_data)
                t = asyncio.ensure_future(save_tokens_async(access_token, refresh_token, email, ip))
                await asyncio.gather(t)
                response.set_cookie(key='email', value=email, httponly=True, secure=True)
                # Return the calendar events as a JSON response
                return response

    @async_to_sync
    async def get(self, request):
        
        # check if cookie is stored in users browser for access token        
        email = request.COOKIES.get('email', None)

        # if it is stored
        if email is not None:
            # get refresh all the token data from database
            user = asyncio.ensure_future(get_refresh_token_async(email))
            user_details = await asyncio.gather(user)
            tokens = user_details[0][0]
            print("=====================================================================")
            print(tokens)
            print("=====================================================================")
            if tokens is not None:
                refresh_token = tokens.refresh_token
                if refresh_token:

                    access_token = await refresh_access_token(refresh_token)

                    # if we didn't got token means we need to sign in again
                    if access_token is None:
                        response = Response('Cookie unset')
                        response.delete_cookie('email')
                        return redirect(reverse('events:init'))
                        # access_token = tokens.access_token

                    response = await self.get_calendar_events(access_token, refresh_token, email, tokens.ip)
                    return response

                # user cookies is invalid
                else:
                    return Response({'message': 'Invalid user'})
            else:
                response = Response('Cookie unset')
                response.delete_cookie('email')
                return redirect(reverse('events:init'))

        # if email is not set in cookies
        else:
            # Get the authorization code from the query parameters
            authorization_code = request.GET.get('code')

            # if authorization_code in invalid promopt user
            if not authorization_code:
                return Response({'message':'No authorization code provided'})
            
            access_token, refresh_token = await get_tokens(authorization_code)

            email, ip = await self.get_user_info(access_token, request)
        
            response = await self.get_calendar_events(access_token, refresh_token, email, ip)
            
            return response

redirect_view = GoogleCalendarRedirectView.as_view()
