from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sql_app import crud, mymodels, schemas, database

app = FastAPI()

mymodels.Base.metadata.create_all(bind=database.engine)

@app.get("/api/characters/{id}", response_model=schemas.Character)
async def get_character(id: int, db: Session = Depends(database.get_db)):
    character = crud.get_character(db, id)
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@app.post("/api/characters", response_model=schemas.Character)
async def create_character(character: schemas.CharacterCreate, db: Session = Depends(database.get_db)):
    return crud.create_character(db, character)

@app.put("/api/characters/{id}/attributes", response_model=schemas.Character)
async def adjust_character_attributes(id: int, adjustments: schemas.AttributeAdjustment, db: Session = Depends(database.get_db)):
    character = crud.update_character(db, id, adjustments)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found or not enough available points")
    return character

@app.post("/api/lobbies", response_model=schemas.Lobby)
async def create_lobby(db: Session = Depends(database.get_db)):
    return crud.create_lobby(db)

@app.post("/api/lobbies/{lobby_id}/join", response_model=schemas.Lobby)
async def join_lobby(lobby_id: int, character_id: int, db: Session = Depends(database.get_db)):
    return crud.join_lobby(db, lobby_id, character_id)

@app.post("/api/lobbies/{lobby_id}/fights", response_model=schemas.Fight)
async def start_fight(lobby_id: int, db: Session = Depends(database.get_db)):
    return crud.start_fight(db, lobby_id)

@app.post("/api/fights/{fight_id}/moves", response_model=schemas.MoveResult)
async def make_move(fight_id: int, attack: schemas.Move, block: schemas.Move, block2: schemas.Move, db: Session = Depends(database.get_db)):
    return crud.make_move(db, fight_id, attack, block, block2)

@app.delete("/api/fights/{fight_id}", response_model=schemas.EndFightResult)
async def end_fight(fight_id: int, db: Session = Depends(database.get_db)):
    return crud.end_fight(db, fight_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
