"""
Seed de desarrollo para Active Trace.

Crea:
  Tenant : Demo University
  Roles  : ADMIN, COORDINADOR, PROFESOR, ALUMNO  (globales y por tenant)
  Permisos y relaciones RolPermiso
  Entidades académicas de prueba: Carrera (TUPAD), Cohortes, Materias
  Usuarios y Asignaciones iniciales de comisiones de prueba
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone

# Asegura que /app esté en el path cuando se corre fuera de Docker
sys.path.insert(0, "/app") if "/app" not in sys.path else None

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.core.security import generate_email_hash, hash_password
from app.models.asignacion import Asignacion
from app.models.rol import Rol
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.aviso import Aviso, AlcanceEnum

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------

TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

ROLES = [
    {"nombre": "ADMIN",        "descripcion": "Administrador de tenant"},
    {"nombre": "COORDINADOR",  "descripcion": "Coordinador académico"},
    {"nombre": "PROFESOR",     "descripcion": "Docente / Profesor"},
    {"nombre": "ALUMNO",       "descripcion": "Estudiante"},
]

PERMISOS = [
    {"nombre": "usuarios:gestionar", "descripcion": "Crear, editar o desactivar usuarios del tenant"},
    {"nombre": "tareas:gestionar", "descripcion": "Crear y gestionar tareas internas"},
    {"nombre": "estructura:gestionar", "descripcion": "Crear y gestionar carreras, cohortes y materias"},
    {"nombre": "encuentros:gestionar", "descripcion": "Crear y editar encuentros y slots de disponibilidad"},
    {"nombre": "equipos:asignar", "descripcion": "Asignar docentes a materias/cohortes (equipos)"},
    {"nombre": "comunicacion:enviar", "descripcion": "Redactar y encolar envíos de emails"},
    {"nombre": "comunicacion:aprobar", "descripcion": "Aprobar o rechazar envíos de emails masivos"},
    {"nombre": "calificaciones:importar", "descripcion": "Importar calificaciones desde CSV o Moodle"},
    {"nombre": "avisos:publicar", "descripcion": "Publicar avisos institucionales (tablón)"},
    {"nombre": "auditoria:ver", "descripcion": "Visualizar logs de auditoría"},
    {"nombre": "atrasados:ver", "descripcion": "Visualizar listado y monitor de alumnos atrasados"},
]

MAPEO_ROL_PERMISO = {
    "ADMIN": [p["nombre"] for p in PERMISOS],
    "COORDINADOR": [
        "usuarios:gestionar",
        "tareas:gestionar",
        "estructura:gestionar",
        "encuentros:gestionar",
        "equipos:asignar",
        "comunicacion:enviar",
        "comunicacion:aprobar",
        "calificaciones:importar",
        "avisos:publicar",
        "atrasados:ver",
    ],
    "PROFESOR": [
        "tareas:gestionar",
        "encuentros:gestionar",
        "calificaciones:importar",
        "atrasados:ver",
    ],
    "ALUMNO": []
}

USUARIOS = [
    {
        "nombre":   "Admin",
        "apellidos": "Demo",
        "email":    "admin@demo.com",
        "password": "admin1234",
        "rol":      "ADMIN",
    },
    {
        "nombre":   "Coordinador",
        "apellidos": "Demo",
        "email":    "coordinador@demo.com",
        "password": "coord1234",
        "rol":      "COORDINADOR",
    },
    {
        "nombre":   "Docente",
        "apellidos": "Demo",
        "email":    "docente@demo.com",
        "password": "docente1234",
        "rol":      "PROFESOR",
    },
    {
        "nombre":   "Alumno",
        "apellidos": "Demo",
        "email":    "alumno@demo.com",
        "password": "alumno1234",
        "rol":      "ALUMNO",
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def get_or_create_tenant(session: AsyncSession) -> Tenant:
    result = await session.execute(select(Tenant).where(Tenant.id == TENANT_ID))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(id=TENANT_ID, name="Demo University")
        session.add(tenant)
        await session.flush()
        print(f"  [+] Tenant creado: {tenant.name}")
    else:
        print(f"  [~] Tenant ya existe: {tenant.name}")
    return tenant


async def get_or_create_roles(session: AsyncSession) -> dict[str, Rol]:
    roles: dict[str, Rol] = {}
    for r in ROLES:
        result = await session.execute(
            select(Rol).where(Rol.nombre == r["nombre"], Rol.tenant_id == TENANT_ID)
        )
        rol = result.scalar_one_or_none()
        if rol is None:
            rol = Rol(tenant_id=TENANT_ID, nombre=r["nombre"], descripcion=r["descripcion"])
            session.add(rol)
            await session.flush()
            print(f"  [+] Rol creado: {rol.nombre}")
        else:
            print(f"  [~] Rol ya existe: {rol.nombre}")
        roles[rol.nombre] = rol
    return roles


async def get_or_create_permisos(session: AsyncSession) -> dict[str, Permiso]:
    permisos: dict[str, Permiso] = {}
    for p in PERMISOS:
        result = await session.execute(
            select(Permiso).where(Permiso.nombre == p["nombre"], Permiso.tenant_id == TENANT_ID)
        )
        permiso = result.scalar_one_or_none()
        if permiso is None:
            permiso = Permiso(tenant_id=TENANT_ID, nombre=p["nombre"], descripcion=p["descripcion"])
            session.add(permiso)
            await session.flush()
            print(f"  [+] Permiso creado: {permiso.nombre}")
        else:
            print(f"  [~] Permiso ya existe: {permiso.nombre}")
        permisos[permiso.nombre] = permiso
    return permisos


async def sync_rol_permisos(session: AsyncSession, roles: dict[str, Rol], permisos: dict[str, Permiso]) -> None:
    for rol_nombre, permisos_lista in MAPEO_ROL_PERMISO.items():
        rol = roles[rol_nombre]
        for p_nombre in permisos_lista:
            permiso = permisos[p_nombre]
            result = await session.execute(
                select(RolPermiso).where(
                    RolPermiso.rol_id == rol.id,
                    RolPermiso.permiso_id == permiso.id,
                    RolPermiso.tenant_id == TENANT_ID
                )
            )
            rp = result.scalar_one_or_none()
            if rp is None:
                rp = RolPermiso(tenant_id=TENANT_ID, rol_id=rol.id, permiso_id=permiso.id)
                session.add(rp)
                print(f"     → Rol {rol_nombre} vinculado con Permiso {p_nombre}")


async def get_or_create_usuario(
    session: AsyncSession, data: dict, tenant_id: uuid.UUID
) -> Usuario:
    email_hash = generate_email_hash(data["email"])
    result = await session.execute(
        select(Usuario).where(
            Usuario.tenant_id == tenant_id,
            Usuario.email_hash == email_hash,
        )
    )
    usuario = result.scalar_one_or_none()
    if usuario is None:
        usuario = Usuario(
            tenant_id=tenant_id,
            email=data["email"],
            hashed_password=hash_password(data["password"]),
            nombre=data["nombre"],
            apellidos=data["apellidos"],
            estado="Activo",
        )
        session.add(usuario)
        await session.flush()
        print(f"  [+] Usuario creado: {data['email']}")
    else:
        print(f"  [~] Usuario ya existe: {data['email']}")
    return usuario


async def assign_rol(
    session: AsyncSession, usuario: Usuario, rol: Rol, materia_id = None, cohorte_id = None, comisiones = None
) -> Asignacion:
    result = await session.execute(
        select(Asignacion).where(
            Asignacion.usuario_id == usuario.id,
            Asignacion.rol_id == rol.id,
            Asignacion.materia_id == materia_id,
            Asignacion.cohorte_id == cohorte_id
        )
    )
    asig = result.scalar_one_or_none()
    if asig is None:
        asig = Asignacion(
            tenant_id=usuario.tenant_id,
            usuario_id=usuario.id,
            rol_id=rol.id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            comisiones=comisiones,
            desde=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(asig)
        await session.flush()
        print(f"     → asignado rol {rol.nombre} (materia: {materia_id}, cohorte: {cohorte_id})")
    return asig

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def seed() -> None:
    print("\n=== Seed de desarrollo ===\n")
    async with SessionLocal() as session:
        async with session.begin():
            tenant = await get_or_create_tenant(session)
            roles = await get_or_create_roles(session)
            permisos = await get_or_create_permisos(session)
            await sync_rol_permisos(session, roles, permisos)

            # Estructura Académica Básica
            print("\n--- Estructura Académica ---")
            # 1. Carrera
            result_carrera = await session.execute(
                select(Carrera).where(Carrera.codigo == "TUPAD", Carrera.tenant_id == TENANT_ID)
            )
            carrera = result_carrera.scalar_one_or_none()
            if not carrera:
                carrera = Carrera(tenant_id=TENANT_ID, codigo="TUPAD", nombre="Tecnicatura Universitaria en Programación a Distancia")
                session.add(carrera)
                await session.flush()
                print(f"  [+] Carrera creada: {carrera.nombre}")
            else:
                print(f"  [~] Carrera ya existe: {carrera.nombre}")

            # 2. Cohortes
            cohortes_nombres = ["2026-1", "2026-2"]
            cohortes_dict: dict[str, Cohorte] = {}
            for cn in cohortes_nombres:
                result_cohorte = await session.execute(
                    select(Cohorte).where(Cohorte.nombre == cn, Cohorte.tenant_id == TENANT_ID)
                )
                coh = result_cohorte.scalar_one_or_none()
                if not coh:
                    coh = Cohorte(
                        tenant_id=TENANT_ID,
                        carrera_id=carrera.id,
                        nombre=cn,
                        anio=2026,
                        vig_desde=datetime.now(timezone.utc).date()
                    )
                    session.add(coh)
                    await session.flush()
                    print(f"  [+] Cohorte creada: {coh.nombre}")
                else:
                    print(f"  [~] Cohorte ya existe: {coh.nombre}")
                cohortes_dict[cn] = coh

            # 3. Materias
            materias_datos = [
                {"codigo": "PROG1", "nombre": "Programación I"},
                {"codigo": "PROG2", "nombre": "Programación II"},
                {"codigo": "BDD", "nombre": "Bases de Datos"},
            ]
            materias_dict: dict[str, Materia] = {}
            for md in materias_datos:
                result_materia = await session.execute(
                    select(Materia).where(Materia.codigo == md["codigo"], Materia.tenant_id == TENANT_ID)
                )
                mat = result_materia.scalar_one_or_none()
                if not mat:
                    mat = Materia(tenant_id=TENANT_ID, codigo=md["codigo"], nombre=md["nombre"])
                    session.add(mat)
                    await session.flush()
                    print(f"  [+] Materia creada: {mat.nombre}")
                else:
                    print(f"  [~] Materia ya existe: {mat.nombre}")
                materias_dict[md["codigo"]] = mat

            print("\n--- Usuarios y Asignaciones ---")
            usuarios_creados = {}
            for data in USUARIOS:
                usuario = await get_or_create_usuario(session, data, tenant.id)
                usuarios_creados[data["email"]] = usuario
                
                # Asignación global inicial
                await assign_rol(session, usuario, roles[data["rol"]])

            # Asignaciones académicas específicas para simular equipos / comisiones
            docente_user = usuarios_creados["docente@demo.com"]
            coord_user = usuarios_creados["coordinador@demo.com"]
            
            # Asignar Docente a PROG1 en 2026-1 con Comisión A
            await assign_rol(
                session, 
                docente_user, 
                roles["PROFESOR"], 
                materia_id=materias_dict["PROG1"].id, 
                cohorte_id=cohortes_dict["2026-1"].id,
                comisiones=["A"]
            )
            # Añadir estudiante extra para demo
            maria_user = await get_or_create_usuario(session, {
                "nombre": "María",
                "apellidos": "Gómez",
                "email": "maria.gomez@demo.com",
                "password": "maria1234",
                "rol": "ALUMNO",
            }, tenant.id)
            usuarios_creados["maria.gomez@demo.com"] = maria_user
            # Asignar Coordinador a PROG1 en 2026-1
            await assign_rol(
                session, 
                coord_user, 
                roles["COORDINADOR"], 
                materia_id=materias_dict["PROG1"].id, 
                cohorte_id=cohortes_dict["2026-1"].id
            )
            
            # --- Seed de Padrón y Calificaciones para el Alumno ---
            from app.models.padron import VersionPadron, EntradaPadron
            from app.models.calificacion import Calificacion
            
            alumno_user = usuarios_creados["alumno@demo.com"]
            
            # Crear Padrones para todas las materias
            for mat_codigo in ["PROG1", "PROG2", "BDD"]:
                vp = await session.execute(select(VersionPadron).where(
                    VersionPadron.materia_id == materias_dict[mat_codigo].id,
                    VersionPadron.cohorte_id == cohortes_dict["2026-1"].id,
                    VersionPadron.activa == True
                ))
                version_padron = vp.scalar_one_or_none()
                if not version_padron:
                    version_padron = VersionPadron(
                        tenant_id=TENANT_ID,
                        materia_id=materias_dict[mat_codigo].id,
                        cohorte_id=cohortes_dict["2026-1"].id,
                        activa=True
                    )
                    session.add(version_padron)
                    await session.flush()
                
                # Inscribir al alumno en esta materia
                ep = await session.execute(select(EntradaPadron).where(
                    EntradaPadron.version_id == version_padron.id,
                    EntradaPadron.usuario_id == alumno_user.id
                ))
                entrada_padron = ep.scalar_one_or_none()
                if not entrada_padron:
                    # Inscribir al alumno en esta materia (existente)
                    entrada_padron = EntradaPadron(
                        tenant_id=TENANT_ID,
                        version_id=version_padron.id,
                        usuario_id=alumno_user.id,
                        email=alumno_user.email,
                        nombre=alumno_user.nombre,
                        apellidos=alumno_user.apellidos,
                        comision="A"
                    )
                    session.add(entrada_padron)
                    await session.flush()
                    # Inscribir a Maria Gómez en la misma materia
                    entrada_padron_maria = EntradaPadron(
                        tenant_id=TENANT_ID,
                        version_id=version_padron.id,
                        usuario_id=maria_user.id,
                        email=maria_user.email,
                        nombre=maria_user.nombre,
                        apellidos=maria_user.apellidos,
                        comision="A"
                    )
                    session.add(entrada_padron_maria)
                    await session.flush()

                # Agregar calificaciones variadas según la materia
                if mat_codigo == "PROG1":
                    acts = [
                        ("TP 1", 8.0, True, True),
                        ("TP 2", 9.0, True, True),
                        ("Parcial 1", None, False, False), # Pendiente
                        ("Trabajo Final", None, False, False) # Pendiente
                    ]
                elif mat_codigo == "PROG2":
                    acts = [
                        ("TP 1", 4.0, False, True), # Desaprobado
                        ("Recuperatorio TP 1", 7.0, True, True),
                        ("Parcial 1", 10.0, True, True)
                    ]
                else: # BDD
                    acts = [
                        ("Modelo ER", None, False, False), # Pendiente
                        ("Parcial SQL", None, False, False) # Pendiente
                    ]

                for act_nombre, nota, aprobado, finalizado in acts:
                    calif_check = await session.execute(select(Calificacion).where(
                        Calificacion.entrada_padron_id == entrada_padron.id,
                        Calificacion.actividad == act_nombre
                    ))
                    if not calif_check.scalars().first():
                        c = Calificacion(
                            tenant_id=TENANT_ID,
                            entrada_padron_id=entrada_padron.id,
                            materia_id=materias_dict[mat_codigo].id,
                            docente_id=docente_user.id,
                            actividad=act_nombre,
                            nota_numerica=nota,
                            aprobado=aprobado,
                            finalizado=finalizado,
                            origen="Seed"
                        )
                        session.add(c)

            # --- Seed de Avisos institucionales ---
            print("\n--- Avisos ---")
            from datetime import timedelta
            avisos_demo = [
                {
                    "alcance": AlcanceEnum.GLOBAL,
                    "severidad": "info",
                    "titulo": "Bienvenidos al cuatrimestre 2026",
                    "cuerpo": "Les damos la bienvenida al ciclo lectivo 2026. Recordá revisar los cronogramas de cada materia.",
                    "inicio_en": datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1),
                    "fin_en": datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30),
                    "orden": 0,
                    "activo": True,
                    "requiere_ack": False,
                },
                {
                    "alcance": AlcanceEnum.GLOBAL,
                    "severidad": "warning",
                    "titulo": "Mantenimiento programado este sábado",
                    "cuerpo": "El sistema estará en mantenimiento el sábado de 02:00 a 06:00 hs. Guardá tu trabajo con anticipación.",
                    "inicio_en": datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=2),
                    "fin_en": datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7),
                    "orden": 1,
                    "activo": True,
                    "requiere_ack": True,
                },
            ]
            for av_data in avisos_demo:
                existing = await session.execute(
                    select(Aviso).where(
                        Aviso.titulo == av_data["titulo"],
                        Aviso.tenant_id == TENANT_ID
                    )
                )
                if not existing.scalar_one_or_none():
                    aviso = Aviso(tenant_id=TENANT_ID, **av_data)
                    session.add(aviso)
                    await session.flush()
                    print(f"  [+] Aviso creado: {av_data['titulo']}")
                else:
                    print(f"  [~] Aviso ya existe: {av_data['titulo']}")

    print("\n=== Seed completado ===")
    print("Cuentas disponibles:")
    print("  admin@demo.com       / admin1234")
    print("  coordinador@demo.com / coord1234")
    print("  docente@demo.com     / docente1234")
    print("  alumno@demo.com      / alumno1234")
    
    print("\nUUIDs útiles para probar la carga manual de Padrón:")
    print(f"  Materia PROG1:   {materias_dict['PROG1'].id}")
    print(f"  Cohorte 2026-1:  {cohortes_dict['2026-1'].id}")
    print()


if __name__ == "__main__":
    asyncio.run(seed())

#Materia (PROG1): b4f06063-457a-4f00-b50f-f0c4aa89b14e
#Cohorte (2026-1): 06dd4cc6-9a0e-4171-8a6c-6fb3686d81aa