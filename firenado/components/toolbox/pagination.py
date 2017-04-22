from collections import namedtuple


def page_first_row(page, rows_per_page=10):
    return (int(page) * int(rows_per_page)) + 1 - int(rows_per_page)


class Paginator(object):

    def __init__(self, row_count, current_page=None, rows_per_page=10,
                 pages_per_block=10):
        if current_page is None or current_page == 0:
            current_page = 1

        self.row_count = row_count
        self.rows_per_page = rows_per_page
        self.rows_last_page = 0

        self.current_page = int(current_page)
        self.page_count = 1

        self.block_count = 0
        self.current_block = 0
        self.pages_per_block = pages_per_block
        self.pages_last_block = 0

        self.current_first_row = 0
        self.current_last_row = 0

        self.block_first_page = 0
        self.block_last_page = 0

        # Setting page count
        if self.row_count > 0:
            self.page_count = int(self.row_count/self.rows_per_page) + (
                1 if self.row_count % self.rows_per_page else 0)

        # Fixed current if overflows the row count
        if self.page_count < self.current_page:
            self.current_page = self.page_count

        # Setting rows in the last page
        self.rows_last_page = self.rows_per_page if not(
            self.row_count % self.rows_per_page) else (
            self.row_count % self.rows_per_page)

        # Setting block count
        self.block_count = int(self.page_count / self.pages_per_block) + (
            1 if self.page_count % self.pages_per_block else 0)

        # Setting pages in the last block of pages
        if self.page_count < self.pages_per_block:
            self.pages_last_block = self.page_count
        else:
            self.pages_last_block = self.pages_per_block if not(
                self.page_count % self.pages_per_block) else (
                self.page_count % self.pages_per_block)

        # Setting current block of pages
        if self.current_page <= self.pages_per_block:
            self.current_block = 1
        else:
            self.current_block = int(
                self.current_page / self.pages_per_block) + (
                1 if self.current_page % self.pages_per_block else 0)

        # Setting current first row
        self.current_first_row = page_first_row(self.current_page,
                                                self.rows_per_page)
        # Setting current last row
        if self.current_page == self.page_count:
            self.current_last_row = (self.current_first_row +
                                     self.rows_last_page - 1)
        else:
            self.current_last_row = (self.current_page * self.rows_per_page)

        # Setting current first page
        self.block_first_page = ((self.current_block * self.pages_per_block
                                    ) + 1 - self.pages_per_block)
        # Setting current last page
        if self.current_block == self.block_count:
            self.block_last_page = (self.block_first_page +
                                    self.pages_last_block - 1)
        else:
            self.block_last_page = (self.current_block *
                                    self.pages_per_block)

    @property
    def is_first_page(self):
        if self.current_page == 1:
            return True
        return False

    @property
    def is_last_page(self):
        if self.current_page == self.page_count:
            return True
        return False

    @property
    def block_pages(self):
        return range(self.block_first_page, self.block_last_page+1)

PagedData = namedtuple('PagedData', ['data', 'count'])
