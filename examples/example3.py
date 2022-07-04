import time, random, logging
from multiprocessing import Queue
from queue import Empty
import names
from mppbar import MPpbar
logger = logging.getLogger(__name__)

def do_work(total):
    # log our intentions - messages will be intercepted as designated by MPpbar regex
    logger.debug(f'worker is {names.get_last_name()}')
    logger.debug(f'processing total of {total} items')
    for index in range(total):
        # simulate work by sleeping
        time.sleep(random.choice([.001, .003, .005]))
        logger.debug(f'processed item {index}')
    return total

def prepare_queue():
    # create queue to add all the work that needs to be done
    queue = Queue()
    for _ in range(75):
        queue.put({'total': random.randint(100, 150)})
    return queue

def run_q(data, *args):
    queue = data['queue']
    result = 0
    while True:
        try:
            # get work from queue
            total = queue.get(timeout=1)['total']
            # process the work
            result += do_work(total)
            # this allows us to reset progress bar
            logger.debug('reset-mppbar')
        except Empty:
            logger.debug('reset-mppbar-complete')
            break
    return result

def main():
    queue = prepare_queue()
    # designate 3 processes total - each getting reference to the queue
    process_data = [{'queue': queue} for item in range(3)]
    print(f'>> Processing {queue.qsize()} totals using {len(process_data)} workers ...')
    pbars =  MPpbar(function=run_q, process_data=process_data, timeout=1, show_prefix=False, show_percentage=False)
    results = pbars.execute()
    # add up results from all workers
    print(f">> {len(process_data)} workers processed a total of {sum(result for result in results)} items")

if __name__ == '__main__':
    main()
