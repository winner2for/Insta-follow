from flask import Flask, render_template, request, jsonify, session
import requests, re, json, time, os, sys
from requests.exceptions import SSLError, RequestException

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

SUKSES, GAGAL, FOLLOWERS, STATUS, BAD, CHECKPOINT, FAILED, TRY = [], [], { "COUNT": 0 }, [], [], [], [], []

class KIRIMKAN:
    def PENGIKUT(self, session, username, password, host, your_username):
        global SUKSES, GAGAL, STATUS, FAILED, BAD, CHECKPOINT
        session.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Sec-Fetch-Mode': 'navigate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Host': '{}'.format(host),
            'Sec-Fetch-Dest': 'document',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Connection': 'keep-alive'
        })
        response = session.get('https://{}/login'.format(host))
        self.ANTI_FORGERY_TOKEN = re.search(r'"&antiForgeryToken=(.*?)";', str(response.text))
        if self.ANTI_FORGERY_TOKEN != None:
            self.TOKEN = self.ANTI_FORGERY_TOKEN.group(1)
            session.headers.update({
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Sec-Fetch-Site': 'same-origin',
                'Referer': 'https://{}/login'.format(host),
                'Sec-Fetch-Mode': 'cors',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Sec-Fetch-Dest': 'empty',
                'Cookie': '; '.join([str(key) + '=' + str(value) for key, value in session.cookies.get_dict().items()]),
                'Origin': 'https://{}'.format(host)
            })
            data = {
                'username': f'{username}',
                'antiForgeryToken': f'{self.TOKEN}',
                'userid': '',
                'password': f'{password}'
            }
            response2 = session.post('https://{}/login?'.format(host), data = data)
            self.JSON_RESPONSE = json.loads(response2.text)
            if '\'status\': \'success\'' in str(self.JSON_RESPONSE):
                session.headers.update({
                    'Referer': 'https://{}/tools/send-follower'.format(host),
                    'Cookie': '; '.join([str(key) + '=' + str(value) for key, value in session.cookies.get_dict().items()])
                })
                data = {
                    'username': f'{your_username}',
                }
                response3 = session.post('https://{}/tools/send-follower?formType=findUserID'.format(host), data = data)
                if 'name="userID"' in str(response3.text):
                    self.USER_ID = re.search(r'name="userID" value="(\d+)">', str(response3.text)).group(1)
                    session.headers.update({
                        'Cookie': '; '.join([str(key) + '=' + str(value) for key, value in session.cookies.get_dict().items()])
                    })
                    data = {
                        'userName': f'{your_username}',
                        'adet': '500',
                        'userID': f'{self.USER_ID}',
                    }
                    response4 = session.post('https://{}/tools/send-follower/{}?formType=send'.format(host, self.USER_ID), data = data)
                    self.JSON_RESPONSE4 = json.loads(response4.text)
                    if '\'status\': \'success\'' in str(self.JSON_RESPONSE4):
                        SUKSES.append(f'{self.JSON_RESPONSE4}')
                        STATUS.append(f'{self.JSON_RESPONSE4}')
                        return {'status': 'success', 'message': 'Followers sent successfully!'}
                    elif '\'code\': \'nocreditleft\'' in str(self.JSON_RESPONSE4):
                        return {'status': 'error', 'message': 'Your credits have ran out!'}
                    elif '\'code\': \'nouserleft\'' in str(self.JSON_RESPONSE4):
                        return {'status': 'error', 'message': 'No users found!'}
                    elif 'istek engellendi.' in str(self.JSON_RESPONSE4):
                        TRY.append(f'{self.JSON_RESPONSE4}')
                        if len(TRY) >= 3:
                            TRY.clear()
                            return {'status': 'error', 'message': 'Request to send followers blocked!'}
                        else:
                            return self.PENGIKUT(session, username, password, host, your_username)
                    else:
                        GAGAL.append(f'{self.JSON_RESPONSE4}')
                        return {'status': 'error', 'message': 'Error while sending followers!'}
                else:
                    return {'status': 'error', 'message': 'Target username not found!'}
            elif 'Güvenliksiz giriş tespit edildi.' in str(self.JSON_RESPONSE):
                CHECKPOINT.append(f'{self.JSON_RESPONSE}')
                return {'status': 'error', 'message': 'Your account is checkpoint!'}
            elif 'Üzgünüz, şifren yanlıştı.' in str(self.JSON_RESPONSE):
                BAD.append(f'{self.JSON_RESPONSE}')
                return {'status': 'error', 'message': 'Your password is wrong!'}
            else:
                FAILED.append(f'{self.JSON_RESPONSE}')
                return {'status': 'error', 'message': 'Login error!'}
        else:
            return {'status': 'error', 'message': 'Forgery token not found!'}

class INFORMASI:
    def PENGIKUT(self, your_username, updated):
        global FOLLOWERS
        with requests.Session() as session:
            session.headers.update({
                'User-Agent': 'Instagram 317.0.0.0.3 Android (27/8.1.0; 360dpi; 720x1280; LAVA; Z60s; Z60s; mt6739; en_IN; 559698990)',
                'Host': 'i.instagram.com',
                'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            })
            response = session.get('https://i.instagram.com/api/v1/users/web_profile_info/?username={}'.format(your_username))
            if '"status":"ok"' in str(response.text):
                self.EDGE_FOLLOWED_BY = json.loads(response.text)['data']['user']['edge_followed_by']['count']
                if bool(updated) == True:
                    FOLLOWERS.update({
                        "COUNT": int(self.EDGE_FOLLOWED_BY)
                    })
                    return {'status': 'success', 'count': int(self.EDGE_FOLLOWED_BY)}
                else:
                    self.JUMLAH_MASUK = (int(self.EDGE_FOLLOWED_BY) - int(FOLLOWERS['COUNT']))
                    return {'status': 'success', 'count': int(self.EDGE_FOLLOWED_BY), 'increase': self.JUMLAH_MASUK}
            else:
                if bool(updated) == True:
                    FOLLOWERS.update({
                        "COUNT": 0
                    })
                    return {'status': 'error', 'message': 'Failed to get follower count'}
                else:
                    return {'status': 'error', 'message': 'Failed to get updated follower count'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-followers', methods=['POST'])
def send_followers():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    target_username = data.get('target_username')
    
    if not username or not password or not target_username:
        return jsonify({'status': 'error', 'message': 'All fields are required!'})
    
    # Get initial follower count
    info = INFORMASI()
    initial_count = info.PENGIKUT(target_username, True)
    
    # Send followers from all services
    results = []
    hosts = ['instamoda.org', 'takipcitime.com', 'takipcikrali.com', 'bigtakip.net', 'takipcimx.net']
    
    for host in hosts:
        try:
            with requests.Session() as session:
                kirim = KIRIMKAN()
                result = kirim.PENGIKUT(session, username, password, host, target_username)
                results.append({
                    'service': host,
                    'result': result
                })
        except Exception as e:
            results.append({
                'service': host,
                'result': {'status': 'error', 'message': f'Connection error: {str(e)}'}
            })
    
    # Get updated follower count
    updated_count = info.PENGIKUT(target_username, False)
    
    return jsonify({
        'initial_count': initial_count,
        'results': results,
        'updated_count': updated_count
    })

@app.route('/get-follower-count', methods=['POST'])
def get_follower_count():
    data = request.json
    target_username = data.get('target_username')
    
    if not target_username:
        return jsonify({'status': 'error', 'message': 'Username is required!'})
    
    info = INFORMASI()
    result = info.PENGIKUT(target_username, False)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)