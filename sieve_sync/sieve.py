#!/usr/bin/env python3

HEADER_START = '#### Managed by Sieve Sync Start ####'
HEADER_END = '#### Managed by Sieve Sync End ####'


class Sieve:
    def __init__(self, require, start, blocked, middle, rules, end):
        self.require: str = require
        self._start: str = start
        self.blocked: str = blocked
        self._middle: str = middle
        self.rules: str = rules
        self._end: str = end

    def __str__(self):
        return f'{self.require}\n{self._start}\n{self.blocked}\n{self._middle}\n{self.rules}\n{self._end}'

    def __eq__(self, o):
        return self._start == o._start and self._middle == o._middle and self._end == o._end

    @staticmethod
    def from_file(s):
        start_index = s.find(HEADER_START)
        end_index = s.find(HEADER_END)
        require = s[:start_index]
        start = s[start_index:end_index + len(HEADER_END)]
        s = s[end_index + len(HEADER_END):]
        start_index = s.find(HEADER_START)
        end_index = s.find(HEADER_END)
        blocked = s[:start_index]
        middle = s[start_index:end_index + len(HEADER_END)]
        s = s[end_index + len(HEADER_END):]
        start_index = s.find(HEADER_START)
        end_index = s.find(HEADER_END)
        rules = s[:start_index]
        end = s[start_index:end_index + len(HEADER_END)]
        s = s[end_index + len(HEADER_END):]
        return Sieve(require, start, blocked, middle, rules, end)

    def insert_sieve_sync_block(self) -> bool:
        inserted = False
        # print('start', self._start)
        if HEADER_START not in self._start:
            self._start += '\n'
            self._start += HEADER_START
            self._start += "\n"
            self._start += HEADER_END
            self._start += "\n"
            self._start = self._start.strip()
            inserted = True

        # print('middle', self._middle)
        if HEADER_START not in self._middle:
            self._middle += '\n'
            self._middle += HEADER_START
            self._middle += "\n"
            self._middle += HEADER_END
            self._middle += "\n"
            self._middle = self._middle.strip()
            inserted = True

        # print('end', self._end)
        if HEADER_START not in self._end:
            self._end += '\n'
            self._end += HEADER_START
            self._end += "\n"
            self._end += HEADER_END
            self._end += "\n"
            self._end = self._end.strip()
            inserted = True

        return inserted

    def find_content(self, s):
        assert HEADER_START in s and HEADER_END in s
        # Find the indices of the start and end headers
        start_index = s.find(HEADER_START)
        end_index = s.find(HEADER_END)

        result = s[start_index + len(HEADER_START):end_index]
        return result

    def edit_content(self, s, content):
        '''
        content is without HEADER
        '''
        assert HEADER_START in s and HEADER_END in s
        # Find the indices of the start and end headers
        start_index = s.find(HEADER_START)
        end_index = s.find(HEADER_END)

        prolog = s[:start_index]
        epilog = s[end_index+len(HEADER_END):]

        result = f'{prolog}{HEADER_START}{content}{HEADER_END}{epilog}'.strip()
        return result

    @property
    def start(self):
        return self.find_content(self._start)

    @start.setter
    def start(self, value):
        self._start = self.edit_content(self._start, value)

    @property
    def middle(self):
        return self.find_content(self._middle)

    @middle.setter
    def middle(self, value):
        self._middle =  self.edit_content(self._middle, value)

    @property
    def end(self):
        return self.find_content(self._end)

    @end.setter
    def end(self, value):
        self._end = self.edit_content(self._end, value)

    def get_blocks(self):
        return {'start': self.start, 'middle': self.middle, 'end': self.end}

    def edit_blocks(self, start, middle, end):
        self.start = start
        self.middle = middle
        self.end = end
