from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DuaEntry(BaseModel):
    """
    Representa una casilla específica del Documento Único Administrativo (DUA).
    """
    casilla: str = Field(..., description="Número o identificador de la casilla del DUA")
    valor: str = Field(..., description="Valor contenido en la casilla")
    descripcion: Optional[str] = Field(None, description="Descripción técnica de lo que representa la casilla")

class TradeRequirement(BaseModel):
    """
    Representa un requisito técnico o sigla de comercio exterior (ej. CUD, REOCE).
    """
    sigla: str = Field(..., description="Sigla del requisito (ej. CUD, REOCE, SOIVRE)")
    nombre: str = Field(..., description="Nombre completo del requisito")
    descripcion: str = Field(..., description="Definición técnica según el Manual del Exportador")
    obligatorio: bool = Field(True, description="Indica si es un requisito obligatorio para el despacho")

class ValidationResult(BaseModel):
    """
    Resultado individual de una validación para una casilla o requisito.
    """
    campo: str
    es_valido: bool
    mensaje: str
    sugerencia: Optional[str] = None

class ValidationReport(BaseModel):
    """
    Informe completo de validación del DUA.
    """
    id_validacion: str
    fecha: datetime = Field(default_factory=datetime.now)
    documento_id: str
    resultados: List[ValidationResult]
    resumen_validez: bool
    metadatos: Dict[str, Any] = Field(default_factory=dict)
