from fabric.api import run, cd, env

env.hosts = ['scenable']
env.use_ssh_config = True


def deploy(update_static=True):
    update_static = bool(update_static)
    print update_static
    webapp_source_root = 'webapps/scenable/betasite'
    with cd(webapp_source_root):
        run('git checkout master')
        run('git pull')
        if update_static:
            run('./manage.py collectstatic')
        run('../apache2/bin/restart')
