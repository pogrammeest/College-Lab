from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Teams(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    raiting = Column(Float)


class FootballPlayers(Base):
    __tablename__ = "football_players"
    fb_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
