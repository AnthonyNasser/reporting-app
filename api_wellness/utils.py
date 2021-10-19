import hashlib
import json
from datetime import datetime

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_bytes
from django.utils.http import http_date, parse_etags, quote_etag
from rest_framework.throttling import AnonRateThrottle

from .constants import CACHE_KEY_ETAG_LATEST_EVENTS, CACHE_KEY_ETAG_RANKINGS


def generate_cache_key(key):
    return hashlib.md5(force_bytes(key)).hexdigest()

def set_cache_headers(response, etag, cache_timeout=86400):
    response['ETag'] = etag
    response['Last-Modified'] = http_date()
    response['Cache-Control'] = 'max-age=' + str(cache_timeout)
    return response

def confirm_etag(request, key):
    request_etag = parse_etag(request)
    if request_etag:
        etag = generate_etag(key)
        return request_etag == etag
    return False

def parse_etag(request):
    if_none_match = request.META.get('HTTP_IF_NONE_MATCH')
    if if_none_match:
        return parse_etags(if_none_match)[0]
    return None

def generate_etag(key, content=None):
    etag = None
    json_content = None
    cache_key = generate_cache_key(key)

    if not content: # A request for a cached ETag
        return cache.get(cache_key)
    elif isinstance(content, datetime):
        json_content = json.dumps(content, cls=DjangoJSONEncoder)
    else:
        json_content = json.dumps(content, sort_keys=True)
        
    if json_content:
        etag = quote_etag(hashlib.md5(json_content.encode()).hexdigest())
        # Cache generated ETag if needed
        if key == CACHE_KEY_ETAG_LATEST_EVENTS:
            cache.add(cache_key, etag, None)
        elif key == CACHE_KEY_ETAG_RANKINGS:
            cache.add(cache_key, etag, 60 * 60 * 24)

    return etag

class RegisterThrottle(AnonRateThrottle):
    rate = '5/hour'
