import base64, hashlib, json, os, socket, struct, sys, urllib.parse, urllib.request
from pathlib import Path
class Client:
 def __init__(self,url):
  p=urllib.parse.urlsplit(url)
  assert p.hostname=='127.0.0.1' or p.hostname=='localhost', 'loopback only'
  self.s=socket.create_connection((p.hostname,p.port),timeout=5);self.s.settimeout(15);self.buf=b'';self.ident=0
  key=base64.b64encode(os.urandom(16)).decode()
  self.s.sendall((f'GET {p.path} HTTP/1.1\r\nHost: {p.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
  while b'\r\n\r\n' not in self.buf:self.buf+=self.s.recv(65536)
  headers,self.buf=self.buf.split(b'\r\n\r\n',1)
  assert b'101' in headers.splitlines()[0],headers
 def read(self,n):
  while len(self.buf)<n:
   chunk=self.s.recv(max(65536,n-len(self.buf)))
   if not chunk:raise EOFError()
   self.buf+=chunk
  data,self.buf=self.buf[:n],self.buf[n:];return data
 def request(self,method,params=None):
  self.ident+=1; data=json.dumps({'id':self.ident,'method':method,'params':params or {}}).encode(); mask=os.urandom(4)
  prefix=bytes([0x81,0x80|len(data)]) if len(data)<126 else bytes([0x81,0x80|126])+struct.pack('!H',len(data)) if len(data)<65536 else bytes([0x81,0x80|127])+struct.pack('!Q',len(data))
  self.s.sendall(prefix+mask+bytes(b^mask[i%4] for i,b in enumerate(data)))
  parts=b''
  while True:
   a,b=self.read(2);length=b&127
   if length==126:length=struct.unpack('!H',self.read(2))[0]
   if length==127:length=struct.unpack('!Q',self.read(8))[0]
   key=self.read(4) if b&128 else None
   payload=self.read(length)
   if key:payload=bytes(x^key[i%4] for i,x in enumerate(payload))
   if a&15==8:raise EOFError('WebSocket closed')
   if a&15 not in [0,1]:continue
   parts+=payload
   if not a&128:continue
   reply=json.loads(parts);parts=b''
   if reply.get('id')==self.ident:return reply
 def close(self):self.s.close()
if __name__=='__main__':
 run=Path(sys.argv[1]);command=json.loads(Path(sys.argv[2]).read_text());port=json.loads((run/'cursor-launch.json').read_text())['port']
 with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list',timeout=5) as f:targets=json.load(f)
 (run/'cdp-targets.json').write_text(json.dumps(targets,indent=2)+'\n')
 pages=[t for t in targets if t.get('type')=='page'];assert pages,targets
 c=Client(pages[0]['webSocketDebuggerUrl']);r=c.request(command['method'],command.get('params'));c.close()
 out=run/(command.get('output','cdp-result.json'))
 if command['method']=='Page.captureScreenshot' and 'data' in r.get('result',{}):
  (run/'cursor-window.png').write_bytes(base64.b64decode(r['result']['data']));r['result']={'saved_image':str(run/'cursor-window.png')}
 out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
