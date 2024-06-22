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
    if id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    return characters[id]

@app.post("/api/characters")
async def create_character(name_: str):
    ch = Character(name=name_)
    characters.append(ch)
    return ch

@app.put("/api/characters/{g_id}/attributes")
async def adjust_character_attributes(g_id: int, adjustments: AttributeAdjustment):
    character = characters[g_id]
    if g_id not in characters:
        raise HTTPException(status_code=404, detail="Character not found")
    if (adjustments.strength + adjustments.agility + adjustments.stamina) > character.availablePoints:
        raise HTTPException(status_code=400, detail="Not enough available points")
    character.strength = adjustments.strength
    character.agility = adjustments.agility
    character.stamina = adjustments.stamina
    character.availablePoints -= (adjustments.strength + adjustments.agility + adjustments.stamina)
    return character
