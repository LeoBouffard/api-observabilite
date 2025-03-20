from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


app = FastAPI(
    title="Observabilité - OpenAPI 3.1",
    description="API d'observabilité standardisée des systèmes d'information.",
    version="1.0.2",
    contact={
        "name": "Nom Direction Application",
        "email": "adresse.a.definir@intradef.gouv.fr",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
    },
)


class MetaData(BaseModel):
    versionApi: str

class ErreurApi(BaseModel):
    message: str
    details: Optional[str]

class Mention(str, Enum):
    CP = "CP"
    CPP = "CPP"
    CM = "CM"
    CT = "CT"
    CI = "CI"
    CC = "CC"
    CCR = "CCR"
    SF = "SF"
    ACSSI = "ACSSI"
    CRYPTO = "CRYPTO"
    CCI = "CCI"

class InfoSi(BaseModel):
    nom: str
    trigramme: str
    version: str

class Service(BaseModel):
    nom: str
    description: str
    categorie: str
    uri: str
    statut: str
    tempsReponse: int

class HealthData(BaseModel):
    statut: str
    infoSi: InfoSi
    services: List[Service]

class InfoData(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }
    infoSi: InfoSi
    dateVersion: datetime
    environnement: str
    classificationMaxDonnees: str
    mentions: List[Mention]
    niveauArr: str
    niveauService: str
    directionSystemeInformation: str
    directionApplication: str
    typeHomologation: str
    dateFinHomologation: datetime

class Info(BaseModel):
    metadata: MetaData
    data: InfoData

class Health(BaseModel):
    metadata: MetaData
    data: HealthData

@app.get("/info", response_model=Info, tags=["observabilité", "gouvernance"])
async def get_info():
    # Exemple de données pour la réponse
    info_si = InfoSi(nom="ROC NG", trigramme="SCL", version="2.3.1")
    info_data = InfoData(
        infoSi=info_si,
        dateVersion=datetime.now(),
        environnement="production",
        classificationMaxDonnees="DR",
        mentions=[Mention.CP],
        niveauArr="I3",
        niveauService="infogerance",
        directionSystemeInformation="SCL",
        directionApplication="EMA/DORH/BIAR",
        typeHomologation="APE",
        dateFinHomologation=datetime(2024, 7, 21),
    )
    metadata = MetaData(versionApi="1.0.2")
    return Info(metadata=metadata, data=info_data)

@app.get("/health", response_model=Health, tags=["observabilité", "statut", "supervision"])
async def get_health():
    # Exemple de données pour la réponse
    info_si = InfoSi(nom="ROC NG", trigramme="SCL", version="2.3.1")
    services = [
        Service(nom="base de donnée", description="base de données Postgres", categorie="sgbdr", uri="https://url_service", statut="UP", tempsReponse=4)
    ]
    health_data = HealthData(statut="UP", infoSi=info_si, services=services)
    metadata = MetaData(versionApi="1.0.2")
    return Health(metadata=metadata, data=health_data)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return {"message": "Erreur interne", "details": str(exc)}

# Lancer l'API avec Uvicorn
# uvicorn app:app --reload
