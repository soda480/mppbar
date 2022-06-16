import re
import sys
import logging
from colorama import Cursor, init as colorama_init
import cursor
from mpmq import MPmq
from progress1bar import ProgressBar

logger = logging.getLogger(__name__)

MAX_LINES = 75
CLEAR_EOL = '\033[K'


class MPpbar(MPmq):
    """ a subclass of MPmq providing multi-processing enabled progress bars
    """
    def __init__(self, *args, regex=None, fill=None, **kwargs):
        logger.debug('executing MPpbar constructor')
        self.regex = regex
        self.fill = fill
        # call parent constructor
        super().__init__(*args, **kwargs)
        colorama_init()
        self._current = 0
        self._create_progress_bars()

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
            self._progress_bars[offset].match(message)
            self._print_progress_bar(offset)

    def execute_run(self):
        """ hide cursor and print initial progress bars
            override parent class method
        """
        logger.debug('executing run task wrapper')
        self._hide_cursor()
        self._print_progress_bars()
        # call parent method
        super().execute_run()

    def final(self):
        """ print final progress bars and show cursor
            override parent class method
        """
        logger.debug('executing final task')
        self._print_progress_bars(add_duration=True, force=True)
        self._show_cursor()

    def _create_progress_bars(self):
        """ create and return list of progress bars
        """
        logger.debug('creating progress bars')
        self._progress_bars = []
        for offset, _ in enumerate(self.process_data):
            progress_bar = ProgressBar(offset, fill=self.fill, regex=self.regex, control=True)
            self._progress_bars.append(progress_bar)

    def _print_progress_bar(self, offset, force=False):
        """ move to offset and print progress bar at offset
        """
        if sys.stderr.isatty() or force:
            move_char = self._get_move_char(offset)
            print(f'{move_char}{CLEAR_EOL}', end='', file=sys.stderr)
            print(self._progress_bars[offset], file=sys.stderr)
            sys.stderr.flush()
            self._current += 1

    def _print_progress_bars(self, add_duration=False, force=False):
        """ print all progress bars
        """
        logger.info('printing progress bars')
        for offset, _ in enumerate(self._progress_bars):
            if add_duration:
                self._progress_bars[offset].duration = self.processes.get(offset, {}).get('duration')
            self._print_progress_bar(offset, force=force)

    def _get_move_char(self, offset):
        """ return char to move to offset
        """
        move_char = ''
        if offset < self._current:
            move_char = self._move_up(offset)
        elif offset > self._current:
            move_char = self._move_down(offset)
        return move_char

    def _move_down(self, offset):
        """ return char to move down to offset and update current
        """
        diff = offset - self._current
        self._current += diff
        return Cursor.DOWN(diff)

    def _move_up(self, offset):
        """ return char to move up to offset and update current
        """
        diff = self._current - offset
        self._current -= diff
        return Cursor.UP(diff)

    def _show_cursor(self):
        """ show cursor
        """
        if sys.stderr.isatty():
            cursor.show()

    def _hide_cursor(self):
        """ hide cursor
        """
        if sys.stderr.isatty():
            cursor.hide()
