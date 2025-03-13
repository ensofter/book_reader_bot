from aiogram import Router, F
from copy import deepcopy

from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from database.database import user_dict_template, users_db
from filters.filters import IsDigitCallbackData, IsDelBookmarkCallbackData
from keyboards.bookmarks_kb import create_bookmark_keyboard, create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import book



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

@router.callback_query(F.text == 'forward')
async def handle_clbck_forward(callback: CallbackQuery):
    if users_db[callback.from_user.id]['page'] < len(book):
        users_db[callback.from_user.id]['page'] += 1
        text = book[users_db[callback.from_user.id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=await create_pagination_keyboard(
                'backward',
                f'{users_db[callback.from_user.id]["page"]}'/'{len(book)}',
                'forward'
            )
        )
    await callback.answer()
