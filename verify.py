#coding:utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.process
import tornado.web
from captcha import Captcha 
from io import BytesIO
import torndb
import uuid
class verify_captcha(tornado.web.RequestHandler):
	def initialize(self, db, vc):
		self.db=db
		self.vc=vc
		#tornado.web.RequestHandler.__init__(self)

	def get(self, *args, **kwargs):
		code_img,captcha_code = self.vc.create();
		session = uuid.uuid1()
		self.db.execute('INSERT INTO captcha(session,code) VALUES(%s,%s)', session, captcha_code);
		msstream=BytesIO()
		code_img.save(msstream,"jpeg")
		code_img.close()
		self.set_header('Content-Type', 'image/jpg')
		self.set_secure_cookie("ivs",captcha_code)
		self.write(msstream.getvalue())

	def post(self, *args, **kwags):
		code=self.get_argument('code', '')
		session=self.get_secure_cookie("ivs");
		captcha_code = self.db.query('SELECT code FROM captcha WHERE session=%s', session)
		self.db.execute('DELETE FROM captcha WHERE session=%s', session)
		if code != captcha_code:
			self.write('verify captcha error !')
		else:
			self.write('verify captcha success !')
			#todo
			
class Config:
	CAPTCHA_DB_HOST='127.0.0.1:3306'
	CAPTCHA_DB_NAME='captcha'
	CAPTCHA_DB_USER='gsgame'
	CAPTCHA_DB_PASSWORD='gsgame'
	LISTEN_PORT=10600
config=Config()

def get_db(db=None):
	sdb=db
	if db is None:
		sdb = config.CAPTCHA_DB_NAME
	return torndb.Connection(config.CAPTCHA_DB_HOST, sdb , config.CAPTCHA_DB_USER, config.CAPTCHA_DB_PASSWORD)
	

def get_app(inst_id=0):
	db=get_db()
	vc=Captcha()
	return tornado.web.Application([(r'/', verify_captcha, dict(db=db, vc=vc))], cookie_secret="61oETzKXQ236GaYdk53n08&%$#GeJJug&QnrgdTP1o=Vo=")


def init_db():
	db = get_db('')# torndb.Connection(config.CAPTCHA_DB_HOST, '' , config.CAPTCHA_DB_USER, config.CAPTCHA_DB_PASSWORD)
	db.execute('CREATE DATABASE IF NOT EXISTS %s;' % config.CAPTCHA_DB_NAME)
	db.execute("""USE %s; CREATE TABLE IF NOT EXISTS %s (
			session VARCHAR(128),
			code VARCHAR(8)
		)ENGINE=InnoDB DEFAULT CHARSET=utf8;""" % (config.CAPTCHA_DB_NAME, 'captcha'))

def main(inst_id=0):
	app = get_app(inst_id)
	app.listen(config.LISTEN_PORT+inst_id)
	tornado.ioloop.IOLoop.current().start()

import sys
if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'dbinit':
		init_db()
	main()	





