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


characters: dict[int, Character] = {}

@app.get("/api/characters/{id}")
async def get_character(id: int):
    result = []
    for character in characters:
        if character.get("id") == id:
            result.append(character)
    return result

@app.post("/api/characters")
async def create_character(character: Character):
    characters.append(character)
    return (character, characters)

@app.put("/api/characters/{id}/attributes")
async def adjust_character_attributes(id: int, adjustments: AttributeAdjustment):
    if id not in characters:
        return {"response": "Character not found"}
    character = characters[id]
    if adjustments.strength + adjustments.agility + adjustments.stamina > character.availablePoints:
        return {"response": "Not enough available points"}
    character.strength = adjustments.strength
    character.agility = adjustments.agility
    character.stamina = adjustments.stamina
    character.availablePoints -= (adjustments.strength + adjustments.agility + adjustments.stamina)
    return character

