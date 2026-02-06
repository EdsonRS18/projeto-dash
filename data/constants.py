from enum import Enum

estado_para_sigla = {
    "Acre": "ac",
    "Amazonas": "am",
    "Amapá": "ap",
    "Mato Grosso": "mt",
    "Pará": "pa",
    "Rondônia": "ro",
    "Roraima": "rr",
    "Tocantins": "to",
    "Maranhão": "ma"
}
sigla_para_codigo_ibge = {
    "ac": "12",
    "am": "13",
    "ap": "16",
    "ma": "21",
    "mt": "51",
    "pa": "15",
    "ro": "11",
    "rr": "14",
    "to": "17"
}
#enum com as possiveis direções
from enum import Enum

class SankeyDirection(Enum):
    INFECTION_TO_NOTIFICATION = 0
    INFECTION_TO_RESIDENCE = 1
    NOTIFICATION_TO_INFECTION = 2
    RESIDENCE_TO_INFECTION = 3


def direction_columns(direction):
    # 🔒 Normalização (Dash-safe)
    if not isinstance(direction, SankeyDirection):
        direction = SankeyDirection(int(direction))

    match direction:
        case SankeyDirection.INFECTION_TO_NOTIFICATION:
            return 'SIGLA_INFE', 'SIGLA_NOTI'
        case SankeyDirection.INFECTION_TO_RESIDENCE:
            return 'SIGLA_INFE', 'SIGLA_RESI'
        case SankeyDirection.NOTIFICATION_TO_INFECTION:
            return 'SIGLA_NOTI', 'SIGLA_INFE'
        case SankeyDirection.RESIDENCE_TO_INFECTION:
            return 'SIGLA_RESI', 'SIGLA_INFE'
        case _:
            raise ValueError(f"Direção não tratada: {direction}")

#texto das direções
def direction_text(direction):
    # 🔒 Normalização (Dash-safe)
    if not isinstance(direction, SankeyDirection):
        direction = SankeyDirection(int(direction))

    match direction:
        case SankeyDirection.INFECTION_TO_NOTIFICATION:
            return 'Estado de Infecção → Estado de Notificação'
        case SankeyDirection.INFECTION_TO_RESIDENCE:
            return 'Estado de Infecção → Estado de Residência'
        case SankeyDirection.NOTIFICATION_TO_INFECTION:
            return 'Estado de Notificação → Estado de Infecção'
        case SankeyDirection.RESIDENCE_TO_INFECTION:
            return 'Estado de Residência → Estado de Infecção'
        case _:
            return 'Direção desconhecida'
        


class SankeyDirectionMunicipio(Enum):
    INFECTION_TO_NOTIFICATION = 0
    INFECTION_TO_RESIDENCE = 1
    NOTIFICATION_TO_INFECTION = 2
    RESIDENCE_TO_INFECTION = 3


def direction_columns_municipio(direction):
    # 🔒 Normalização (Dash-safe)
    if not isinstance(direction, SankeyDirectionMunicipio):
        direction = SankeyDirectionMunicipio(int(direction))

    match direction:
        case SankeyDirectionMunicipio.INFECTION_TO_NOTIFICATION:
            return 'NOME_INFE', 'NOME_NOTI'
        case SankeyDirectionMunicipio.INFECTION_TO_RESIDENCE:
            return 'NOME_INFE', 'NOME_RESI'
        case SankeyDirectionMunicipio.NOTIFICATION_TO_INFECTION:
            return 'NOME_NOTI', 'NOME_INFE'
        case SankeyDirectionMunicipio.RESIDENCE_TO_INFECTION:
            return 'NOME_RESI', 'NOME_INFE'
        case _:
            raise ValueError(f"Direção municipal não tratada: {direction}")
        
def direction_text_municipio(direction):
    # 🔒 Normalização (Dash-safe)
    if not isinstance(direction, SankeyDirectionMunicipio):
        direction = SankeyDirectionMunicipio(int(direction))

    match direction:
        case SankeyDirectionMunicipio.INFECTION_TO_NOTIFICATION:
            return 'Município de Infecção → Município de Notificação'
        case SankeyDirectionMunicipio.INFECTION_TO_RESIDENCE:
            return 'Município de Infecção → Município de Residência'
        case SankeyDirectionMunicipio.NOTIFICATION_TO_INFECTION:
            return 'Município de Notificação → Município de Infecção'
        case SankeyDirectionMunicipio.RESIDENCE_TO_INFECTION:
            return 'Município de Residência → Município de Infecção'
        case _:
            return 'Direção municipal desconhecida'

