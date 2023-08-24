"""
    ws和http启动文件，包括后台启动任务
"""

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.ws.channelmid import MyMiddleware
from utils.mq.gpt.consumer import ConsumerGpt
from utils.mq.tasks.base import RegisterTask
from . import routings

application = ProtocolTypeRouter({
    'websocket': MyMiddleware(URLRouter(routings.websocket_urlpatterns)),
    'http': get_asgi_application()

})

# ============================================================================ 启动后台线程进行处理消费任务
# t=threading.Thread(target=RegisterTask().run,daemon=True)
# t.start()

# t = threading.Thread(
#     target=ConsumerGpt().start(), daemon=True
# )
r = RegisterTask()
r.register(ConsumerGpt())
r.run()
