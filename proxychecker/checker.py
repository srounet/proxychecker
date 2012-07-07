#!/usr/bin/env python

import json
import httplib
import urllib2

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s'
)


jsonip = 'http://www.jsonip.com'
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
verbose = False


def whats_my_ip():
    response = urllib2.urlopen(jsonip)
    content = response.read()
    json_content = json.loads(content)
    my_ip = json_content[u'ip']
    if verbose:
        logging.debug('Your ip without proxy is: {}'.format(my_ip))
    return my_ip


def test_single_proxy(my_ip, ip, port):
    proxy_handler = urllib2.ProxyHandler({'http': '{}:{}'.format(ip, port)})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
    try:
        response = urllib2.urlopen(jsonip)
    except (urllib2.URLError, httplib.BadStatusLine) as e:
        message = e.message or 'something wrong happened, could be a timeout'
        logging.debug('Error ({}), with proxy: {}'.format(message, ip))
        return False
    response_info = response.info()
    leaking_headers = []
    for header_key in privacy_headers:
        header_value = response_info.get(header_key)
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
        logging.debug('Proxy safe: {}'.format(ip))
    return True


def test_proxy_list(http_proxies):
    my_ip = whats_my_ip()
    for proxy in http_proxies:
        ip, port = proxy.rsplit(':')
        is_anonymous = test_single_proxy(my_ip, ip, port)
        yield proxy, is_anonymous
