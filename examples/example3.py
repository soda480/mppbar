import time, random, logging
from multiprocessing import Queue
from queue import Empty
import names
from mppbar import MPpbar
logger = logging.getLogger(__name__)

def do_work(total):
    # log our intentions - messages will be intercepted as designated by MPpbar regex
    logger.debug(f'processor is {names.get_last_name()}')
    logger.debug(f'processing total of {total}')
    for index in range(total):
        # simulae work by sleeping
        time.sleep(random.choice([.001, .003, .005]))
        logger.debug(f'processed item {index}')
    return total

def prepare_queue():
    # create queue to add all the work that needs to be done
    queue = Queue()
    for _ in range(100):
        queue.put({'total': random.randint(40, 99)})
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
    # supply regex to intercept and set values for total count and alias
    regex = {
        'total': r'^processing total of (?P<value>\d+)$',
        'count': r'^processed item \d+$',
        'alias': r'^processor is (?P<value>.*)$',
    }
    print('>> Processing items...')
    pbars =  MPpbar(function=run_q, process_data=process_data, regex=regex, timeout=1)
    results = pbars.execute()
    # add up totals from all processes
    print(f">> {len(process_data)} workers processed a total of {sum(result for result in results)} items")

if __name__ == '__main__':
    main()
