DEFAULT_CHANNEL_LAYER = 'default'

from .asgi import channel_layers  # NOQA isort:skip
from .channel import Channel, Group  # NOQA isort:skip
from .routing import route, include  # NOQA isort:skip
