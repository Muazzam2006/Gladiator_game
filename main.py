from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

characters = [
    {
        "id": 1, 
        "name": "Character 1", 
        "strength": 0, 
        "agility": 0, 
        "stamina": 0, 
        "level": 1, 
        "availablePoints": 5
    },
    {
        "id": 2,
        "name": "charac2",
        "strength": 0,
        "agility": 0,
        "stamina": 0,
        "level": 1,
        "availablePoints": 5
    }
]

class Character(BaseModel):
    id: int = len(characters) + 1
    name: str
    strength: int = 0
    agility: int = 0
    stamina: int = 0
    level: int = 1
    availablePoints: int = 5

class AttributeAdjustment(BaseModel):
    strength: int
    agility: int
    stamina: int


@app.get("/api/characters/{id}")
def get_character(id: int):
    chc = list(filter(lambda ch: ch.get("id") == id, characters))
    if not chc:
        raise HTTPException(status_code=404, detail="Character not found")
    return chc[0]

@app.post("/api/characters")
async def create_character(name_: str):
    ch = Character(name=name_)
    characters.append(ch)
    return ch

@app.put("/api/characters/{id}/attributes")
async def adjust_character_attributes(id: int, adjustments: AttributeAdjustment):
    chc = list(filter(lambda ch: ch.get("id") == id, characters))
    if not chc:
        raise HTTPException(status_code=404, detail="Character not found")
    else:
        chc = chc[0]
        if (adjustments.strength + adjustments.agility + adjustments.stamina) > chc["availablePoints"]:
            raise HTTPException(status_code=400, detail="Not enough available points")
        else:
            chc["strength"] = adjustments.strength
            chc["agility"] = adjustments.agility
            chc["stamina"] = adjustments.stamina
            chc["availablePoints"] -= (adjustments.strength + adjustments.agility + adjustments.stamina)
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
    else:
        chc = list(filter(lambda ch: ch.get("id") == characterId, characters))
        if not chc:
            raise HTTPException(status_code=404, detail="Character not found")
        else:
            chc = chc[0]
            for l in lobbies:
                if chc in l.players:
                    raise HTTPException(status_code=400, detail="Character is already in a lobby")
            lb.players.append(chc)
            return lb
