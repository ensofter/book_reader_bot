from aiogram.types import Message
from aiogram import Router

router = Router()


@router.message()
async def handle_every_message(message: Message):
    await message.answer(f'Hello World! - {message.text}')
