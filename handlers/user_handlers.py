import logging
from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from database.database import user_dict_template, users_db
from filters.filters import IsDigitCallbackData, IsDelBookmarkCallbackData
from keyboards.bookmarks_kb import create_bookmark_keyboard, create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import book

logger = logging.Logger(__name__)

router = Router()

@router.message(CommandStart())
async def handle_cmd_start(message: Message):
    await message.answer(LEXICON[message.text])
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)


@router.message(Command(commands='help'))
async def handle_cmd_help(message: Message):
    await message.answer(text=LEXICON[message.text])


@router.message(Command(commands='beginning'))
async def handle_cmd_beginning(message: Message):
    users_db[message.from_user.id]['page'] = 1
    text = book[1]
    await message.answer(
        text=text,
        reply_markup=await create_pagination_keyboard(
            'backward',
            f'{users_db[message.from_user.id]["page"]}/{len(book)}',
            'forward'
        )
    )


@router.message(Command(commands='continue'))
async def handle_cmd_continue(message: Message):
    text = book[users_db[message.from_user.id]['page']]
    await message.answer(
        text=text,
        reply_markup=await create_pagination_keyboard(
            'backward',
            f'{users_db[message.from_user.id]["page"]}/{len(book)}',
            'forward'
        )
    )


@router.message(Command(commands='bookmarks'))
async def handle_cmd_bookmark(message: Message):
    if users_db[message.from_user.id]['bookmarks']:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=await create_bookmark_keyboard(*users_db[message.from_user.id]['bookmarks'])
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


@router.callback_query(F.data == 'forward')
async def handle_clbck_forward(callback: CallbackQuery):
    if users_db[callback.from_user.id]['page'] < len(book):
        users_db[callback.from_user.id]['page'] += 1
        text = book[users_db[callback.from_user.id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=await create_pagination_keyboard(
                'backward',
                f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
                'forward'
            )
        )
    await callback.answer()


@router.callback_query(F.data == 'backward')
async def handle_clbck_backward(callback: CallbackQuery):
    if users_db[callback.from_user.id]['page'] > 1:
        users_db[callback.from_user.id]['page'] -= 1
        text = book[users_db[callback.from_user.id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=await create_pagination_keyboard(
                'backward',
                f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
                'forward',
            )
        )
    else:
        await callback.answer()


@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
async def handle_clbck_add_page_to_bookmarks(callback: CallbackQuery):
    users_db[callback.from_user.id]['bookmarks'].add(
        users_db[callback.from_user.id]['page']
    )
    await callback.answer('Страница добавлена')


@router.callback_query(IsDigitCallbackData())
async def handle_clbck_bookmark_press(callback: CallbackQuery):
    text = book[int(callback.data)]
    users_db[callback.from_user.id]['page'] = int(callback.data)
    await callback.message.edit_text(
        text=text,
        reply_markup=await create_pagination_keyboard(
            'backward',
            f'{users_db[callback.from_user.id]["page"]}/{len(book)}',
            'forward'
        )
    )


@router.callback_query(F.data == 'edit_bookmarks')
async def handle_clbck_bookmarks_edit(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=await create_edit_keyboard(
            *users_db[callback.from_user.id]['bookmarks']
        )
    )


@router.callback_query(F.data == 'cancel')
async def handle_clbck_cancel_bookmarks_edit(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])


@router.callback_query(IsDelBookmarkCallbackData())
async def process_clbck_del_bookmark(callback: CallbackQuery):
    logger.debug(callback.data)
    logger.debug(callback.data[:-3])
    users_db[callback.from_user.id]['bookmarks'].remove(
        int(callback.data[:-3])
    )
    if users_db[callback.from_user.id]['bookmarks']:
        await callback.message.edit_text(
            text=LEXICON['/bookmarks'],
            reply_markup=await create_edit_keyboard(
                *users_db[callback.from_user.id]['bookmarks']
            )
        )
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
