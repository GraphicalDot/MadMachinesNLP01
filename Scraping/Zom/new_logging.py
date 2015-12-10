#!/usr/bin/env python
import logging

if __name__ == '__main__':
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(ip)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug('No one expects the spammish repetition', extra={"ip": "182.65.78.89"})
