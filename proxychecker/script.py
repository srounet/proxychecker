#!/usr/bin/env python

import argparse
import proxychecker.checker


def test_proxy():
    parser = argparse.ArgumentParser()
    parser.add_argument('proxies_filepath', help='filepath to the list of proxies')
    parser.add_argument('--verbose',
        action='store_true',
        help='display debug informations',
    )
    parser.add_argument('--save_filepath',
        help='save all valid proxies to specified filepath',
    )
    arguments = parser.parse_args()
    if arguments.verbose:
        proxychecker.checker.verbose = True

    with open(arguments.proxies_filepath, 'r') as fd:
        content = fd.read()

    proxies = content.split('\n')
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]

    if arguments.save_filepath:
        valid_proxies_filepath = arguments.save_filepath
        if arguments.verbose:
            proxychecker.checker.logging.debug(
                'Saving valid proxies to: {}'.format(valid_proxies_filepath)
            )
        save_file = open(arguments.save_filepath, 'w+')

    for proxy, is_anonymous in proxychecker.checker.test_proxy_list(proxies):
        if arguments.save_filepath and is_anonymous:
            save_file.write('{}\n'.format(proxy))
