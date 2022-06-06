import asyncio
import threading

from django.http import FileResponse, HttpResponse, AsyncStreamingHttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


def hello(request):
    name = request.GET.get("name") or "World"
    return HttpResponse("Hello %s!" % name)


def hello_meta(request):
    return HttpResponse(
        "From %s" % request.META.get("HTTP_REFERER") or "",
        content_type=request.META.get("CONTENT_TYPE"),
    )


def sync_waiter(request):
    with sync_waiter.lock:
        sync_waiter.active_threads.add(threading.current_thread())
    sync_waiter.barrier.wait(timeout=0.5)
    return hello(request)


@csrf_exempt
def post_echo(request):
    return HttpResponse(request.body)


def async_stream(request):
    async def stream():
        for word in (b"I", b"am", b"a", b"stream"):
            await asyncio.sleep(0.0)
            yield word

    return AsyncStreamingHttpResponse(stream())


sync_waiter.active_threads = set()
sync_waiter.lock = threading.Lock()
sync_waiter.barrier = threading.Barrier(2)


test_filename = __file__


urlpatterns = [
    path("", hello),
    path("file/", lambda x: FileResponse(open(test_filename, "rb"))),
    path("meta/", hello_meta),
    path("post/", post_echo),
    path("wait/", sync_waiter),
    path("stream/", async_stream),
]
