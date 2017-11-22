import json
from flask import *
import requests
import base64
import urllib
import json
import time
from tmm_functions import *
from flask_cors import CORS
# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response. 


app = Flask(__name__)
CORS(app)
global access_token
access_token = ''

with open("login.txt") as f: #Abrindo o login.txt que contem na 1a linha Client_user e na segunda a Client_secre
    data = f.readlines()


#  Client Keys
CLIENT_ID = data[0].strip()
CLIENT_SECRET = data[1].strip()

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "localhost"
PORT = 5000
REDIRECT_URI = "http://{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"
STATE = ""
SHOW_DIALOG_bool = False
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()



auth_query_parameters = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "show_dialog": SHOW_DIALOG_str,
}

@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }

    auth_str = "{0}:{1}".format(CLIENT_ID, CLIENT_SECRET)
    base64encoded = base64.urlsafe_b64encode(auth_str.encode()).decode()
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    print('RESPONSE',response_data)
    access_token = response_data["access_token"]
    tokenfile = open('./token.txt','w')
    tokenfile.write(access_token)
    tokenfile.close()
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "https://api.spotify.com/v1/me/playlists"
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)
    
    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return redirect('static/index.html')

@app.route("/token")
def getToken():
    file = open("./token.txt",'r')
    return file.readline()

@app.route("/playlist",methods=['GET'])
def getPlaylist():
    genero = request.args.get('genero')
    genero = genero.lower()
    moods = request.args.get('moods')
    moods = moods.lower()
    name = request.args.get('name')
    name = name.lower()
    print('OBTAINED PARAMETERS',genero,moods)
    token = getToken()

    # # try:
    client = User(data,token=token)
    client.sp.user_playlist_create(user=12144879613,name=name,public=True)
    ash=Trainer()

    classified_musics=ash.playlist_maker(genero,moods)
    oi=client.sp.user_playlist(user=12144879613, playlist_id=None, fields=None)

    authorization_header = {"Authorization":"Bearer {}".format(token)}
    playlist_api_endpoint = "https://api.spotify.com/v1/me/playlists"
    playlists_response = requests.get(url=playlist_api_endpoint,params=None,headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    print(playlist_data,type(playlist_data))
    for i in playlist_data['items']:
        if i['name']==name:
            id=i['id']
            uri=i['uri']
    musics_ids_list=classified_musics['id'].tolist()
    client.sp.user_playlist_add_tracks(user=12144879613, playlist_id=id, tracks=musics_ids_list, position=None)
    
    res = {}
    res['status'] = "SUCCESS"
    res['uri'] = uri

    return jsonify(res)



if __name__ == "__main__":
    app.run(debug=True,host="localhost",port=PORT,threaded=True)

