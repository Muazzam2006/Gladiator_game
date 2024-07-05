from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from enum import Enum

app = FastAPI()

characters = []

class Character(BaseModel):
    id: int = len(characters) + 1
    name: str
    strength: int = 10
    agility: int = 10
    stamina: int = 10
    level: int = 1
    availablePoints: int = 0
    health: int = 120
    experience: int = 0

    def increase_xp(self, xp: int):
        self.experience += xp
        if self.experience >= self.level * 100: 
            self.level += 1
            self.availablePoints += 5
            self.health += self.stamina // 2

        
class Bot(BaseModel):
    id: int
    name: str
    strength: int
    agility: int
    stamina: int
    health: int = 120


class AttributeAdjustment(BaseModel):
    strength: int
    agility: int
    stamina: int


class Lobby(BaseModel):
    lobbyId: int
    players: list[Character] = []


class Fight(BaseModel):
    fightId: int
    lobbyId: int
    playerTurn: bool
    playerHealth: int
    opponentHealth: int
    playerId: int
    botId: int

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
    fightOver: bool
    victory: bool

class EndFightResult(BaseModel):
    winner: str
    experience: int


@app.get("/api/characters/{id}")
def get_character(id: int):
    chc = list(filter(lambda ch: ch.id == id, characters))
    if not chc:
        raise HTTPException(status_code=404, detail="Character not found")
    return chc[0]


@app.post("/api/characters")
async def create_character(name_: str):
    ch = Character(name=name_)
    characters.append(ch)
    return ch

# тут нужно добавить логику level-ов потом
@app.put("/api/characters/{id}/attributes")
async def adjust_character_attributes(c_id: int, adjustments: AttributeAdjustment):
    chc = next((ch for ch in characters if ch.id == c_id), None)
    if not chc:
        raise HTTPException(status_code=404, detail="Character not found")
    else:
        if (adjustments.strength + adjustments.agility + adjustments.stamina) > chc.availablePoints:
            raise HTTPException(status_code=400, detail="Not enough available points")
        else:
            chc.strength += adjustments.strength
            chc.agility += adjustments.agility
            chc.stamina += adjustments.stamina
            chc.availablePoints -= (adjustments.strength + adjustments.agility + adjustments.stamina)
            return chc


lobbies = []

    

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
    bot_strength = random.randint(1, 20)
    bot_agility = random.randint(1, 30-bot_strength-1)
    bot_stamina = random.randint(1, 30-bot_strength-bot_agility)
    bot = Bot(
        id=bot_id,
        name=f"Bot {bot_id}",
        strength=bot_strength,
        agility=bot_agility,
        stamina=bot_stamina,
        health=120
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


@app.post("/api/fights/{fightId}/moves", response_model=MoveResult)
async def make_move(fightId: int, attack: Move, block: Move, block2: Move):
    fight = next((fight for fight in fights if fight.fightId == fightId), None)
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    fightOver = fight.opponentHealth <= 0 or fight.playerHealth <= 0
    victory = fight.opponentHealth <= 0

    if fightOver:
        raise HTTPException(status_code=400, detail="Fight is Over")
    
    else:
        character = next((char for char in characters if char.id == fight.playerId), None)
        bot = next((b for b in bots if b.id == fight.botId), None)

        bot_attack = random.choice(list(Move))
        bot_block = random.sample(list(Move), 2)

        playerHit = attack not in bot_block
        playerDamageDealt = character.strength + 5 if playerHit else 0 
        fight.opponentHealth -= (playerDamageDealt - (1 if character.agility > 20 else 2 * character.agility // 100))

        bot_attack = random.choice(list(Move))
        bot_block = random.sample(list(Move), 2)

        opponentHit = bot_attack != block and bot_attack != block2
        opponentDamageDealt = bot.strength + 5 if opponentHit else 0 
        fight.playerHealth -= (opponentDamageDealt - (1 if bot.agility > 20 else 2 * bot.agility // 100))

        return MoveResult(
            playerHit=playerHit,
            opponentHit=opponentHit,
            playerDamageDealt=playerDamageDealt,
            opponentDamageDealt=opponentDamageDealt,
            playerHealth=fight.playerHealth,
            opponentHealth=fight.opponentHealth,
            fightOver=fightOver,
            victory=victory
        )


@app.delete("/api/fights/{fightId}", response_model=EndFightResult)
async def end_fight(fightId: int):
    fight = next((fight for fight in fights if fight.fightId == fightId), None)
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")

    character = next((char for char in characters if char.id == fight.playerId), None)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if not (fight.opponentHealth <= 0 or fight.playerHealth <= 0):
        raise HTTPException(status_code=400, detail="Fight isn't over")
    else:
        xp = 100  
        winner = "player" if fight.opponentHealth <= 0 else "bot"

        if winner == "player":
            character.increase_xp(xp)

        fights.remove(fight)

        return EndFightResult(
            winner=winner,
            experience=xp if winner == "player" else 0
        )


if __name__ == "__main2__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
