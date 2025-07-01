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

# Conversion manuelle ou nettoyage du modèle
def clean_enums(obj):
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, list):
        return [clean_enums(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: clean_enums(value) for key, value in obj.items()}
    else:
        return obj


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

from fastapi.responses import Response
import yaml

@app.get("/info.yaml", response_class=Response, tags=["observabilité", "gouvernance"])
async def get_info_yaml():
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
    info = Info(metadata=metadata, data=info_data)

    yaml_data = yaml.dump(clean_enums(info.dict()), allow_unicode=True, sort_keys=False)
    return Response(content=yaml_data, media_type="application/x-yaml")

@app.get("/health.yaml", response_model=Health, tags=["observabilité", "statut", "supervision"])
async def get_health():
    # Exemple de données pour la réponse
    info_si = InfoSi(nom="ROC NG", trigramme="SCL", version="2.3.1")
    services = [
        Service(nom="base de donnée", description="base de données Postgres", categorie="sgbdr", uri="https://url_service", statut="UP", tempsReponse=4)
    ]
    health_data = HealthData(statut="UP", infoSi=info_si, services=services)
    metadata = MetaData(versionApi="1.0.2")

    health = Health(metadata=metadata, data=health_data)
    yaml_data = yaml.dump(clean_enums(health.dict()), allow_unicode=True)
    return Response(content=yaml_data, media_type="application/x-yaml")

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    error_content = {
        "message": "Erreur interne",
        "details": str(exc.detail)
    }
    yaml_error = yaml.dump(error_content, allow_unicode=True, sort_keys=False)
    return Response(content=yaml_error, media_type="application/x-yaml", status_code=exc.status_code)


# Lancer l'API avec Uvicorn
# uvicorn app:app --reload
