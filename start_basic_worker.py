
from workers.basic_worker import BasicUserParseWorker


if __name__ == "__main__":
    worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")
    worker.run()
