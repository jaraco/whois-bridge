from fabric.api import sudo, run, task, env
from fabric.contrib import files
from fabric.context_managers import shell_env
from jaraco.text import (
	local_format as lf,
	global_format as gf,
)

if not env.hosts:
	env.hosts = ['punisher']

install_root = '/opt/whois-bridge'
proc_name = 'whois-bridge'

@task
def bootstrap():
	install_env()
	update()

@task
def install_env():
	sudo('rm -Rf "{install_root}"'.format(**globals()))
	install_upstart_conf()

@task
def install_upstart_conf(install_root=install_root):
	sudo(lf('mkdir -p "{install_root}"'))
	conf = gf("ubuntu/{proc_name}.service")
	files.upload_template(conf, "/etc/systemd/system",
		use_sudo=True, context=vars())
	sudo(gf('systemctl enable {proc_name}'))

@task
def update(version=None):
	install_to(install_root, version, use_sudo=True)
	cmd = gf('systemctl restart {proc_name}')
	sudo(cmd)

def install_to(root, version=None, use_sudo=False):
	"""
	Install package to a PEP-370 environment at root. If version is
	not None, install that version specifically. Otherwise, use the latest.
	"""
	action = sudo if use_sudo else run
	pkg_spec = 'jaraco.net'
	if version:
		pkg_spec += '==' + version
	if True: #with apt.package_context('python-dev'):
		with shell_env(PYTHONUSERBASE=root):
			usp = run('python3 -c "import site; print(site.getusersitepackages())"')
			action('mkdir -p {usp}'.format(**locals()))
			# can't run with '-U' because that will cause lxml to upgrade/build
			cmd = [
				'python3',
				'-m', 'pip',
				'install',
				'--user',
				pkg_spec,
			]
			action(' '.join(cmd))

@task
def remove_all():
	sudo(gf('systemctl stop {proc_name} || echo -n'))
	sudo(gf('rm /etc/systemd/system/{proc_name}.service || echo -n'))
	sudo(gf('rm -Rf "{install_root}"'))
