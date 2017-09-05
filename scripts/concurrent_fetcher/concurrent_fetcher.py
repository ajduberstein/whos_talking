from threading import Thread
import sys
from Queue import Queue
import itertools
import time
import math

import requests

"""
Largely taken from
https://stackoverflow.com/questions/23547604/python-counter-atomic-increment
https://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
"""


class ConcurrentFetcher(object):
    """Concurrently fetches multiple URLs"""

    def __init__(
            self,
            urls_list=None,
            sec_between_executions=1,
            max_simultaneous_executions=5,
            processing_callback=None
            ):
        self.queue_size = len(urls_list)
        self.urls_list = urls_list
        self.processing_callback = processing_callback
        self.thread_counter = itertools.count()
        self.sec_between_executions = sec_between_executions
        self.max_simultaneous_executions = max_simultaneous_executions

    def do_work(self):
        while True:
            # Sleepa check
            group_count = self.thread_counter.next()
            sleep_time = self.sec_between_executions *\
                math.floor(int(group_count) / self.max_simultaneous_executions)
            time.sleep(sleep_time)
            print 'slept for ' + str(sleep_time)
            # End
            url = self.q.get()
            print 'Processing ' + url + '\n'
            o = requests.get(url)
            if self.processing_callback:
                self.processing_callback(o, url)
            else:
                print o.status_code, url
                print '\n'
            self.q.task_done()

    def run(self):
        self.q = Queue(self.queue_size * 2)
        for i in range(self.queue_size):
            t = Thread(target=self.do_work)
            t.daemon = True
            t.start()
        try:
            for url in self.urls_list:
                self.q.put(url.strip())
            self.q.join()
        except KeyboardInterrupt:
            sys.exit(1)
        except Exception:
            sys.exit(2)


if __name__ == "__main__":
    # Run python -m SimpleHTTPServer 3000 in another file
    # Test concurrent calls
    URLS_LIST = [
            "http://localhost:3000/1",
            "http://localhost:3000/11",
            "http://localhost:3000/111",
            "http://localhost:3000/1111",
            "http://localhost:3000/11111",
            "http://localhost:3000/2",
            "http://localhost:3000/22",
            "http://localhost:3000/222",
            "http://localhost:3000/2222",
            "http://localhost:3000/22222",
            "http://localhost:3000/3",
            "http://localhost:3000/33",
            "http://localhost:3000/333",
            "http://localhost:3000/3333",
            "http://localhost:3000/33333",
            "http://localhost:3000/4",
            "http://localhost:3000/44",
            "http://localhost:3000/444",
            "http://localhost:3000/4444",
    ]
    cf = ConcurrentFetcher(urls_list=URLS_LIST)
    cf.run()
