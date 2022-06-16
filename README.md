# mppbar
[![build](https://github.com/soda480/mppbar/actions/workflows/main.yml/badge.svg)](https://github.com/soda480/mppbar/actions/workflows/main.yml)
[![Code Grade](https://api.codiga.io/project/33815/status/svg)](https://app.codiga.io/public/project/33815/mppbar/dashboard)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/mppbar.svg)](https://badge.fury.io/py/mppbar)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)

The mppbar module provides a convenient way to scale execution of a function across multiple input values by distributing the input across a number of background processes, it displays the execution status of each background process using a [progress bar](https://pypi.org/project/progress1bar/).

The MPpbar class is a subclass of [MPmq](https://pypi.org/project/mpmq/) and the primary benefit of using `mppbar` is that the function being scaled requires minimal modification (if at all) since the multiprocessing and progress bar are completely abstracted. The progress bar is initialized and updated through the interception and processing of the messages logged within the function. The log messages in the function must use f-string style formatting.

### Installation
```bash
pip install mppbar
```

### `MPpbar class`
```
MPpbar(function, process_data=None, shared_data=None, processes_to_start=None, regex=None, fill=None)
```

<details><summary>Documentation</summary>

> `function` - The function to execute. It should accept two positional arguments; the first argument is the dictionary containing the input data for the respective process see `process_data` below, the second argument is the shared dictionary sent to all proceses see `shared_data` below.

> `process_data` - A list of dictionaries where each dictionary describes the input data that will be sent to the respective process executing the function; the length of the list dictates the total number of processes that will be executed.

> `shared_data` - A dictionary containing arbitrary data that will be sent to all processes.

> `processes_to_start` - The number of processes to initially start; this represents the number of concurrent processes that will be running. If the total number of processes is greater than this number then the remaining processes will be queued and executed to ensure this concurrency is maintained. Defaults to the length of the `process_data` lsit.

> `regex` - A dictionary whose key values are regular expressions for `total`, `count` and `alias`. The regular expressions will be checked against the log messages intercepted from the executing function, if matched the value will be used to assign the attribute for the respective progress bar. The `total` and `count` key values are required, the `alias` key value is optional.

> `fill` - A dictionary whose key values are integers that dictate the number of leading zeros the progress bar should add to the `total`, `index` and `completed` values; this is optional and should be used to format the progress bar appearance. The supported key values are `max_total`, `max_index` and `max_completed`.

> **execute(raise_if_error=False)**
>> Start execution the process’s activity. If `raise_if_error` is set to True, an exception will be raised if the function encounters an error during execution.

</details>

### Examples

#### [example1](https://github.com/soda480/mppbar/blob/main/examples/example1.py)

Distribute work across multiple processes with all executing concurrently, each displays a progress bar showing its execution status.

<details><summary>Code</summary>

```Python
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
```

</details>

![example1](https://raw.githubusercontent.com/soda480/mppbar/main/docs/images/example1.gif)

#### [example2](https://github.com/soda480/mppbar/blob/main/examples/example2.py)

Distribute work across multiple processes but only a subset are executing concurrently, each displays a progress bar showing its execution status. Useful if you can only afford to run a few processes concurrently.

<details><summary>Code</summary>

```Python
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
    # designate fill factor for total - to make progress bar look nicer
    fill = {
        'max_total': 100
    }
    print('>> Processing items...')
    # set concurrency to 3 - max of 3 processes will be running at any given time
    pbars =  MPpbar(function=do_work, process_data=process_data, regex=regex, fill=fill, processes_to_start=3, timeout=1)
    results = pbars.execute()
    # add up totals from all processes
    print(f">> {len(process_data)} workers processed a total of {sum(result for result in results)} items")

if __name__ == '__main__':
    main()
```

</details>

![example2](https://raw.githubusercontent.com/soda480/mppbar/main/docs/images/example2.gif)

#### [example3](https://github.com/soda480/mppbar/blob/main/examples/example3.py)

Distribute alot of work across a small set of processes using a thread-safe queue, each process gets work off the queue until there is no more work, all processes reuse a progress bar to show its execution status. Useful if you have alot of data to distribute across a small set of processes.

<details><summary>Code</summary>

```Python
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
```

</details>

![example3](https://raw.githubusercontent.com/soda480/mppbar/main/docs/images/example3.gif)


### Development

Clone the repository and ensure the latest version of Docker is installed on your development server.

Build the Docker image:
```sh
docker image build \
-t \
mppbar:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-v $PWD:/code \
mppbar:latest \
/bin/bash
```

Execute the build:
```sh
pyb -X
```
