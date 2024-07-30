from http.client import HTTPException
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
from models.models import metadata, Device, Akb, DeviceAKB

app = FastAPI()
DATABASE_URL = "sqlite:///./devices.db"
engine = create_engine(DATABASE_URL)
metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DeviceCreateModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class AkbCreateModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
class AkbCreate(BaseModel):
    name: str
class DeviceCreate(BaseModel):
    name: str
    akb_id: int
    akb_ids: List[int]

class DeviceCreateDeviceModel(BaseModel):
    name: str
    akb_id:Optional[int] = 1
    akb_ids: List[int]

class DeviceModel(BaseModel):
    id: int
    name: str
    akb_id: int

class AKBModel(BaseModel):
    id: int
    name: str



#главная страница
@app.get("/", response_class=HTMLResponse)
def view_devices(request: Request, db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    akbs = db.query(Akb).all()
    return templates.TemplateResponse("index.html", {"request": request, "devices": devices, "akbs": akbs})

#Связка электроники
@app.get("/bunch", response_class=HTMLResponse)
async def devices_with_akbs(request: Request, db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    akbs = db.query(Akb).all()
    device_akb_relations = db.query(DeviceAKB).all()
    device_akb_map = {}
    for device in devices:
        device_id = device.id
        device_akb_map[device_id] = []
    for relation in device_akb_relations:
        device_id = relation.device_id
        akb_id = relation.akb_id
        device_akb_map[device_id].append(akb_id)
    return templates.TemplateResponse("bunch.html",{"request": request,"devices": devices,"akbs": akbs,"device_akb_map": device_akb_map}
    )

#  отоброзить на странице новые акб
@app.get("/new_akb", response_class=HTMLResponse)
def new_akb(request: Request, db: Session = Depends(get_db)):
    akb_list = db.query(Akb).all()
    return templates.TemplateResponse("new_akb.html", {"request": request, "akb_list": akb_list})
# реально cоздать новы акб
@app.post("/new_akb", response_model=dict)
def create_akb(akb: AkbCreate, db: Session = Depends(get_db)):
    try:
        print(akb.dict())
        query = Akb.insert().values(name=akb.name)
        last_record_id = db.execute(query)
        db.commit()
        return {"id": last_record_id.inserted_primary_key[0], "name": akb.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# отоброзить на странице новые девайс
@app.get("/new_device", response_class=HTMLResponse)
async def new_device(request: Request, db: Session = Depends(get_db)):
    akb_list = db.query(Akb).all()  # Получаем список аккумуляторов
    device_list = db.query(Device).all()  # Получаем список устройств
    return templates.TemplateResponse("new_device.html", {"request": request, "akb_list": akb_list, "device_list": device_list})

# Создать новый девайс
@app.post("/devices/post", response_model=dict)
def create_device(device: DeviceCreateDeviceModel, db: Session = Depends(get_db)):
    # Создаем новое устройство
    query = Device.insert().values(name=device.name, akb_id=device.akb_id)
    last_record_id = db.execute(query)
    db.commit()
    new_device_id = last_record_id.inserted_primary_key[0]
    for akb_id in device.akb_ids:
        db.execute(DeviceAKB.insert().values(device_id=new_device_id, akb_id=akb_id))

    db.commit()

    return {"id": new_device_id, "name": device.name}




@app.put("/akb/{akb_id}", response_model=dict)
def update_akb(akb_id: int, akb: AkbCreate, db: Session = Depends(get_db)):
    query = Akb.update().where(Akb.c.id == akb_id).values(name=akb.name)
    result = db.execute(query)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="AKB not found")
    return {"id": akb_id, "name": akb.name}

@app.put("/devices/{device_id}", response_model=dict)
def update_device(device_id: int, device: DeviceCreate, db: Session = Depends(get_db)):
    # Обновление элемента в таблице device
    query = Device.update().where(Device.c.id == device_id).values(name=device.name, akb_id=device.akb_id)
    result = db.execute(query)  # Выполнение запроса обновления
    db.commit()  # Коммит изменений

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    return {"id": device_id, "name": device.name, "akb_id": device.akb_id}



# отоброзить на странице akb
@app.get("/akb", response_model=list[dict])
def get_devices(request: Request, db: Session = Depends(get_db)):
    devices = db.query(Akb).all()
    return templates.TemplateResponse("akb.html", {"request": request, "devices": devices})
# удалить на странице akb
@app.delete("/akb/{akb_id}", response_model=dict)
def delete_akb(akb_id: int, db: Session = Depends(get_db)):
    query = Akb.delete().where(Akb.c.id == akb_id)
    result = db.execute(query)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="AKB not found")

    return {"detail": "AKB deleted", "id": akb_id}
# отоброзить на странице девайсы
@app.get("/devices", response_model=list[dict])
def get_devices(request: Request,db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return templates.TemplateResponse("devices.html", {"request": request, "devices": devices})
# удалить на странице устройства
@app.delete("/devices/{device_id}", response_model=dict)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    query = Device.delete().where(Device.c.id == device_id)
    result = db.execute(query)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    return {"detail": "Device deleted", "id": device_id}

# api на акб
@app.get("/akbs_all/", response_model=List[AkbCreateModel])
def read_akbs(db: Session = Depends(get_db)):
    akbs = db.query(Akb).all()
    return akbs

# api на девайсы
@app.get("/devices_all/", response_model=List[DeviceCreateModel])
def read_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return devices