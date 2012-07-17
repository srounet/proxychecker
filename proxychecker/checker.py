#!/usr/bin/env python

import json
import gevent
from gevent import monkey; monkey.patch_all()
import gevent.pool
import gevent.queue
import httplib
import socket
import urllib2

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s'
)


jsonip = 'http://www.jsonip.com'
LOCAL_SERVER = None
privacy_headers = [
    'VIA',
    'X-FORWARDED-FOR',
    'X-FORWARDED',
    'FORWARDED-FOR',
    'FORWARDED-FOR-IP',
    'FORWARDED',
    'CLIENT-IP',
    'PROXY-CONNECTION',
]
socket.setdefaulttimeout(60)
queue = gevent.queue.Queue()
verbose = False


def whats_my_ip():
    if verbose:
        logging.debug('Retrieving your ip address')
    try:
        response = urllib2.urlopen(jsonip)
    except (urllib2.URLError, httplib.BadStatusLine) as e:
        return whats_my_ip()
    content = response.read()
    json_content = json.loads(content)
    my_ip = json_content[u'ip']
    if verbose:
        logging.debug('Your ip without proxy is: {}'.format(my_ip))
    return my_ip


def test_single_proxy(my_ip, ip, port, retry_count=0):
    if retry_count == 3:
        logging.debug('Could not connect to: {}:{}'.format(ip, port))
        return
    retry_count += 1
    proxy_handler = urllib2.ProxyHandler({'http': '{}:{}'.format(ip, port)})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
    try:
        response = urllib2.urlopen(LOCAL_SERVER)
    except (urllib2.URLError, httplib.BadStatusLine) as e:
        message = e.message or 'something wrong happened, retring...'
        logging.debug('Error ({}), with proxy: {}:{}'.format(message, ip, port))
        return test_single_proxy(my_ip, ip, port, retry_count)
    except socket.timeout as e:
        message = e.message or 'something wrong happened, retring...'
        logging.debug('Error ({}), with proxy: {}:{}'.format(message, ip, port))
        return False
    response_info = response.info()
    leaking_headers = []
    for header_key in privacy_headers:
        info = response_info
        header_value = info.get(header_key, info.get(header_key.lower()))
        if not header_value:
            continue
        if my_ip in header_value:
            leaking_headers.append(header_key)
    if leaking_headers:
        if verbose:
            headers = ', '.join(leaking_headers)
            logging.debug('Proxy leaking header {}: {}'.format(headers, ip))
        return False
    if verbose:
        logging.debug('Proxy safe: {}:{}'.format(ip, port))
    queue.put('{}:{}'.format(ip, port))


def test_proxy_list(http_proxies, pool_size, server_port):
    pool = gevent.pool.Pool(pool_size)
    my_ip = whats_my_ip()
    globals()['LOCAL_SERVER'] = 'http://{}:{}/'.format(my_ip, server_port)
    for proxy in http_proxies:
        ip, port = proxy.rsplit(':')
        pool.spawn(test_single_proxy, my_ip, ip, port)
    pool.join()
    queue.put(StopIteration)


def stop_server(ip, port):
    conn = httplib.HTTPConnection("{}:{}".format(ip, port))
    conn.request("QUIT", "/")
    conn.getresponse()
