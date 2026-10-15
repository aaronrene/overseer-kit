import io, json, urllib.request, urllib.response
from email.message import Message
from tools.hosted_dashboard.http_client import UpstreamClient
from tools.hosted_dashboard.hosts import url_host_allowed
calls=[]
class FixtureHandler(urllib.request.BaseHandler):
    handler_order=100
    def https_open(self, req):
        calls.append({'url':req.full_url,'authorization':req.get_header('Authorization'), 'host_allowed':url_host_allowed(req.full_url)})
        headers=Message()
        if req.full_url.startswith('https://api.github.com/'):
            headers['Location']='https://not-allowlisted.invalid/stolen'
            code=302
            body=b''
        else:
            code=200
            headers['Content-Type']='application/json'
            body=b'{"fake":true}'
        response=urllib.response.addinfourl(io.BytesIO(body),headers,req.full_url,code)
        response.msg='fixture'
        return response
    http_open=https_open
opener=urllib.request.build_opener(FixtureHandler())
previous=urllib.request._opener
urllib.request.install_opener(opener)
try:
    result=UpstreamClient(token='FAKE-REVIEW-TOKEN').get_json('https://api.github.com/repos/acme/demo')
finally:
    urllib.request._opener=previous
print(json.dumps({'result':result,'calls':calls,'network_used':False},indent=2))
assert len(calls)==2
assert calls[1]['host_allowed'] is False
assert calls[1]['authorization']=='Bearer FAKE-REVIEW-TOKEN'
