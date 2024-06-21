from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Character(BaseModel):
    id: int
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

@app.get("/api/characters/{id}")
async def get_character(id: int):
    for character in characters:
        if character.get("id") == id:
            return character
    return {"response": "Character not found"}

@app.post("/api/characters")
async def create_character(character: Character):
    characters.append(character)
    return characters

@app.put("/api/characters/{g_id}/attributes")
async def adjust_character_attributes(g_id: int, adjustments: AttributeAdjustment):
    character = characters[g_id]
    if g_id not in characters:
        return {"response": "Character not found"}
    if (adjustments.strength + adjustments.agility + adjustments.stamina) > character.availablePoints:
        return {"response": "Not enough available points"}
    character.strength = adjustments.strength
    character.agility = adjustments.agility
    character.stamina = adjustments.stamina
    character.availablePoints -= (adjustments.strength + adjustments.agility + adjustments.stamina)
    return character

