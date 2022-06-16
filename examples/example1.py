import time, random, logging
import names
from mppbar import MPpbar
logger = logging.getLogger(__name__)

def do_work(data, *args):
    # log our intentions - messages will be intercepted as designated by MPpbar regex
    logger.debug(f'processor is {names.get_last_name()}')
    total = data['total']
    logger.debug(f'processing total of {total}')
    for index in range(total):
        # simulae work by sleeping
        time.sleep(random.choice([.1, .2, .4]))
        logger.debug(f'processed item {index}')
    return total

def main():
    # designate 6 processes total - each getting a different total
    process_data = [{'total': random.randint(8, 16)} for item in range(6)]
    # supply regex to intercept and set values for total count and alias
    regex = {
        'total': r'^processing total of (?P<value>\d+)$',
        'count': r'^processed item \d+$',
        'alias': r'^processor is (?P<value>.*)$',
    }
    print('>> Processing items...')
    pbars =  MPpbar(function=do_work, process_data=process_data, regex=regex, timeout=1)
    results = pbars.execute()
    # add up totals from all processes
    print(f">> {len(process_data)} workers processed a total of {sum(result for result in results)} items")

if __name__ == '__main__':
    main()
