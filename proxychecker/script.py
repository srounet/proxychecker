#!/usr/bin/env python

import argparse
import multiprocessing
import time

import proxychecker.checker
import proxychecker.httpserver


def test_proxy():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help='the port you want to use for the local proxy server', type=int)
    parser.add_argument('proxies_filepath', help='filepath to the list of proxies')
    parser.add_argument('--pool', help='simultaneous requests count', type=int, default=1)
    parser.add_argument('--verbose',
        action='store_true',
        help='display debug informations',
    )
    parser.add_argument('--save_filepath',
        help='save all valid proxies to specified filepath',
    )
    args = parser.parse_args()
    if args.verbose:
        proxychecker.checker.verbose = True

    with open(args.proxies_filepath, 'r') as fd:
        content = fd.read()

    proxies = content.split('\n')
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]

    if args.save_filepath:
        valid_proxies_filepath = args.save_filepath
        if args.verbose:
            proxychecker.checker.logging.debug(
                'Saving valid proxies to: {}'.format(valid_proxies_filepath)
            )
        save_file = open(args.save_filepath, 'w+')

    process = multiprocessing.Process(
        target=proxychecker.httpserver.simple_http_server,
        args=('0.0.0.0', args.port)
    )
    process.start()

    try:
        proxychecker.checker.test_proxy_list(proxies, args.pool, args.port)
    except KeyboardInterrupt:
        proxychecker.checker.stop_server('127.0.0.1', args.port)
        process.join()
        return
    for proxy in proxychecker.checker.queue:
        if args.save_filepath:
            save_file.write('{}\n'.format(proxy))
    proxychecker.checker.logging.debug('Finished, exiting both server and checker')
    proxychecker.checker.stop_server('127.0.0.1', args.port)
    process.join()

