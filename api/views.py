from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import gspread
from django.db import connection
from oauth2client.client import GoogleCredentials
import httplib2


cursor = connection.cursor()
auth_url = (settings.CFG['domain']+'/login/google-oauth2/').replace('//', '/')


def index(request):
    context = {
        'posts': [1,2,3]
        if request.user.is_authenticated else []
    }

    return render(request, 'index.html', context)


def gspread_client(email):
    row = cursor.execute("""SELECT extra_data
                            FROM social_auth_usersocialauth
                            where uid = '""" + email + "'")
    row = row.fetchone()
    if row:
        refresh_token = eval(row[0])['refresh_token']
        credentials = GoogleCredentials(None,
                                        settings.CFG['client_id'],
                                        settings.CFG['client_secret'],
                                        refresh_token,
                                        None,
                                        "https://accounts.google.com/o/oauth2/token",
                                        'sms-proxy')
        http = credentials.authorize(httplib2.Http())
        credentials.refresh(http)

        return gspread.authorize(credentials)
    else:
        return None


class Sheet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        gc = gspread_client(request.data['email'])

        if gc:
            try:
                existing_sheets = []
                for spreadsheet in gc.openall():
                    existing_sheets.append(spreadsheet.title)

                if request.data['sheet_title'] in existing_sheets:
                    content = {'message': 'A spreadsheet with given name already exists.'}
                    return Response(content, status=400)
                else:
                    sh = gc.create(request.data['sheet_title'])

                    content = {
                        'sheet_url': 'https://docs.google.com/spreadsheets/d/' + sh.id,
                    }
                    return Response(content)
            except gspread.exceptions.APIError as ex:
                content = {'message': eval(str(ex))['errors'][0]['message']}
                return Response(content, status=400)
        else:
            content = {
                'message': 'The user has not given permissions yet. Share authorization url with the user.',
                'authorization_url': auth_url
            }
            return Response(content, status=400)

    def put(self, request):
        gc = gspread_client(request.data['email'])

        if gc:
            try:
                worksheet = gc.open(request.data['sheet']).worksheet(request.data['tab'])
                worksheet.update(request.data['range'], request.data['data'])

                content = {'message': 'Sheet updated successfully.'}
                return Response(content)
            except gspread.exceptions.SpreadsheetNotFound:
                content = {'message': 'Spreadsheet with given name not found.'}
                return Response(content, status=400)
            except gspread.exceptions.WorksheetNotFound as ex:
                content = {'message': 'Tab named '+str(ex)+' not found.'}
                return Response(content, status=400)
        else:
            content = {
                'message': 'The user has not given permissions yet. Share authorization url with the user.',
                'authorization_url': auth_url
            }
            return Response(content, status=400)

    def delete(self, request):
        gc = gspread_client(request.data['email'])

        if gc:
            try:
                sh = gc.open(request.data['sheet_title'])
                try:
                    gc.del_spreadsheet(sh.id)
                    content = {'message': 'Sheet deleted successfully.'}
                    return Response(content)
                except gspread.exceptions.APIError as ex:
                    content = {'message': eval(str(ex))['errors'][0]['message']}
                    return Response(content, status=400)
            except gspread.exceptions.SpreadsheetNotFound:
                content = {'message': 'Spreadsheet with given name not found.'}
                return Response(content, status=400)
        else:
            content = {
                'message': 'The user has not given permissions yet. Share authorization url with the user.',
                'authorization_url': auth_url
            }
            return Response(content, status=400)
