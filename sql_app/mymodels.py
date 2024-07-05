from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sql_app.database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")

characters_lobbies = Table(
    "characters_lobbies",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.char_id")),
    Column("lobby_id", Integer, ForeignKey("lobbies.lobby_id"))
)



class Character(Base):
    __tablename__ = "characters"

    char_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    stamina = Column(Integer, default=10)
    level = Column(Integer, default=1)
    availablePoints = Column(Integer, default=0)
    health = Column(Integer, default=120)
    experience = Column(Integer, default=0)
    lobbies = relationship("Lobby", secondary=characters_lobbies, back_populates="players")
    fights = relationship("Fight", back_populates="player")

    # items = relationship("Item", back_populates="owner")

    # def increase_xp(self, xp: int):
    #     self.experience += xp
    #     if self.experience >= self.level * 100: 
    #         self.level += 1
    #         self.availablePoints += 5
    #         self.health += self.stamina // 2

class Bot(Base):
    __tablename__ = "bots"

    bot_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    stamina = Column(Integer, default=10)
    health = Column(Integer, default=120)

    # items = relationship("Item", back_populates="owner")

class Lobby(Base):
    __tablename__ = "lobbies"

    lobby_id = Column(Integer, primary_key=True)
    players = relationship("Character", secondary=characters_lobbies, back_populates="lobbies")

    # items = relationship("Item", back_populates="owner")


class Fight(Base):
    __tablename__ = "fights"

    fight_id = Column(Integer, primary_key=True, index=True)
    lobby_id = Column(Integer, ForeignKey("lobbies.lobby_id"))
    playerTurn = Column(Boolean, default=True)
    playerHealth = Column(Integer)
    opponentHealth = Column(Integer)
    playerId = Column(Integer, ForeignKey("characters.char_id"))
    botId = Column(Integer, ForeignKey("bots.bot_id"))

    lobby = relationship("Lobby", back_populates="fights")
    player = relationship("Character", foreign_keys=[playerId])
    bot = relationship("Bot", foreign_keys=[botId])

