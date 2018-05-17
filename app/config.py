#!/usr/bin/env python3
import html
import cgi
import os
import http.cookies
import funct
import sql
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates/'))
template = env.get_template('config.html')

print('Content-type: text/html\n')
funct.check_login()
funct.page_for_admin(level = 2)

form = cgi.FieldStorage()
serv = form.getvalue('serv')
config_read = ""
cfg = ""
stderr = ""
error = ""
aftersave = ""

try:
	cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
	user_id = cookie.get('uuid')
	user = sql.get_user_name_by_uuid(user_id.value)
	servers = sql.get_dick_permit()
except:
	pass

log_path = funct.get_config_var('main', 'log_path')
hap_configs_dir = funct.get_config_var('configs', 'haproxy_save_configs_dir')

if serv is not None:
	cfg = hap_configs_dir + serv + "-" + funct.get_data('config') + ".cfg"

if form.getvalue('serv') is not None and form.getvalue('open') is not None :
	
	try:
		funct.logging(serv, "config.py open config")
	except:
		pass
	
	error = funct.get_config(serv, cfg)
	
	try:
		conf = open(cfg, "r")
		config_read = conf.read()
		conf.close
	except IOError:
		error += '<br />Can\'t read import config file'

	os.system("/bin/mv %s %s.old" % (cfg, cfg))	

if form.getvalue('serv') is not None and form.getvalue('config') is not None:
	try:
		funct.logging(serv, "config.py edited config")
	except:
		pass
		
	config = form.getvalue('config')
	oldcfg = form.getvalue('oldconfig')
	save = form.getvalue('save')
	aftersave = 1
	try:
		with open(cfg, "a") as conf:
			conf.write(config)
	except IOError:
		error = "Can't read import config file"
	
	MASTERS = sql.is_master(serv)
	for master in MASTERS:
		if master[0] != None:
			funct.upload_and_restart(master[0], cfg, just_save=save)
		
	stderr = funct.upload_and_restart(serv, cfg, just_save=save)
		
	os.system("/bin/diff -ub %s %s >> %s/config_edit-%s.log" % (oldcfg, cfg, log_path, funct.get_data('logs')))
	os.system("/bin/rm -f " + hap_configs_dir + "*.old")

output_from_parsed_template = template.render(h2 = 1, title = "Edit Runnig HAProxy config",
													role = sql.get_user_role_by_uuid(user_id.value),
													action = "config.py",
													user = user,
													select_id = "serv",
													serv = serv,
													aftersave = aftersave,
													config = config_read,
													cfg = cfg,
													selects = servers,
													stderr = stderr,
													error = error,
													note = 1)
print(output_from_parsed_template)