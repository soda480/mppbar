from mppbar import MPpbar
import time, names, random, logging
logger = logging.getLogger(__name__)

def do_work(data, *args):
    logger.debug(f'processor is {names.get_last_name()}')
    total = data['total']
    logger.debug(f'processing total of {total}')
    for index in range(total):
        time.sleep(random.choice([.1, .2, .4]))
        logger.debug(f'processed item {index}')
    return total

def main():
    process_data = [{'total': random.randint(8, 16)} for item in range(6)]
    regex = {
        'total': r'^processing total of (?P<value>\d+)$',
        'count': r'^processed item \d+$',
        'alias': r'^processor is (?P<value>.*)$',
    }
    print('>> Processing items...')
    pbars =  MPpbar(function=do_work, process_data=process_data, regex=regex, timeout=1)
    results = pbars.execute()
    print(f">> {len(process_data)} workers processed a total of {sum(result for result in results)} items")

if __name__ == '__main__':
    main()
