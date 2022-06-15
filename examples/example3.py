from mppbar import MPpbar
import time, names, random, logging
from multiprocessing import Queue
from queue import Empty
logger = logging.getLogger(__name__)

def do_work(total):
    logger.debug(f'processor is {names.get_last_name()}')
    logger.debug(f'processing total of {total}')
    for index in range(total):
        time.sleep(random.choice([.001, .003, .005]))
        logger.debug(f'processed item {index}')
    return total

def prepare_queue():
    queue = Queue()
    for _ in range(100):
        queue.put({'total': random.randint(40, 99)})
    return queue

def run_q(data, *args):
    queue = data['queue']
    result = 0
    while True:
        try:
            total = queue.get(timeout=1)['total']
            result += do_work(total)
            logger.debug('reset-mppbar')
        except Empty:
            logger.debug('reset-mppbar-complete')
            break
    return result

def main():
    queue = prepare_queue()
    process_data = [{'queue': queue} for item in range(3)]
    regex = {
        'total': r'^processing total of (?P<value>\d+)$',
        'count': r'^processed item \d+$',
        'alias': r'^processor is (?P<value>.*)$',
    }
    print('>> Processing items...')
    pbars =  MPpbar(function=run_q, process_data=process_data, regex=regex, timeout=1)
    results = pbars.execute()
    print(f">> {len(process_data)} workers processed a total of {sum(result for result in results)} items")

if __name__ == '__main__':
    main()
