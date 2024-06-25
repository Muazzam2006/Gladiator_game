from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from enum import Enum

app = FastAPI()

characters = []

class Character(BaseModel):
    id: int = len(characters) + 1
    name: str
    strength: int = 0
    agility: int = 0
    stamina: int = 0
    level: int = 1
    availablePoints: int = 30
    health: int = 100
    experience: int = 0

    def attack_power(self):
        return self.strength

    def critical_chance(self):
        return min(50, self.agility * 2)

    def dodge_chance(self):
        return min(50, self.agility * 2)
    


class Bot(BaseModel):
    id: int
    name: str
    strength: int
    agility: int
    stamina: int
    health: int = 100

    def attack_power(self):
        return self.strength

    def critical_chance(self):
        return min(50, self.agility * 2)

    def dodge_chance(self):
        return min(50, self.agility * 2)


class AttributeAdjustment(BaseModel):
    strength: int
    agility: int
    stamina: int


@app.get("/api/characters/{id}")
def get_character(id: int):
    chc = list(filter(lambda ch: ch["id"] == id, characters))
    if not chc:
        raise HTTPException(status_code=404, detail="Character not found")
    return chc[0]


@app.post("/api/characters")
async def create_character(name_: str):
    ch = Character(name=name_)
    characters.append(ch)
    return ch


@app.put("/api/characters/{id}/attributes")
async def adjust_character_attributes(c_id: int, adjustments: AttributeAdjustment):
    chc = next((ch for ch in characters if ch.id == c_id), None)
    if not chc:
        raise HTTPException(status_code=404, detail="Character not found")
    else:
        # chc = chc[0]
        if (adjustments.strength + adjustments.agility + adjustments.stamina) > chc.availablePoints:
            raise HTTPException(status_code=400, detail="Not enough available points")
        else:
            chc.strength = adjustments.strength
            chc.agility = adjustments.agility
            chc.stamina = adjustments.stamina
            chc.availablePoints -= (adjustments.strength + adjustments.agility + adjustments.stamina)
            return chc


lobbies = []

class Lobby(BaseModel):
    lobbyId: int
    players: list[Character] = []
    

@app.post("/api/lobbies", response_model=Lobby)
async def create_lobby():
    lobby_id = len(lobbies) + 1
    new_lobby = Lobby(lobbyId=lobby_id, players=[])
    lobbies.append(new_lobby)
    return new_lobby


@app.post("/api/lobbies/{lobbyId}/join", response_model=Lobby)
async def join_lobby(lobbyId: int, characterId: int):
    lb = next((lobby for lobby in lobbies if lobby.lobbyId == lobbyId), None)
    if not lb:
        raise HTTPException(status_code=404, detail="Lobby not found")
    elif lb.players:
        raise HTTPException(status_code=400, detail="Lobby already has a character")
    else:
        chc = next((ch for ch in characters if ch.id == characterId), None)
        if not chc:
            raise HTTPException(status_code=404, detail="Character not found")
        else:
            lb.players.append(chc)
            return lb



fights = []

class Fight(BaseModel):
    fightId: int
    lobbyId: int
    playerTurn: bool
    playerHealth: int
    opponentHealth: int
    playerId: int
    botId: int

bots = []

@app.post("/api/lobbies/{lobbyId}/fights", response_model=Fight)
async def start_fight(lobbyId: int):
    lobby = next((lobby for lobby in lobbies if lobby.lobbyId == lobbyId), None)
    if not lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if not lobby.players:
        raise HTTPException(status_code=400, detail="No characters in lobby to start a fight")

    character = lobby.players[0]
    
    bot_id = len(bots) + 1
    bot_strength = random.randint(5, 15)
    bot_agility = random.randint(5, 15)
    bot_stamina = random.randint(5, 15)
    bot = Bot(
        id=bot_id,
        name=f"Bot {bot_id}",
        strength=bot_strength,
        agility=bot_agility,
        stamina=bot_stamina,
        health=bot_stamina * 10
    )
    bots.append(bot)

    fight_id = len(fights) + 1
    new_fight = Fight(
        fightId=fight_id, 
        lobbyId=lobbyId, 
        playerTurn=True, 
        playerHealth=character.health, 
        opponentHealth=bot.health,
        playerId=character.id,
        botId=bot.id
    )
    fights.append(new_fight)
    return new_fight

class Move(str, Enum):
    head = "head"
    chest = "chest"
    groin = "groin"
    legs = "legs"



class MoveResult(BaseModel):
    playerHit: bool
    opponentHit: bool
    playerDamageDealt: int
    opponentDamageDealt: int
    playerHealth: int
    opponentHealth: int


@app.post("/api/fights/{fightId}/moves", response_model=MoveResult)
async def make_move(fightId: int, attack: Move, block: Move, block2: Move):
    fight = next((fight for fight in fights if fight.fightId == fightId), None)
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")

    if not fight.playerTurn:
        raise HTTPException(status_code=400, detail="Not player's turn")

    
    character = next((char for char in characters if char.id == fight.playerId), None)
    bot = next((b for b in bots if b.id == fight.botId), None)

    playerHit = attack != block and attack != block2
    critical_hit = random.random() < (character.critical_chance() / 100)
    playerDamageDealt = character.attack_power() * (1.5 if critical_hit else 1) if playerHit else 0

    fight.opponentHealth -= playerDamageDealt

    bot_attack = random.choice(list(Move))
    bot_block = random.sample(list(Move), 2)

    opponentHit = bot_attack != block and bot_attack != block2
    critical_hit = random.random() < (bot.critical_chance() / 100)
    opponentDamageDealt = bot.attack_power() * (1.5 if critical_hit else 1) if opponentHit else 0

    fight.playerHealth -= opponentDamageDealt

    fight.playerTurn = not fight.playerTurn

    return MoveResult(
        playerHit=playerHit,
        opponentHit=opponentHit,
        playerDamageDealt=playerDamageDealt,
        opponentDamageDealt=opponentDamageDealt,
        playerHealth=fight.playerHealth,
        opponentHealth=fight.opponentHealth
    )

