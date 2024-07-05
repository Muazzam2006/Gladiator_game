from pydantic import BaseModel
from enum import Enum

class CharacterBase(BaseModel):
    name: str

class CharacterCreate(CharacterBase):
    pass

class Character(CharacterBase):
    char_id: int
    strength: int = 10
    agility: int = 10
    stamina: int = 10
    level: int = 1
    availablePoints: int = 0
    health: int = 120
    experience: int = 0

    class Config:
        orm_mode = True

class BotBase(BaseModel):
    name: str
    strength: int
    agility: int
    stamina: int
    health: int = 120

class BotCreate(BotBase):
    pass

class Bot(BotBase):
    bot_id: int

    class Config:
        orm_mode = True

class AttributeAdjustment(BaseModel):
    strength: int
    agility: int
    stamina: int

class LobbyBase(BaseModel):
    lobby_id: int

class LobbyCreate(LobbyBase):
    pass

class Lobby(LobbyBase):
    players: list[Character] = []

    class Config:
        orm_mode = True

class FightBase(BaseModel):
    lobby_id: int
    player_turn: bool
    player_health: int
    opponent_health: int
    player_id: int
    bot_id: int

class FightCreate(FightBase):
    pass

class Fight(FightBase):
    fight_id: int

    class Config:
        orm_mode = True

class Move(str, Enum):
    head = "head"
    chest = "chest"
    groin = "groin"
    legs = "legs"

class MoveResult(BaseModel):
    player_hit: bool
    opponent_hit: bool
    player_damage_dealt: int
    opponent_damage_dealt: int
    player_health: int
    opponent_health: int
    fight_over: bool
    victory: bool

class EndFightResult(BaseModel):
    winner: str
    experience: int

    class Config:
        orm_mode = True
