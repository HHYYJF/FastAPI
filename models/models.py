from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker

metadata = MetaData()

Device = Table(
    "device",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("akb_id", ForeignKey("akb.id"))
)

Akb = Table(
    "akb",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String)
)

DeviceAKB = Table(
    "device_akb",
    metadata,
    Column("device_id", ForeignKey("device.id"), primary_key=True),
    Column("akb_id", ForeignKey("akb.id"), primary_key=True)
)