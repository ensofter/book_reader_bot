from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str = None
    admin_ids: list[int] = None


@dataclass
class DbConfig:
    db_name: str = None
    db_host: str = None
    db_port: int = None


@dataclass
class TgConfig:
    tg_bot: TgBot = None
    db_conf: DbConfig = None


def load_config():
    env = Env()
    env.read_env()

    return TgConfig(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=[int(i) for i in env.list('ADMIN_IDS')]),
        db_conf=DbConfig(
            db_name='poopa',
            db_host='loopa',
            db_port=666
        )
    )
