# ================================================= 启动web服务
# daphne EasyChannel.asgi:application
# ================================================= 启动celery服务
# celery -A mytasks.main worker -l info -P eventlet
daphne EasyChannel.asgi:application && celery -A mytasks.main worker -l info -P gevent
