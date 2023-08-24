# ws中间件
import logging

from channels.middleware import BaseMiddleware
from utils.auth import decode_jwt
from utils.parse.cookies import decode

logger = logging.getLogger('chat')


class MyMiddleware(BaseMiddleware):

    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        # 在请求到达消费者之前执行的操作
        headers = dict(scope['headers'])
        # print(headers)

        cookie: str = headers.get(b'cookie', b'').decode("utf8")
        # 存在cookies
        cookies_map: dict = decode(cookie)
        # 存在cookies,但是jwt是已经篡改过了...
        access_token = cookies_map.get("access_token")

        scope['user'] = None
        if access_token:
            try:
                user = await decode_jwt(access_token)
                scope['user'] = user
            except Exception as e:
                # TODO 记录日志
                # 认证失败，关闭连接
                logger.warning(access_token + f'msg：{ e}' )
                await send({
                    'type': 'websocket.close',
                })

        # 调用下一个中间件或消费者
        await super().__call__(scope, receive, send)
