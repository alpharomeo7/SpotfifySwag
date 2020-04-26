from flask import Flask, request,redirect
from flask import render_template
import requests
import json


app = Flask(__name__)

@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    pass




@app.route('/')
def index():
    client_id = 'Your client ID'
    redirect_uri = request.base_url + 'results/'
    scope = 'user-top-read'
    login_url = 'https://accounts.spotify.com/authorize?client_id=' + client_id + '&state=bravo_charlie&response_type=code&redirect_uri=' + redirect_uri + '&scope=' + scope
    return render_template('index.html',login_url=login_url)




@app.route('/results/')
def results():
    code = request.args['code']
    headers = get_headers(code)
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user = json.loads(response.text)
    user['images'] += [{'url': "../static/assets/img/Spotify_Icon_CMYK_Green.png"}]
    terms = ['long','medium','short']
    bravo_charlie = {}
    swag = {}

    for term in terms:
        base_url = 'https://api.spotify.com/v1/me/top/tracks?time_range={}_term&limit=50'.format(term)
        response = requests.get(base_url, headers=headers)
        tracks = json.loads(response.text)['items']
        swag[term], bravo_charlie[term] = get_bravo_charlie(tracks, headers)

    timeperiod = {'long': 'Full History','short':'~4 weeks', 'medium':'~ 6 months'}
    return render_template('results.html', user=user, swag=swag, bravo_charlie= bravo_charlie,terms=terms,timeperiod=timeperiod)

def get_headers(code):
    redirect_uri = request.base_url
    encoded_client_credentials = 'Your encoded creditians' #Insert base64 client_id:client_secret
    headers = {
        'Authorization': 'Basic ' + encoded_client_credentials,
    }

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    bearer_token = 'Bearer ' + json.loads(response.text)['access_token']

    headers = {
        'Authorization': bearer_token,
    }
    return headers

def get_bravo_charlie(tracks,headers):
    album_ids = []
    albums_image_urls = []
    white_url = 'https://dummyimage.com/300x300/ffffff/ffffff'
    for track in tracks:
        album = track['album']
        if album['id'] not in album_ids:
            album_ids.append(album['id'])
            albums_image_urls.append(album['images'][1]['url'])
        if len(album_ids) > 4:
            break

    if len(albums_image_urls) == 0:
        return("#","../static/assets/img/Blank Clinton.png")

    albums_image_urls = albums_image_urls + [white_url]*(4-len(albums_image_urls))
    bravo_charlie_url = 'https://www.billclintonswag.com/api/image?album_url={}&album_url={}&album_url={}&album_url={}'.format(*albums_image_urls)

    swag_url = requests.get(bravo_charlie_url, stream=True).url
    image_id = swag_url.rsplit('/', 1)[-1]
    swag_url = 'https://bill-clinton-swag-fgj90r9m3.now.sh/shop?swag={}'.format(image_id)
    image_url = 'https://s3.amazonaws.com/Clinton_Swag/{}/swag.png'.format(image_id)
    return(swag_url,image_url)


if __name__ == '__main__':
    app.run(port = 8081)
