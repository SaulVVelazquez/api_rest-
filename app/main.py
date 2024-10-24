from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
from databases import Database
from sqlalchemy.orm import Session

# Definir el esquema de la tabla
metadata = MetaData()

personas = Table(
    "personas",
    metadata,
    Column("id_persona", Integer, primary_key=True, index=True),
    Column("nombre", String(100)),
    Column("email", String(100)),
    Column("telefono", String(15)),
)

# URL de la base de datos 
DATABASE_URL = "postgresql://user:PF0WAFqr3W3NgUuWcQL5xpxm0p1Pt9y2@dpg-csc0qvaj1k6c73bo7090-a.oregon-postgres.render.com/db_agenda_zcrm"

# Configurar la base de datos
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)

# Definir la aplicación FastAPI
app = FastAPI()

# Modelo para el endpoint
class Personas(BaseModel):
    nombre: str
    email: str
    telefono: str

# Crear tablas al iniciar la aplicación
@app.on_event("startup")
async def startup():
    metadata.create_all(engine)  # Crea la tabla si no existe
    await database.connect()     # Conecta la base de datos

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()  # Desconecta la base de datos

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Crear nueva persona
@app.post("/postpersonas/")
async def create_persona(persona: Personas):
    query = personas.insert().values(
        nombre=persona.nombre,
        email=persona.email,
        telefono=persona.telefono
    )
    last_record_id = await database.execute(query)
    return {"message": "Persona creada exitosamente", "id_persona": last_record_id}

@app.get("/personas/")
async def get_personas():
    query = personas.select()
    results = await database.fetch_all(query)
    return results

# Ruta para ver las tablas de la base de datos
@app.get("/tables")
async def ver_tablas():
    # Ejecuta la consulta para obtener las tablas
    query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    result = await database.fetch_all(query)
    # Retorna una lista de nombres de tablas
    return {"tables": [table[0] for table in result]}
