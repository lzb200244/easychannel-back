import os

from channels.layers import get_channel_layer

from EasyChannel.settings.base import *

BASE_DIR = BASE_DIR.parent
# ##########################################channels配置
ASGI_APPLICATION = "EasyChannel.asgi.application"
# Channel内存管理
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer"
#     }
# }

#
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],  # 指定Redis服务器的地址和端口
        },
    },
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE'),
        'USER': os.getenv('MYSQL_ROOT_USER'),
        'PASSWORD': os.getenv('MYSQL_ROOT_PASSWORD'),
        'HOST': os.getenv('MYSQL_ROOT_HOST'),
        'PORT': os.getenv('MYSQL_ROOT_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AUTH_USER_MODEL = 'account.UserInfo'
# ########################################drf配置
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "extensions.auth.jwtauthentication.JWTAuthentication"],
    'EXCEPTION_HANDLER': 'extensions.exceptions.custom_exception_handler',
}
# #####################################################JWT配置
JWT_CONF = {
    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
}
# 跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ()
# 对应的发送的请求的跨域
# 允许携带身份验证信息（例如cookies）的请求

# 允许的请求方法
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
]

# 允许的请求头
CORS_ALLOW_HEADERS = [
    '*'
]

# ############################### Redis配置
CATCH_LIST = ['default', 'channel', 'account']


def redis_conf(index):
    return {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{index}",  # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1 << 32,
                "encoding": 'utf-8'
            },
            "PASSWORD": os.getenv('REDIS_PASSWORD')  # redis密码
        }
    }


CACHES = {
    item: redis_conf(index) for index, item in enumerate(CATCH_LIST)
}

# ###################################log 日志配置
LOG_ROOT = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_ROOT):
    os.mkdir(LOG_ROOT)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # 日志格式
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        "default": {
            "format": '%(asctime)s %(name)s  %(pathname)s:%(lineno)d %(module)s:%(funcName)s '
                      '%(levelname)s- %(message)s',
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # StreamHandler处理方式
            'formatter': 'default'
        },

        # 定义一个为account的处理器
        'account': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存日志自动切割
            'filename': os.path.join(BASE_DIR, 'logs/account.log'),
            'formatter': 'default',
            'backupCount': 4,  # 备份info.log.1 info.log.2 info.log.3 info.log.4
            'maxBytes': 1024 * 1024 * 50,  # 日志大小50m
            'encoding': 'utf-8'
        },
        "error": {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'formatter': 'default',
            'backupCount': 5,  # 备份info.log.1 info.log.2 info.log.3 info.log.4
            'maxBytes': 1024 * 1024 * 50,  # 日志大小50m
        },
        "waring": {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 按时间分类存储日志文件
            'filename': os.path.join(BASE_DIR, 'logs/waring.log'),
            'when': 'D',
            'backupCount': 4,
            'encoding': 'utf-8',
            'formatter': 'default'
        },
        "chat": {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'encoding': 'utf-8',
            'filename': os.path.join(BASE_DIR, 'logs/chat.log'),
            'formatter': 'default',
            'backupCount': 3,  # 备份info.log.1 info.log.2 info.log.3 info.log.4
            'maxBytes': 1024 * 1024 * 50,  # 日志大小50m
        },

    },
    # 日志实例对象
    # 所有的实例对象凡是有日志记录这里都会有一份
    'loggers': {
        # '': {
        #     'handlers': ['waring', 'console', 'error'],
        #     'level': 'DEBUG',
        #     'propagate': True  # 是否向上传递日志
        # },

        'chat': {
            'handlers': ['chat'],
            'level': 'INFO'
        },
        'account': {
            'handlers': ['account'],
            'level': 'INFO'
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },

    }

}
channel = get_channel_layer()


class MySingle:
    pass


Single = MySingle()
