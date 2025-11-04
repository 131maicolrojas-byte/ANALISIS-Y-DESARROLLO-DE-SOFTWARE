# -*- coding: utf-8 -*-
"""
analisis_desarrollo.py

Clase ProyectoSoftware:
Representa un proyecto de análisis y desarrollo de software con atributos y métodos
para gestionar su ciclo de vida, requerimientos, exportación e importación desde/para JSON.

Buenas prácticas aplicadas:
- Tipado con annotations.
- Uso de dataclass para claridad y menos código repetitivo.
- Evitar mutables como valores por defecto (usar None y field en __post_init__).
- Serialización de fechas en formato ISO 8601.
- Manejo básico de errores y mensajes informativos.
- Métodos documentados con docstrings en español.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Type
from datetime import date, datetime
import json
import re
import os


@dataclass
class ProyectoSoftware:
    """
    Clase que modela un proyecto de análisis y desarrollo de software.
    """
    nombre: str
    descripcion: str
    requerimientos: Optional[List[str]] = None
    fase_actual: str = "análisis"
    equipo: Optional[List[str]] = None
    fecha_inicio: Optional[date] = None
    fecha_fin_estimada: Optional[date] = None

    # Lista de fases del ciclo de vida (constante de clase)
    CICLO_VIDA: List[str] = field(default_factory=lambda: [
        "análisis",
        "diseño",
        "desarrollo",
        "pruebas",
        "implementación",
        "mantenimiento"
    ], init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Inicializaciones posteriores a la creación del dataclass:
        - Se asegura que listas no sean None.
        - Valida que la fase_actual sea una fase válida; si no, se ajusta a 'análisis'.
        - Si no se proporciona fecha_inicio, se usa la fecha de hoy.
        """
        if self.requerimientos is None:
            self.requerimientos = []
        if self.equipo is None:
            self.equipo = []

        # Normalizar fase actual a minúsculas y validar
        self.fase_actual = (self.fase_actual or "análisis").strip().lower()
        if self.fase_actual not in self.CICLO_VIDA:
            # Si la fase no es válida, reiniciarla a análisis
            self.fase_actual = "análisis"

        if self.fecha_inicio is None:
            self.fecha_inicio = date.today()

    def mostrar_info(self) -> None:
        """
        Imprime por pantalla toda la información relevante del proyecto.
        Incluye nombre, descripción, fechas, fase actual, equipo y requerimientos.
        """
        print(f"Proyecto: {self.nombre}")
        print(f"Descripción: {self.descripcion}")
        print(f"Fase actual: {self.fase_actual}")
        print(f"Fecha de inicio: {self.fecha_inicio.isoformat() if self.fecha_inicio else 'No definida'}")
        print(f"Fecha fin estimada: {self.fecha_fin_estimada.isoformat() if self.fecha_fin_estimada else 'No definida'}")
        print(f"Equipo ({len(self.equipo)} miembros): {', '.join(self.equipo) if self.equipo else 'No asignado'}")
        print(f"Requerimientos ({len(self.requerimientos)}):")
        if self.requerimientos:
            for idx, req in enumerate(self.requerimientos, start=1):
                print(f"  {idx}. {req}")
        else:
            print("  No hay requerimientos registrados.")
        print(f"Progreso aproximado: {self.resumen_progreso()}%")

    def avanzar_fase(self) -> bool:
        """
        Avanza la fase actual a la siguiente en el ciclo de vida, si no está en la última.
        Retorna True si se avanzó, False si ya estaba en la fase final.
        """
        try:
            idx = self.CICLO_VIDA.index(self.fase_actual)
        except ValueError:
            # Si por alguna razón la fase_actual no está en la lista, resetearla
            self.fase_actual = "análisis"
            idx = 0

        if idx < len(self.CICLO_VIDA) - 1:
            self.fase_actual = self.CICLO_VIDA[idx + 1]
            return True
        else:
            # Ya en la fase final
            return False

    def agregar_requerimiento(self, nuevo_requerimiento: str) -> None:
        """
        Añade un nuevo requerimiento al proyecto.
        - Evita agregar requerimientos vacíos.
        - Evita duplicados exactos (comparación case-insensitive).
        """
        if not nuevo_requerimiento or not nuevo_requerimiento.strip():
            raise ValueError("El requerimiento no puede estar vacío.")

        req_clean = nuevo_requerimiento.strip()
        # Verificar duplicado case-insensitive
        exists = any(r.strip().lower() == req_clean.lower() for r in self.requerimientos)
        if exists:
            # No agregar duplicados exactos
            return
        self.requerimientos.append(req_clean)

    def resumen_progreso(self) -> int:
        """
        Calcula un porcentaje aproximado de progreso según la fase actual.
        Método:
        - Se considera que cada fase tiene el mismo "peso".
        - Retorna un entero redondeado hacia abajo del porcentaje completado.
        Ejemplo: si la fase actual es 'diseño' (índice 1 de 6), se considera 2/6 ~ 33%.
        """
        try:
            idx = self.CICLO_VIDA.index(self.fase_actual)
        except ValueError:
            idx = 0
        # idx es 0-based; suponer progreso = (idx + 1) fases completadas de total
        total = len(self.CICLO_VIDA)
        progreso = int(((idx + 1) / total) * 100)
        return progreso

    def exportar_json(self, ruta: Optional[str] = None, sobrescribir: bool = True) -> str:
        """
        Exporta la información del proyecto a un archivo JSON.
        - ruta: ruta del archivo; si no se especifica, se genera como '<nombre_proyecto_sanitizado>_proyecto.json'
        - sobrescribir: si False y el archivo existe, lanza FileExistsError.
        Retorna la ruta absoluta del archivo creado.
        """
        # Serializar atributos en un diccionario
        def fecha_a_iso(f: Optional[date]) -> Optional[str]:
            return f.isoformat() if f else None

        data: Dict[str, Any] = {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "requerimientos": list(self.requerimientos),
            "fase_actual": self.fase_actual,
            "equipo": list(self.equipo),
            "fecha_inicio": fecha_a_iso(self.fecha_inicio),
            "fecha_fin_estimada": fecha_a_iso(self.fecha_fin_estimada),
            "ciclo_vida": list(self.CICLO_VIDA),
            "progreso_aproximado": self.resumen_progreso()
        }

        # Generar nombre de archivo si no se pasó ruta
        if ruta is None:
            # Sanitizar nombre para crear un filename seguro
            name_safe = re.sub(r"[^0-9a-zA-Z-_]+", "_", self.nombre.strip())
            ruta = f"{name_safe}_proyecto.json"

        abs_path = os.path.abspath(ruta)
        if not sobrescribir and os.path.exists(abs_path):
            raise FileExistsError(f"El archivo {abs_path} ya existe y sobrescribir=False.")

        # Escribir JSON con ensure_ascii=False para mantener acentos, y con indent para legibilidad
        with open(abs_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return abs_path

    @classmethod
    def cargar_json(cls: Type["ProyectoSoftware"], ruta: str) -> "ProyectoSoftware":
        """
        Crea una instancia de ProyectoSoftware a partir de un archivo JSON.
        - ruta: ruta al archivo JSON a cargar.
        Comportamiento:
        - Lanza FileNotFoundError si el archivo no existe.
        - Lanza json.JSONDecodeError si el contenido no es JSON válido.
        - Convierte fechas en formato ISO 8601 a objetos datetime.date.
        - Si faltan campos opcionales, los inicializa con valores por defecto razonables.
        """
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"El archivo especificado no existe: {ruta}")

        with open(ruta, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Helper para convertir strings ISO a date
        def iso_a_fecha(value: Optional[str]) -> Optional[date]:
            if value is None:
                return None
            if not isinstance(value, str) or not value.strip():
                return None
            try:
                # date.fromisoformat acepta 'YYYY-MM-DD'
                return date.fromisoformat(value)
            except Exception:
                # Intentar parseo con datetime si vino con hora (por robustez)
                try:
                    dt = datetime.fromisoformat(value)
                    return dt.date()
                except Exception:
                    # Si no se puede parsear, ignorar (retornar None)
                    return None

        # Extraer campos con valores por defecto si faltan
        nombre = raw.get("nombre", "Proyecto sin nombre")
        descripcion = raw.get("descripcion", "")
        requerimientos = raw.get("requerimientos") or []
        equipo = raw.get("equipo") or []
        fase_actual = raw.get("fase_actual", "análisis")
        fecha_inicio = iso_a_fecha(raw.get("fecha_inicio"))
        fecha_fin_estimada = iso_a_fecha(raw.get("fecha_fin_estimada"))

        # Crear la instancia validando la fase y normalizando listas
        proyecto = cls(
            nombre=nombre,
            descripcion=descripcion,
            requerimientos=list(requerimientos),
            fase_actual=fase_actual,
            equipo=list(equipo),
            fecha_inicio=fecha_inicio,
            fecha_fin_estimada=fecha_fin_estimada
        )

        return proyecto


if __name__ == "__main__":
    # Ejemplo de uso del ProyectoSoftware
    proyecto = ProyectoSoftware(
        nombre="Sistema de Gestión Académica",
        descripcion="Proyecto para gestionar estudiantes, cursos y calificaciones.",
        requerimientos=["Registro de estudiantes", "Asignación de cursos"],
        fase_actual="análisis",
        equipo=["María", "José", "Ana"],
        fecha_inicio=date(2025, 11, 1),
        fecha_fin_estimada=date(2026, 4, 30)
    )

    # Mostrar información inicial
    proyecto.mostrar_info()

    # Agregar un nuevo requerimiento
    proyecto.agregar_requerimiento("Módulo de reportes")
    print("\nDespués de agregar un requerimiento:")
    proyecto.mostrar_info()

    # Avanzar de fase y mostrar el nuevo estado
    if proyecto.avanzar_fase():
        print("\nSe avanzó a la siguiente fase.")
    else:
        print("\nEl proyecto ya está en la fase final.")
    proyecto.mostrar_info()

    # Exportar a JSON
    ruta_guardado = proyecto.exportar_json()
    print(f"\nProyecto exportado a: {ruta_guardado}")

    # Cargar desde JSON para demostrar la función de importación
    print("\nCargando proyecto desde el archivo JSON exportado...")
    proyecto_cargado = ProyectoSoftware.cargar_json(ruta_guardado)
    print("Proyecto cargado:")
    proyecto_cargado.mostrar_info()