import os
import sys

import logging

logger = logging.getLogger(__name__)

BOOK_PATH = 'book/kogda_dyhanie_rastvoryaetsya_v_vozduhe.txt'
PAGE_SIZE = 1050

book: dict[int, str] = {}


# функция возвращающая строку с текстом страницы и ее размер
def _get_part_text(text, start, page_size):
    symbs = '.,:;!?'
    fragment = (text + '\n')[start:start+page_size+1].rstrip(symbs)
    last_symb_idx = len(fragment)
    for i in range(len(fragment)-1, -1, -1):
        if fragment[i] in symbs:
            last_symb_idx = i
            break
    return fragment[:last_symb_idx+1], last_symb_idx + 1


# функция формирующая словарь книги
def prepare_book(path: str) -> None:
    with open(file=path, encoding='utf-8', mode='r') as f:
        full_text = f.read()
        len_full_text = len(full_text)
        start = 0
        page_number = 1
        while len_full_text > start+1:
            page, step = _get_part_text(full_text, start, PAGE_SIZE)
            book[page_number] = page.lstrip()
            start += step
            page_number += 1


# вызов функции prepare_book для подготовки книги из текстового файла
prepare_book(os.path.join(sys.path[0], os.path.normpath(BOOK_PATH)))
