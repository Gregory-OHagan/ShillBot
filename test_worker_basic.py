
import unittest
import codecs
import os
import socket
import threading


from workers.basic_worker import BasicUserParseWorker
from mothership.base import MothershipServer


class TestWorkerBasic(unittest.TestCase):

    def test_basic_worker_connection(self):
        """
        Purpose: Test regular running of worker
        Expectation: startup system, hit the reddit user and parse the data, fail to send to mothership (exception)

        :precondition: Mothership server not running
        :return:
        """
        worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")

        # Can't connect to mother, so should raise ConnectionRefusedError, but should run everything else
        self.assertRaises(socket.error, worker.run)

    def test_worker_parsing(self):
        """
        Purpose: Test regular parsing mechanisms of worker
        Expectation: Load html file, send it to worker to parse, should return list of results

        :return:
        """
        worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")
        file_path = '%s/%s' % (os.path.dirname(os.path.realpath(__file__)), 'test_resources/sample_GET_response.html')

        with codecs.open(file_path, encoding='utf-8') as f:
            text = f.read()
        results, next_page = worker.parse_text(text.encode("utf-8").strip().replace('\r\n', ''))

        self.assertGreater(len(results), 0)     # Check that results are returned
        self.assertEqual(len(results[0]), 3)    # Check that results are in triplets (check formatting)

    def test_worker_add_links_max_limit(self):
        """
        Purpose: Ensure that links are not added once cur_links >= max_links
        Expectation: add_links has no effect (link is not added)

        :return:
        """
        worker = None
        worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")

        worker.max_links = 0
        len_to_crawl_before = len(worker.to_crawl)
        worker.add_links("test.com")
        len_to_crawl_after = len(worker.to_crawl)

        self.assertEqual(len_to_crawl_after, len_to_crawl_before)

    def test_worker_add_links_in_crawled(self):
        """
        Purpose: Test that adding links won't add already crawled links
        Expectation: add_links has no effect (link is not added)

        :return:
        """
        worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")
        worker.crawled = ["https://www.reddit.com/user/Chrikelnel"]

        len_to_crawl_before = len(worker.to_crawl)
        worker.add_links(["https://www.reddit.com/user/Chrikelnel"])
        len_to_crawl_after = len(worker.to_crawl)

        self.assertEqual(len_to_crawl_after, len_to_crawl_before)

    def test_connection_to_mothership(self):
        """
        Purpose: Test that the workers are connecting to the server
        Expectation: start mothership, then run worker. Worker should not raise socket exception

        :return:
        """
        mama = MothershipServer()
        threading.Thread(target=mama.run).start()
        worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")
        self.assertIsNone(worker.run())
        mama.close()
    
    def test_duplicate_links(self):
        """
        Purpose: Test that duplicate links aren't added
        Expectation: length should not increase when adding a duplicate link is attempted to
    
        :return:
        """
        worker = None
        worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")

        worker.max_links = 5
        worker.add_links("test1", "test2")
        len_to_crawl_before = len(worker.to_crawl)
        worker.add_links("test1")
        len_to_crawl_after = len(worker.to_crawl)
        self.assert(len_to_crawl_after == len_to_crawl_before)
        

    def test_curr_links(self):
        """
        Purpose: Test that curr_links is updating when links are added
        Expectation: curr_links should increase as links are added, but only up to max_links

        :return:
        """
        worker = BasicUserParseWorker("link1")
        self.assertEqual(worker.cur_links, 1)
        worker.max_links = 5
        worker.add_links(["link1", "link2", "link3"])
        self.assertEqual(worker.cur_links, 3)
        worker.add_links(["link4", "link5", "link6"])
        self.assertEqual(worker.cur_links, 5)
