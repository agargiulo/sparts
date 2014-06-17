# Copyright (c) 2014, Facebook, Inc.  All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#
from functools import wraps
import time


class Memo(Exception):
    """Control exception to override memoization defaults"""

    # Sentinel 
    UNSET = object()

    def __init__(self, value, ttl=UNSET, nomemo=False, forever=False):
        Exception.__init__("Usage Error: Memo should not be thrown"
                           " from non-memoized functions")

        if forever:
            ttl = None
        elif nomemo:
            ttl = 0

        self.value = value
        self.ttl = ttl


def memoize_timed(ttl, jitter=0.0):
    default_ttl = ttl
    def do_wrap(function):
        memo_cache = {}
        function.sparts_memo_cache = memo_cache
        @wraps(function)
        def wrapped(*args, **kwargs):
            key = (args, tuple(kwargs.items()))
            if key in memo_cache:
                (exptime, result) = memo_cache[key]
            else:
                exptime = 0

            now = time.time()
            if exptime is not None and now > exptime:
                ttl = default_ttl
                try:
                    result = function(*args, **kwargs)
                except Memo as m:
                    result = m.value
                    if m.ttl is not Memo.UNSET:
                        ttl = m.ttl
                finally:
                    # Recalculate `now` in case functiontook a long time
                    # to execute.
                    now = time.time()

                if ttl is None:
                    exptime = None
                else:
                    exptime = now + ttl

                # Set the expiration time and return value 
                memo_cache[key] = (exptime, result)

            return result

        return wrapped
    return do_wrap


def memoize_forever(function):
    return memoize_timed(None)(function)
