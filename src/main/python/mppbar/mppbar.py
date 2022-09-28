import re
import sys
import logging
from colorama import Cursor
from colorama import init as colorama_init
import cursor
from mpmq import MPmq
from progress1bar import ProgressBar
from list2term import Lines

logger = logging.getLogger(__name__)

MAX_LINES = 75
CLEAR_EOL = '\033[K'


class MPpbar(MPmq):
    """ a subclass of MPmq providing multi-processing enabled progress bars
    """
    regex = {
        'total': r'^processing total of (?P<value>\d+) items$',
        'count': r'^processed .*$',
        'alias': r'^worker is (?P<value>.*)$'
    }

    def __init__(self, function, process_data=None, shared_data=None, processes_to_start=None, timeout=None, **kwargs):
        logger.debug('executing MPpbar constructor')
        # call parent constructor
        super().__init__(function, process_data=process_data, shared_data=shared_data, processes_to_start=processes_to_start, timeout=timeout)
        colorama_init()
        self._progress_bars = self._create_progress_bars(kwargs)
        self._lines = Lines(self._progress_bars)

    def get_message(self):
        """ return message from top of message queue
            override parent class method
        """
        message = super().get_message()
        if message['offset'] is None:
            # parse offset from the message
            match = re.match(r'^#(?P<offset>\d+)-(?P<message>.*)$', message['message'], re.M)
            if match:
                return {
                    'offset': int(match.group('offset')),
                    'control': None,
                    'message': match.group('message')
                }
            logger.debug(f'unable to match offset in message {message}')
        return message

    def complete_process(self, offset):
        """ set progress bar to complete and print line out on terminal
            override parent class method
        """
        super().complete_process(offset)
        self._progress_bars[offset].complete = True
        self._lines.print_line(offset)

    def process_message(self, offset, message):
        """ write message to terminal at offset
            override parent class method
        """
        if offset is None:
            logger.warning(f'unable to write {message} line to terminal because offset is None')
            return
        if message == 'reset-mppbar':
            logger.debug(f'resetting progress bar at offset {offset}')
            self._progress_bars[offset].reset()
        elif message == 'reset-mppbar-complete':
            for progress_bar in self._progress_bars:
                progress_bar.complete = True
        else:
            match = self._progress_bars[offset].match(message)
            if match:
                self._lines.print_line(offset)

    def execute_run(self):
        """ hide cursor and print initial progress bars
            override parent class method
        """
        logger.debug('executing run task wrapper')
        self._lines.hide_cursor()
        self._lines.print_lines()
        # call parent method
        super().execute_run()

    def final(self):
        """ print final progress bars and show cursor
            override parent class method
        """
        logger.debug('executing final task')
        for index, progress_bar in enumerate(self._progress_bars):
            progress_bar.duration = self.processes[index]['duration']
        self._lines.print_lines(force=True)
        self._lines.show_cursor()

    def _create_progress_bars(self, kwargs):
        """ create and return list of progress bars
        """
        logger.debug('creating progress bars')
        # progress bar printing will be controlled externally by the MPpbars class
        kwargs['control'] = True
        if not kwargs.get('regex'):
            # assign default progress bar
            kwargs['regex'] = MPpbar.regex
        progress_bars = []
        for _, _ in enumerate(self.process_data):
            progress_bars.append(ProgressBar(**kwargs))
        return progress_bars
