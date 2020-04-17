from fabric.api import *
from fabric.colors import *
from fabutils import *

#important
MODULE = 'bl'

BIN_PATH = '/home/linkcool/bin'
SVR_PATH = '/home/linkcool/pysvr/pipeflow'
BAK_PATH = '/home/linkcool/bak/pipeflow'
UPD_PATH = '/home/linkcool/upload/pysvr/pipeflow'
RSYNC_PATH = 'upload/pysvr/pipeflow'
TEST_SVR = '162.247.97.205'
CK_USER = USER

PIPEFLOW_DEPLOY_MAP = {
    'path': SVR_PATH,
    'bak_path': BAK_PATH,
    'upd_path': UPD_PATH,
    'rsync_path': RSYNC_PATH,
    'items': {
        'server': {
            'files': {
                '__init__.py' : 'f',
                'clients.py' : 'f',
                'endpoints': 'd',
                'error.py' : 'f',
                'example.py' : 'f',
                'log.py' : 'f',
                'server.py' : 'f',
                'tasks.py' : 'f',
            }
        }
    }
}

pipeflow_deploy = ServerDeploy(
    module = MODULE,
    client_items = [],
    server_items = ['server'],
    test_items = [],
    deploy_map = PIPEFLOW_DEPLOY_MAP,
    bin_path = BIN_PATH,
    ck_user = USER,
    ck_name = '',
    console_name = '')

@task
def clean_server(items, targets):
    pipeflow_deploy.server_operation('clean', items, targets)
@task
def deploy_server(items, targets):
    pipeflow_deploy.server_operation('deploy', items, targets)
@task
def update_server(items, targets):
    pipeflow_deploy.server_operation('update', items, targets)
@task
def restore_server(items, targets):
    pipeflow_deploy.server_operation('restore', items, targets)


@task
def help():
    print red('!!!MUST SET MODULE in the fabfile.py')
    print ''
    print '[items defination]'
    print '---client items:[client_config, client]'
    print '---server items:[server_config, server, ck, console, cmd]'
    print ''
    print '[==amz best_seller==]'
    print 'fab clean_server:items=[item1+item2+...|all],targets=[host1+host2+...|all]'
    print 'fab deploy_server:items=[item1+item2+...|all],targets=[host1+host2+...|all]'
    print 'fab update_server:items=[item1+item2+...|all],targets=[host1+host2+...|all]'
    print 'fab restore_server:items=[item1+item2+...|all],targets=[host1+host2+...|all]'
