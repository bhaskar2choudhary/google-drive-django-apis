# google-drive-django-apis
This repo contains Django APIs to handle google drive files on behalf of other users.
Before starting the server, enable google API access and update config.yml file by following steps -

1. Head to [Google Developers Console](https://console.developers.google.com/project) and create a new project.
2. In the box labeled “Search for APIs and Services”, search for “Google Drive API” and enable it.
3. In the box labeled “Search for APIs and Services”, search for “Google Sheets API” and enable it.
4. Go to “APIs & Services > OAuth Consent Screen.” Click the button for “Configure Consent Screen” and follow the directions to give your app a name; you don’t need to fill out anything else on that screen. Click Save.
5. Go to “APIs & Services > Credentials”
6. Click “+ Create credentials” at the top, then select “OAuth client ID”.
7. Select “Web application”, name the credentials and add following entries to "Authorized redirect URIs"
    ``http://127.0.0.1:8000/complete/google-oauth2/``
    ``https://<your_django_domain>/complete/google-oauth2/``
8. Click “Create”. Copy "Your Client ID
" and "Your Client Secret" from “OAuth client created” popup into file config.yml.
9. Run Django server.
10. Tests can be run using Postman samples shared in test folder. All samples have a bearer type token attached in headers to authenticate the APIs calls.