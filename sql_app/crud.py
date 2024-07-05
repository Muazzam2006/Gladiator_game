from sqlalchemy.orm import Session
from sql_app import mymodels, schemas
from fastapi import HTTPException
import random

def get_character(db: Session, character_id: int):
    return db.query(mymodels.Character).filter(mymodels.Character.char_id == character_id).first()

def create_character(db: Session, character: schemas.CharacterCreate):
    db_character = mymodels.Character(name=character.name)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def update_character(db: Session, character_id: int, adjustments: schemas.AttributeAdjustment):
    character = db.query(mymodels.Character).filter(mymodels.Character.char_id == character_id).first()
    if not character:
        return None
    if (adjustments.strength + adjustments.agility + adjustments.stamina) > character.availablePoints:
        return None
    character.strength += adjustments.strength
    character.agility += adjustments.agility
    character.stamina += adjustments.stamina
    character.availablePoints -= (adjustments.strength + adjustments.agility + adjustments.stamina)
    db.commit()
    db.refresh(character)
    return character

def create_lobby(db: Session):
    db_lobby = mymodels.Lobby()
    db.add(db_lobby)
    db.commit()
    db.refresh(db_lobby)
    return db_lobby

def join_lobby(db: Session, lobby_id: int, character_id: int):
    db_lobby = db.query(mymodels.Lobby).filter(mymodels.Lobby.lobby_id == lobby_id).first()
    if not db_lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if db_lobby.players:
        raise HTTPException(status_code=400, detail="Lobby already has a character")

    db_character = db.query(mymodels.Character).filter(mymodels.Character.char_id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    db_lobby.characters.append(db_character)
    db.commit()
    db.refresh(db_lobby)
    return db_lobby


# ХАТОООО!!!!!!
def start_fight(db: Session, lobby_id: int):
    db_lobby = db.query(mymodels.Lobby).filter(mymodels.Lobby.lobby_id == lobby_id).first()
    if not db_lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")

    if not db_lobby.players:
        raise HTTPException(status_code=400, detail="No characters in lobby to start a fight")

    character = db_lobby.players[0]
    
    bot_strength = random.randint(1, 20)
    bot_agility = random.randint(1, 30 - bot_strength - 1)
    bot_stamina = random.randint(1, 30 - bot_strength - bot_agility)
    
    bot = mymodels.Bot(
        name=f"Bot {bot_strength}", 
        strength=bot_strength,
        agility=bot_agility,
        stamina=bot_stamina,
        health=120
    )
    db.add(bot)
    db.commit()
    db.refresh(bot)

    new_fight = mymodels.Fight(
        lobby_id=lobby_id,
        playerTurn=True,
        playerHealth=character.health,
        opponentHealth=bot.health,
        playerId=character.char_id,
        botId=bot.bot_id
    )
    db.add(new_fight)
    db.commit()
    db.refresh(new_fight)
    return new_fight





def make_move(db: Session, fight_id: int, attack: schemas.Move, block: schemas.Move, block2: schemas.Move):
    fight = db.query(mymodels.Fight).filter(mymodels.Fight.fight_id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")

    fight_over = fight.opponentHealth <= 0 or fight.playerHealth <= 0
    victory = fight.opponentHealth <= 0

    if fight_over:
        raise HTTPException(status_code=400, detail="Fight is Over")
    
    character = db.query(mymodels.Character).filter(mymodels.Character.char_id == fight.playerId).first()
    bot = db.query(mymodels.Bot).filter(mymodels.Bot.bot_id == fight.botId).first()

    bot_attack = random.choice(list(schemas.Move))
    bot_block = random.sample(list(schemas.Move), 2)

    player_hit = attack not in bot_block
    player_damage_dealt = character.strength + 5 if player_hit else 0 
    fight.opponentHealth -= (player_damage_dealt - (1 if character.agility > 20 else 2 * character.agility // 100))

    opponent_hit = bot_attack != block and bot_attack != block2
    opponent_damage_dealt = bot.strength + 5 if opponent_hit else 0 
    fight.playerHealth -= (opponent_damage_dealt - (1 if bot.agility > 20 else 2 * bot.agility // 100))

    db.commit()
    db.refresh(fight)

    return schemas.MoveResult(
        player_hit=player_hit,
        opponent_hit=opponent_hit,
        player_damage_dealt=player_damage_dealt,
        opponent_damage_dealt=opponent_damage_dealt,
        player_health=fight.playerHealth,
        opponent_health=fight.opponentHealth,
        fight_over=fight_over,
        victory=victory
    )



def end_fight(db: Session, fight_id: int):
    fight = db.query(mymodels.Fight).filter(mymodels.Fight.fight_id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=404, detail="Fight not found")

    character = db.query(mymodels.Character).filter(mymodels.Character.char_id == fight.playerId).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if not (fight.opponentHealth <= 0 or fight.playerHealth <= 0):
        raise HTTPException(status_code=400, detail="Fight isn't over")

    xp = 100
    winner = "player" if fight.opponentHealth <= 0 else "bot"

    if winner == "player":
        character.experience += xp
        db.commit()
        db.refresh(character)

    db.delete(fight)
    db.commit()

    return schemas.EndFightResult(
        winner=winner,
        experience=xp if winner == "player" else 0
    )
