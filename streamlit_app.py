import streamlit as st
import datetime
import json
import base64
import os

# Carga segura de Stripe
try:
    import stripe
except ImportError:
    stripe = None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SafeMachine CE | Legal Engineering & CE Marking Platform",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CLAVE SECRETA DE STRIPE DESDE SECRETS ---
stripe_key = st.secrets.get("STRIPE_SECRET_KEY", os.environ.get("STRIPE_SECRET_KEY", None))
if stripe_key and stripe:
    stripe.api_key = stripe_key

ADMIN_EMAILS = ["alberto.lantaron@gmail.com", "albertterre.lantaron@gmail.com"]

# --- ENLACES REALES DE PAGO DE STRIPE ---
URL_STRIPE_49 = "https://buy.stripe.com/fZu8wR69oh1k09t5ki0Ny02"
URL_STRIPE_149 = "https://buy.stripe.com/dRm14p55k3auf4nbIG0Ny03"

# --- IDIOMA ---
idioma = st.sidebar.radio("🌐 Language / Idioma:", ["🇪🇸 Español", "🇬🇧 English"], horizontal=True)
es_espanol = "Español" in idioma

# Textos según idioma
T_TITULO = "SAFEMACHINE CE"
T_SUB = "Plataforma de Expedientes Técnicos, Marcado CE y Evaluación de Riesgos (ISO 12100 & Reglamento UE 2023/1230)" if es_espanol else "Automated CE Marking Technical Files & Quantitative Risk Assessment Platform (ISO 12100 & EU 2023/1230)"
T_HEADER_BADGE = "SOFTWARE PROFESIONAL DE INGENIERÍA LEGAL" if es_espanol else "LEGAL ENGINEERING COMPLIANCE SOFTWARE"

# --- ESTILOS VISUALES INDUSTRIAL TECH ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: #f8fafc;
        color: #0f172a;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    input, textarea, select, 
    div[data-baseweb="input"] input, 
    div[data-baseweb="select"] {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border-radius: 14px;
        padding: 28px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.12);
    }
    .header-badge {
        display: inline-block;
        background: #0284c7;
        color: white;
        font-size: 11px;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 12px;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        color: #f8fafc;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 5px;
    }
    
    .card-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    .placa-metalica {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 50%, #94a3b8 100%);
        border: 3px solid #475569;
        border-radius: 8px;
        padding: 20px;
        color: #0f172a;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15), inset 0 0 10px rgba(255,255,255,0.6);
        max-width: 380px;
        margin: 15px auto;
        position: relative;
    }
    .placa-remache {
        width: 12px;
        height: 12px;
        background: radial-gradient(circle, #64748b 30%, #334155 100%);
        border-radius: 50%;
        position: absolute;
    }
    
    div.stButton > button[kind="primary"] {
        background: #0284c7 !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #0369a1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- MATRICES DE CÁLCULO NORMATIVO ---
VALORES_LO = {"Casi imposible (0.033)": 0.033, "Muy improbable (1)": 1, "Poco probable (2)": 2, "Posible (5)": 5, "Probable (8)": 8, "Cierto (15)": 15}
VALORES_FE = {"Anual (0.5)": 0.5, "Mensual (1)": 1, "Semanal (1.5)": 1.5, "Diaria (2.5)": 2.5, "Por turnos / Horaria (4)": 4, "Continua (5)": 5}
VALORES_DPH = {"Arañazo / Golpe leve (0.1)": 0.1, "Laceración / Fractura menor (0.5)": 0.5, "Amputación de dedo / Fractura grave (3)": 3, "Amputación de mano / Pérdida de ojo (7)": 7, "Muerte o incapacidad permanente (15)": 15}
VALORES_NP = {"1 o 2 personas (1)": 1, "3 a 7 personas (2)": 2, "8 a 15 personas (4)": 4, "Más de 15 personas (8)": 8}

def clasificar_hrn(hrn):
    if hrn <= 5:
        return ("Riesgo Aceptable / Insignificante" if es_espanol else "Acceptable / Negligible Risk"), "#10b981"
    elif hrn <= 50:
        return ("Riesgo Bajo (Medidas leves)" if es_espanol else "Low Risk (Minor controls)"), "#0284c7"
    elif hrn <= 150:
        return ("Riesgo Medio (Medidas obligatorias)" if es_espanol else "Medium Risk (Mandatory controls)"), "#f59e0b"
    elif hrn <= 500:
        return ("Riesgo Alto (Peligro crítico)" if es_espanol else "High Risk (Critical danger)"), "#ea580c"
    else:
        return ("Riesgo Inaceptable (Parada de máquina)" if es_espanol else "Unacceptable Risk (Immediate stop)"), "#dc2626"

def calcular_plr(severidad, frecuencia, posibilidad):
    if "S1" in severidad:
        if "F1" in frecuencia:
            return "PL a" if "P1" in posibilidad else "PL b"
        else:
            return "PL b" if "P1" in posibilidad else "PL c"
    else:
        if "F1" in frecuencia:
            return "PL c" if "P1" in posibilidad else "PL d"
        else:
            return "PL d" if "P1" in posibilidad else "PL e (Max. Safety)"

# --- GESTIÓN DE SESIÓN Y LICENCIAS ---
if "tipo_licencia" not in st.session_state:
    st.session_state.tipo_licencia = "ninguna"
if "cliente_email" not in st.session_state:
    st.session_state.cliente_email = ""

def comprobar_licencia_en_stripe(email_a_verificar):
    email_limpio = email_a_verificar.strip().lower()
    if email_limpio in [e.lower() for e in ADMIN_EMAILS]:
        return True, "ilimitada", "Licencia Propietario / Master"
    if not stripe or not stripe_key:
        return False, "ninguna", "Sistema de verificación no conectado a Stripe."

    try:
        clientes = stripe.Customer.list(email=email_limpio)
        if not clientes.data:
            return False, "ninguna", "Correo no encontrado en la base de datos de Stripe."

        customer_id = clientes.data[0].id
        subs = stripe.Subscription.list(customer=customer_id, status="active")
        if subs.data:
            return True, "ilimitada", "Suscripción Oficina Técnica Activa (149€/mes)"

        cargos = stripe.Charge.list(customer=customer_id, limit=5)
        for cargo in cargos.data:
            if cargo.paid and not cargo.refunded:
                return True, "individual", "Licencia Expediente Individual Activa (49€)"

        return False, "ninguna", "No constan pagos vigentes asociados a este correo."
    except Exception as err:
        return False, "ninguna", f"Error de verificación: {err}"

# Detección retorno Stripe
if st.query_params.get("pago_exitoso") == "true":
    st.session_state.tipo_licencia = "individual"
    st.session_state.cliente_email = st.query_params.get("email", "Licencia Empresa Verificada")
    st.balloons()
    st.toast("🎉 ¡Pago verificado con éxito! Expediente oficial desbloqueado.", icon="💎")

# Riesgos iniciales
if "peligros_evaluados" not in st.session_state:
    st.session_state.peligros_evaluados = [
        {
            "zona": "Zona de Transmisión de Potencia" if es_espanol else "Power Transmission Area",
            "peligro": "Atrapamiento en engranajes y cadenas" if es_espanol else "Entanglement in gears and chain drive",
            "norma": "UNE-EN ISO 14120 / UNE-EN ISO 13857",
            "hrn_inicial": 160.0,
            "estado_inicial": "Riesgo Alto" if es_espanol else "High Risk",
            "color_inicial": "#ea580c",
            "plr": "PL d",
            "medida": "Resguardo fijo envolvente atornillado que precisa herramienta para su apertura + microrruptor enclavado." if es_espanol else "Fixed interlocked guarding requiring tools for removal + safety interlock switch.",
            "hrn_residual": 3.2,
            "estado_residual": "Riesgo Aceptable" if es_espanol else "Acceptable Risk",
            "color_residual": "#10b981"
        },
        {
            "zona": "Zona Operativa de Prensado / Corte" if es_espanol else "Pressing & Shearing Tool Area",
            "peligro": "Aplastamiento y cizallamiento por plato móvil" if es_espanol else "Crushing and shearing by hydraulic ram",
            "norma": "UNE-EN ISO 13855 / UNE-EN ISO 13851",
            "hrn_inicial": 240.0,
            "estado_inicial": "Riesgo Alto" if es_espanol else "High Risk",
            "color_inicial": "#ea580c",
            "plr": "PL e",
            "medida": "Barrera inmaterial fotoeléctrica Tipo 4 (distancia de seguridad 450 mm) con parada de emergencia Categoría 4." if es_espanol else "Type 4 safety optical light curtain (450 mm safety distance) with Category 4 emergency stop.",
            "hrn_residual": 4.8,
            "estado_residual": "Riesgo Aceptable" if es_espanol else "Acceptable Risk",
            "color_residual": "#10b981"
        }
    ]

# --- MAQUETADOR DE EXPEDIENTE TÉCNICO OFICIAL CON BLUR ANTI-COPIA ---
def generar_html_expediente(datos, lista_riesgos, tipo_licencia, en_ingles=False):
    fecha_hoy = datetime.date.today().strftime("%d of %B %Y" if en_ingles else "%d de %B de %Y")
    es_valido = tipo_licencia in ["individual", "ilimitada"]
    
    filas_tabla = ""
    for idx, r in enumerate(lista_riesgos):
        # Si no es de pago, difuminamos a partir del segundo riesgo para evitar capturas
        blur_style = "" if (es_valido or idx == 0) else "filter: blur(5px); user-select: none; opacity: 0.6;"
        filas_tabla += f"""
        <tr style="{blur_style}">
            <td style="padding:8px; border:1px solid #cbd5e1;"><strong>{r['zona']}</strong><br><span style="color:#64748b;">{r['peligro']}</span></td>
            <td style="padding:8px; border:1px solid #cbd5e1; font-size:8.5pt;">{r['norma']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; color:{r['color_inicial']}; font-weight:bold;">HRN: {r['hrn_inicial']:.1f}<br><span style="font-size:7.5pt;">{r['estado_inicial']}</span></td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; font-weight:bold; color:#0284c7;">{r['plr']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; font-size:8.5pt;">{r['medida']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; color:{r['color_residual']}; font-weight:bold;">HRN: {r['hrn_residual']:.1f}<br><span style="font-size:7.5pt;">{r['estado_residual']}</span></td>
        </tr>
        """
        
    bloque_bloqueo = "" if es_valido else f"""
    <div style="background: #fff1f2; border: 2px dashed #e11d48; padding: 20px; text-align: center; border-radius: 8px; margin: 25px 0;">
        <span style="font-size: 24pt;">🔒</span>
        <h3 style="color: #9f1239; margin: 8px 0;">{'SECCIONES LEGALES BLOQUEADAS (MODO EVALUACIÓN)' if not en_ingles else 'LEGAL SECTIONS LOCKED (EVALUATION MODE)'}</h3>
        <p style="color: #4c0519; font-size: 10pt; max-width: 600px; margin: 0 auto;">
            {'Para descargar el Expediente de Construcción completo, desbloquear todas las matrices sin desenfoque y obtener la Declaración Oficial visable, adquiere tu licencia (49 € o 149 €/mes).' if not en_ingles else 'To download the full Technical File, unblur all risk assessments, and obtain the officially signable Declaration, purchase a license.'}
        </p>
    </div>
    """

    blur_declaracion = "" if es_valido else "filter: blur(6px); user-select: none; pointer-events: none;"

    t_doc = "TECHNICAL CONSTRUCTION FILE" if en_ingles else "EXPEDIENTE TÉCNICO DE CONSTRUCCIÓN"
    t_reg = "Pursuant to European Machinery Regulation (EU) 2023/1230" if en_ingles else "Conforme al Reglamento Europeo de Máquinas (UE) 2023/1230"
    t_sec1 = "1. TECHNICAL SPECIFICATIONS (EN 60204-1)" if en_ingles else "1. ESPECIFICACIONES TÉCNICAS (UNE-EN 60204-1)"
    t_sec2 = "2. RISK ASSESSMENT & REDUCTION (EN ISO 12100 & ISO 13849-1)" if en_ingles else "2. EVALUACIÓN Y REDUCCIÓN DE RIESGOS (UNE-EN ISO 12100 & ISO 13849-1)"
    t_sec3 = "3. MANDATORY CE MARKING NAMEPLATE (Art. 16)" if en_ingles else "3. PLACA DE CARACTERÍSTICAS TÉCNICAS OBLIGATORIA (Art. 16)"
    t_sec4 = "4. EU DECLARATION OF CONFORMITY" if en_ingles else "4. DECLARACIÓN UE DE CONFORMIDAD (DOCUMENTO OFICIAL)"

    html = f"""
    <!DOCTYPE html>
    <html lang="{'en' if en_ingles else 'es'}">
    <head>
        <meta charset="UTF-8">
        <title>{t_doc} - {datos['modelo']}</title>
        <style>
            @media print {{
                .no-print {{ display: none !important; }}
                body {{ font-size: 9.5pt; color: #111827; }}
                .page-break {{ page-break-after: always; }}
                @page {{ margin: 15mm; size: A4 portrait; }}
            }}
            body {{
                font-family: Arial, Helvetica, sans-serif;
                max-width: 900px;
                margin: 20px auto;
                padding: 25px;
                color: #1e293b;
                line-height: 1.45;
                position: relative;
            }}
            .ce-mark {{
                font-size: 50pt;
                font-weight: 900;
                letter-spacing: -4px;
                text-align: center;
                margin: 10px 0;
            }}
            h1 {{ font-size: 18pt; text-align: center; margin: 5px 0; color: #0f172a; }}
            h2 {{ font-size: 12pt; border-bottom: 2px solid #0284c7; padding-bottom: 4px; margin-top: 25px; color: #0f172a; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 8.5pt; }}
            th {{ background: #f1f5f9; padding: 8px; border: 1px solid #cbd5e1; text-align: left; }}
            .btn-print {{
                background: #0284c7; color: white; padding: 12px 26px; font-weight: bold;
                border: none; border-radius: 6px; cursor: pointer; font-size: 14px;
            }}
            .placa-box {{
                border: 2px solid #000; padding: 15px; width: 320px; margin: 20px auto;
                text-align: center; background: #fafafa;
            }}
        </style>
    </head>
    <body>
        <div class="no-print" style="text-align:center; margin-bottom:30px; background:#f8fafc; padding:15px; border-radius:8px; border:1px solid #cbd5e1;">
            <button class="btn-print" onclick="window.print()">🖨️ {'Print / Save as Official PDF' if en_ingles else 'Guardar Expediente como PDF Oficial'}</button>
            <p style="font-size:12px; color:#64748b; margin-top:6px;">{'Select Destination: Save as PDF in print options.' if en_ingles else 'En la ventana de impresión selecciona: Guardar como PDF.'}</p>
        </div>

        <div style="border: 1px solid #000; padding: 25px; text-align: center; margin-bottom: 30px;">
            <div class="ce-mark">CE</div>
            <h1>{t_doc}</h1>
            <p style="font-size:11pt; margin:5px 0;"><strong>{t_reg}</strong></p>
            <hr style="margin:20px 0;">
            <p style="font-size:11pt;"><strong>{'MACHINERY' if en_ingles else 'MÁQUINA'}:</strong> {datos['denominacion']}</p>
            <p style="font-size:10pt;"><strong>{'MODEL' if en_ingles else 'MODELO'}:</strong> {datos['modelo']} | <strong>S/N:</strong> {datos['serie']}</p>
            <p style="font-size:10pt;"><strong>{'MANUFACTURER' if en_ingles else 'FABRICANTE'}:</strong> {datos['fabricante']}</p>
        </div>

        <h2>{t_sec1}</h2>
        <table>
            <tr><th width="30%">{'Manufacturer' if en_ingles else 'Fabricante'}:</th><td width="70%">{datos['fabricante']} ({datos['cif']})</td></tr>
            <tr><th>{'Address' if en_ingles else 'Ubicación / Instalación'}:</th><td>{datos['direccion']}</td></tr>
            <tr><th>{'Chartered Engineer' if en_ingles else 'Ingeniero Responsable Técnico'}:</th><td>{datos['ingeniero']} (ID: {datos['colegiado']})</td></tr>
            <tr><th>{'Installed Power' if en_ingles else 'Potencia Eléctrica Instalada'}:</th><td>{datos['potencia']} kW</td></tr>
            <tr><th>{'Voltage & Frequency' if en_ingles else 'Tensión y Frecuencia'}:</th><td>{datos['tension']} V | {datos['frecuencia']} Hz ({datos['fases']})</td></tr>
            <tr><th>{'Pneumatic Pressure' if en_ingles else 'Presión Neumática'}:</th><td>{datos['presion']} bar</td></tr>
            <tr><th>{'Year of Manufacture' if en_ingles else 'Año de Construcción'}:</th><td>{datos['anio']}</td></tr>
        </table>

        <h2>{t_sec2}</h2>
        <table>
            <thead>
                <tr>
                    <th width="20%">{'Hazard Area' if en_ingles else 'Zona y Peligro'}</th>
                    <th width="15%">{'Standard' if en_ingles else 'Norma Aplicada'}</th>
                    <th width="12%">{'Initial HRN' if en_ingles else 'Riesgo Inicial'}</th>
                    <th width="8%">PLr</th>
                    <th width="30%">{'Safety Control Applied' if en_ingles else 'Medida de Ingeniería'}</th>
                    <th width="15%">{'Residual HRN' if en_ingles else 'Riesgo Residual'}</th>
                </tr>
            </thead>
            <tbody>
                {filas_tabla}
            </tbody>
        </table>

        {bloque_bloqueo}

        <div class="page-break"></div>

        <h2>{t_sec3}</h2>
        <div class="placa-box">
            <div style="font-size:24pt; font-weight:bold; letter-spacing:-2px;">CE</div>
            <p style="margin:2px 0; font-size:10pt; font-weight:bold;">{datos['fabricante']}</p>
            <p style="margin:2px 0; font-size:8pt;">{datos['direccion']}</p>
            <hr style="margin:6px 0;">
            <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>TYPE / MOD:</strong> {datos['modelo']}</p>
            <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>S/N:</strong> {datos['serie']} &nbsp;|&nbsp; <strong>YEAR:</strong> {datos['anio']}</p>
            <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>POWER:</strong> {datos['potencia']} kW &nbsp;|&nbsp; <strong>VOLTAGE:</strong> {datos['tension']} V</p>
        </div>

        <h2 style="margin-top:35px;">{t_sec4}</h2>
        <div style="{blur_declaracion}">
            <p style="font-size:9pt; text-align:justify;">
                {'The undersigned declares on behalf of the manufacturer that the described machinery fulfills all relevant health and safety requirements of Regulation (EU) 2023/1230 on machinery, as well as Directives 2014/30/EU (EMC) and 2014/35/EU (LVD).' if en_ingles else 'El abajo firmante, en representación del fabricante, declara bajo su exclusiva responsabilidad que la máquina descrita cumple con todos los Requisitos Esenciales de Seguridad y Salud establecidos en el Reglamento (UE) 2023/1230 de máquinas, así como con la Directiva 2014/30/UE (CEM) y 2014/35/UE (Baja Tensión).'}
            </p>
            <p style="font-size:9pt;"><strong>{'Authorized Person to compile Technical File' if en_ingles else 'Persona facultada para compilar el expediente técnico'}:</strong> {datos['ingeniero']} (Col. Nº: {datos['colegiado']}).</p>
            
            <div style="margin-top:50px; display:flex; justify-content:space-between;">
                <div style="width:45%; border-top:1px solid #000; padding-top:8px; text-align:center; font-size:9pt;">
                    <strong>{'Manufacturer Legal Representative' if en_ingles else 'Firma Representante Legal'}</strong><br>
                    <span style="color:#64748b; font-size:8pt;">{datos['fabricante']}</span>
                </div>
                <div style="width:45%; border-top:1px solid #000; padding-top:8px; text-align:center; font-size:9pt;">
                    <strong>{'Chartered Industrial Engineer' if en_ingles else 'Firma Ingeniero Industrial'}</strong><br>
                    <span style="color:#64748b; font-size:8pt;">{datos['ingeniero']} (ID: {datos['colegiado']})</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- CABECERA PRINCIPAL ---
st.markdown(
    f"""
    <div class="header-box">
        <span class="header-badge">{T_HEADER_BADGE}</span>
        <h1 class="header-title">{T_TITULO}</h1>
        <p class="header-subtitle">{T_SUB}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR: ESTADO Y CONTROL DE LICENCIAS ---
st.sidebar.header("💳 Licencia Profesional" if es_espanol else "💳 Commercial License")

if st.session_state.tipo_licencia == "ilimitada":
    st.sidebar.markdown(
        f"""
        <div style="background:#f0fdf4; border:1px solid #86efac; padding:12px; border-radius:8px; color:#166534; font-weight:bold;">
            🟢 {'PLAN OFICINA TÉCNICA (149€/mes)' if es_espanol else 'ENGINEERING OFFICE PLAN (149€/mo)'}<br>
            <span style="font-size:11px; font-weight:normal;">{st.session_state.cliente_email}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
elif st.session_state.tipo_licencia == "individual":
    st.sidebar.markdown(
        f"""
        <div style="background:#eff6ff; border:1px solid #93c5fd; padding:12px; border-radius:8px; color:#1e40af; font-weight:bold;">
            🔵 {'PLAN EXPEDIENTE INDIVIDUAL (49€)' if es_espanol else 'SINGLE MACHINE LICENSE (49€)'}<br>
            <span style="font-size:11px; font-weight:normal;">{'1 Expediente Desbloqueado' if es_espanol else '1 Dossier Unlocked'}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        f"""
        <div style="background:#fffbeb; border:1px solid #fde68a; padding:10px; border-radius:8px; font-size:12px; color:#92400e;">
            ⚠️ <strong>{'MODO EVALUACIÓN' if es_espanol else 'EVALUATION MODE'}</strong><br>
            {'Previsualización con secciones desenfocadas. Desbloquea tu expediente oficial:' if es_espanol else 'Preview with blurred sections. Unlock your signable file:'}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown(f'<a href="{URL_STRIPE_49}" target="_blank" style="background:#0284c7; color:white; display:block; text-align:center; padding:9px; border-radius:6px; font-weight:bold; font-size:12px; text-decoration:none; margin-bottom:6px;">📄 {"Expediente Único (49 €)" if es_espanol else "Single Dossier (49 €)"}</a>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<a href="{URL_STRIPE_149}" target="_blank" style="background:#0f172a; color:white; display:block; text-align:center; padding:9px; border-radius:6px; font-weight:bold; font-size:12px; text-decoration:none;">🏢 {"Oficina Técnica Ilimitada (149 €/mes)" if es_espanol else "Unlimited Plan (149 €/mo)"}</a>', unsafe_allow_html=True)

if st.session_state.tipo_licencia != "ninguna":
    if st.sidebar.button("Cerrar Sesión" if es_espanol else "Logout"):
        st.session_state.tipo_licencia = "ninguna"
        st.session_state.cliente_email = ""
        st.rerun()
else:
    with st.sidebar.form("form_recuperar"):
        st.write("**¿Ya compraste una licencia?**" if es_espanol else "**Already purchased a license?**")
        correo_licencia = st.text_input("Email Stripe:")
        if st.form_submit_button("🔑 Validar" if es_espanol else "🔑 Validate"):
            if "@" in correo_licencia:
                valido, tipo, mensaje = comprobar_licencia_en_stripe(correo_licencia)
                if valido:
                    st.session_state.tipo_licencia = tipo
                    st.session_state.cliente_email = correo_licencia.strip().lower()
                    st.success("¡Licencia validada!" if es_espanol else "License verified!")
                    st.rerun()
                else:
                    st.error(mensaje)

st.sidebar.divider()
st.sidebar.header("💾 Guardar / Cargar" if es_espanol else "💾 Save / Load")
if st.session_state.tipo_licencia in ["ilimitada"]:
    proyecto_json = json.dumps(st.session_state.peligros_evaluados, indent=2)
    st.sidebar.download_button(
        label="💾 Exportar Máquina (.json)" if es_espanol else "💾 Export Machine (.json)",
        data=proyecto_json,
        file_name="Proyecto_Maquina_CE.json",
        mime="application/json"
    )
    archivo_cargado = st.sidebar.file_uploader("📂 Importar (.json):" if es_espanol else "📂 Import (.json):", type=["json"])
    if archivo_cargado:
        try:
            datos_cargados = json.load(archivo_cargado)
            if isinstance(datos_cargados, list):
                st.session_state.peligros_evaluados = datos_cargados
                st.sidebar.success("Cargado con éxito" if es_espanol else "Loaded successfully")
        except Exception:
            st.sidebar.error("Archivo no válido")
else:
    st.sidebar.info("🔒 Guardado en JSON exclusivo del **Plan Oficina Técnica (149€/mes)**." if es_espanol else "🔒 JSON backup requires **Unlimited Plan (149€/mo)**.")

# --- TABS DE TRABAJO ---
titulos_tabs = [
    "🏭 1. Ficha Técnica" if es_espanol else "🏭 1. Machine Data",
    "⚠️ 2. Matriz HRN (ISO 12100)" if es_espanol else "⚠️ 2. HRN Risk Matrix",
    "🛡️ 3. Nivel PLr (ISO 13849)" if es_espanol else "🛡️ 3. Safety Level (PLr)",
    "🏷️ 4. Placa CE Metálica" if es_espanol else "🏷️ 4. Metallic CE Plate",
    "📄 5. Expediente y Descarga" if es_espanol else "📄 5. Dossier & Download"
]
tab_maquina, tab_hrn, tab_plr, tab_placa, tab_expediente = st.tabs(titulos_tabs)

# --- PESTAÑA 1: DATOS GENERALES ---
with tab_maquina:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Identificación de la Máquina" if es_espanol else "Machine Identification")
    
    col1, col2 = st.columns(2)
    with col1:
        denominacion = st.text_input("Denominación oficial:" if es_espanol else "Official Machinery Name:", value="Línea de Envasado y Paletizado Robotizado")
        fabricante = st.text_input("Razón Social Fabricante:" if es_espanol else "Manufacturer Legal Name:", value="Mecanizados y Robótica del Norte S.L.")
        cif = st.text_input("NIF / CIF / VAT ID:", value="B-95847291")
        direccion = st.text_input("Dirección de fabricación:" if es_espanol else "Manufacturing Address:", value="Polígono Industrial Erletxes, Manzana 4, 48960 Galdakao")
    with col2:
        modelo = st.text_input("Modelo / Código:" if es_espanol else "Model / Ref Code:", value="ROBOPACK-2025")
        serie = st.text_input("Número de Serie:" if es_espanol else "Serial Number:", value="SN-2025-0842")
        anio = st.number_input("Año de Fabricación:" if es_espanol else "Year of Manufacture:", min_value=2020, max_value=2030, value=2025)
        ingeniero = st.text_input("Ingeniero Responsable:" if es_espanol else "Chartered Technical Engineer:", value="Alberto Lantarón")
        colegiado = st.text_input("Nº Colegiado / DNI:" if es_espanol else "Professional ID / License:", value="COIIB-48192")

    st.divider()
    st.subheader("Especificaciones Energéticas (EN 60204-1)" if es_espanol else "Energy Specifications (EN 60204-1)")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        potencia = st.number_input("Potencia (kW):" if es_espanol else "Power (kW):", value=12.5, step=0.5)
    with col_e2:
        tension = st.selectbox("Tensión / Voltage (V):", [400, 230, 48, 24])
    with col_e3:
        fases = st.selectbox("Red / Phase:", ["Trifásica (3P+N+T)", "Monofásica (1P+N+T)"] if es_espanol else ["Three-phase (3P+N+E)", "Single-phase (1P+N+E)"])
    with col_e4:
        presion = st.number_input("Presión (bar):" if es_espanol else "Pressure (bar):", value=6.0, step=0.5)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 2: MÉTODO CUANTITATIVO HRN ---
with tab_hrn:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Evaluación Cuantitativa de Riesgo HRN (ISO 12100)" if es_espanol else "Quantitative HRN Risk Assessment (ISO 12100)")
    st.write("Fórmula normalizada: $\\text{HRN} = LO \\times FE \\times DPH \\times NP$. Permite justificar matemáticamente la reducción del riesgo a nivel Aceptable.")
    
    with st.form("form_nuevo_riesgo"):
        st.markdown("#### Añadir Peligro" if es_espanol else "#### Add Hazard")
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            zona_input = st.text_input("Zona / Componente:" if es_espanol else "Machine Area / Part:", placeholder="Zona de corte / Cabezal motor")
            peligro_input = st.text_input("Peligro específico:" if es_espanol else "Hazard description:", placeholder="Cizallamiento / Atrapamiento")
            norma_input = st.text_input("Norma armonizada:" if es_espanol else "Harmonized Standard:", value="UNE-EN ISO 14120 / UNE-EN ISO 13857")
        with c_r2:
            medida_input = st.text_area("Medida de ingeniería adoptada:" if es_espanol else "Engineering safety measure applied:", placeholder="Resguardo fijo perimetral con enclavamiento.")

        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            lo = st.selectbox("Probabilidad / Likelihood (LO):", list(VALORES_LO.keys()), index=4)
        with c_p2:
            fe = st.selectbox("Frecuencia / Frequency (FE):", list(VALORES_FE.keys()), index=4)
        with c_p3:
            dph = st.selectbox("Daño potencial / Harm (DPH):", list(VALORES_DPH.keys()), index=3)
        with c_p4:
            np = st.selectbox("Personas / Persons (NP):", list(VALORES_NP.keys()), index=0)

        hrn_calc_inicial = VALORES_LO[lo] * VALORES_FE[fe] * VALORES_DPH[dph] * VALORES_NP[np]
        estado_calc_inicial, color_calc_inicial = clasificar_hrn(hrn_calc_inicial)

        st.markdown(f"**{'Riesgo Inicial' if es_espanol else 'Initial Risk'}:** <span style='color:{color_calc_inicial}; font-weight:bold; font-size:16px;'>HRN: {hrn_calc_inicial:.1f} ({estado_calc_inicial})</span>", unsafe_allow_html=True)
        
        btn_guardar_riesgo = st.form_submit_button("➕ Registrar en Matriz" if es_espanol else "➕ Register in Matrix")
        if btn_guardar_riesgo:
            if zona_input and peligro_input:
                hrn_residual = round(hrn_calc_inicial * 0.02, 1)
                estado_res, color_res = clasificar_hrn(hrn_residual)
                
                st.session_state.peligros_evaluados.append({
                    "zona": zona_input,
                    "peligro": peligro_input,
                    "norma": norma_input,
                    "hrn_inicial": hrn_calc_inicial,
                    "estado_inicial": estado_calc_inicial,
                    "color_inicial": color_calc_inicial,
                    "plr": "PL d",
                    "medida": medida_input,
                    "hrn_residual": hrn_residual,
                    "estado_residual": estado_res,
                    "color_residual": color_res
                })
                st.success("Guardado en el expediente.")
                st.rerun()

    st.markdown("#### Matriz de Riesgos Registrados" if es_espanol else "#### Active Risk Register")
    for idx, r in enumerate(st.session_state.peligros_evaluados):
        with st.expander(f"📍 {r['zona']} — {r['peligro']}"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**Inicial:** <span style='color:{r['color_inicial']}; font-weight:bold;'>HRN {r['hrn_inicial']} ({r['estado_inicial']})</span>", unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"**Residual:** <span style='color:{r['color_residual']}; font-weight:bold;'>HRN {r['hrn_residual']} ({r['estado_residual']})</span>", unsafe_allow_html=True)
            if st.button("🗑️ Eliminar" if es_espanol else "🗑️ Delete", key=f"del_{idx}"):
                st.session_state.peligros_evaluados.pop(idx)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 3: DETERMINACIÓN DEL PLr (ISO 13849-1) ---
with tab_plr:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Nivel de Rendimiento Requerido (PLr - ISO 13849-1)" if es_espanol else "Required Performance Level (PLr - ISO 13849-1)")
    
    col_pl1, col_pl2 = st.columns([2, 1])
    with col_pl1:
        sev = st.radio("Severidad de la lesión (S):" if es_espanol else "Severity of injury (S):", ["S1 (Lesión leve reversible)" if es_espanol else "S1 (Slight reversible injury)", "S2 (Lesión grave irreversible o muerte)" if es_espanol else "S2 (Serious irreversible injury or death)"])
        frec = st.radio("Frecuencia de exposición (F):" if es_espanol else "Frequency of exposure (F):", ["F1 (Poco frecuente / Exposición corta)" if es_espanol else "F1 (Rare to short exposure)", "F2 (Frecuente a continua)" if es_espanol else "F2 (Frequent to continuous exposure)"])
        pos = st.radio("Posibilidad de evitar el peligro (P):" if es_espanol else "Possibility of avoiding hazard (P):", ["P1 (Posible en determinadas condiciones)" if es_espanol else "P1 (Possible under specific conditions)", "P2 (Casi imposible de evitar)" if es_espanol else "P2 (Scarcely possible)"])
        
    with col_pl2:
        plr_resultado = calcular_plr(sev, frec, pos)
        st.markdown("#### Nivel Exigido:" if es_espanol else "#### Required Level:")
        st.markdown(f'<div style="background:#e0f2fe; color:#0369a1; border:2px solid #0284c7; padding:10px; border-radius:8px; font-size:22px; font-weight:bold; text-align:center;">{plr_resultado}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 4: PLACA CE METÁLICA (SIMULADOR) ---
with tab_placa:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Simulador de Placa CE Físico (Art. 16 y Anexo III)" if es_espanol else "Metallic Nameplate Simulator (Art. 16 & Annex III)")
    st.write("Vista previa de la placa indeleble que debe remacharse al chasis de la máquina:")
    
    st.markdown(
        f"""
        <div class="placa-metalica">
            <div class="placa-remache" style="top:8px; left:8px;"></div>
            <div class="placa-remache" style="top:8px; right:8px;"></div>
            <div class="placa-remache" style="bottom:8px; left:8px;"></div>
            <div class="placa-remache" style="bottom:8px; right:8px;"></div>
            <div style="font-size:32pt; font-weight:900; letter-spacing:-3px; text-align:center; margin-bottom:5px;">CE</div>
            <p style="margin:0; font-weight:bold; font-size:12pt; text-align:center;">{fabricante}</p>
            <p style="margin:0; font-size:8.5pt; text-align:center; color:#334155;">{direccion}</p>
            <hr style="border:1px solid #475569; margin:10px 0;">
            <p style="margin:2px 0; font-size:9pt;"><strong>{'MACHINE' if not es_espanol else 'MÁQUINA'}:</strong> {denominacion}</p>
            <p style="margin:2px 0; font-size:9pt;"><strong>{'MODEL' if not es_espanol else 'MODELO'}:</strong> {modelo}</p>
            <p style="margin:2px 0; font-size:9pt;"><strong>S/N:</strong> {serie} &nbsp;|&nbsp; <strong>{'YEAR' if not es_espanol else 'AÑO'}:</strong> {anio}</p>
            <p style="margin:2px 0; font-size:9pt;"><strong>{'POWER' if not es_espanol else 'POTENCIA'}:</strong> {potencia} kW &nbsp;|&nbsp; <strong>{'VOLTAGE' if not es_espanol else 'TENSIÓN'}:</strong> {tension} V</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 5: EXPEDIENTE OFICIAL Y DESCARGA ---
with tab_expediente:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Expediente Técnico Completo y Marcado CE" if es_espanol else "Technical Construction File & CE Marking")
    
    datos_completos = {
        "denominacion": denominacion,
        "fabricante": fabricante,
        "cif": cif,
        "direccion": direccion,
        "modelo": modelo,
        "serie": serie,
        "anio": anio,
        "ingeniero": ingeniero,
        "colegiado": colegiado,
        "potencia": potencia,
        "tension": tension,
        "fases": fases,
        "frecuencia": 50,
        "presion": presion
    }

    html_dossier = generar_html_expediente(datos_completos, st.session_state.peligros_evaluados, st.session_state.tipo_licencia, en_ingles=(not es_espanol))
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.markdown("#### 1. Descarga del Documento Legal" if es_espanol else "#### 1. Official Document Download")
        if st.session_state.tipo_licencia in ["individual", "ilimitada"]:
            st.download_button(
                label="📥 Descargar Expediente Oficial (PDF)" if es_espanol else "📥 Download Official File (PDF)",
                data=html_dossier,
                file_name=f"Expediente_CE_{modelo}.html",
                mime="text/html",
                type="primary"
            )
            st.caption("Abre el archivo descargado en tu navegador y pulsa 'Guardar como PDF' para obtener el documento oficial limpio sin marcas de agua.")
        else:
            st.warning("🔒 Expediente oficial visable protegido tras licencia." if es_espanol else "🔒 Full official file protected behind license.")
            st.markdown(f'<a href="{URL_STRIPE_49}" target="_blank" style="background:#0284c7; color:white; padding:12px 20px; border-radius:6px; font-weight:bold; text-decoration:none; display:inline-block; margin-bottom:8px;">Desbloquear Expediente Único (49 €)</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="{URL_STRIPE_149}" target="_blank" style="background:#0f172a; color:white; padding:12px 20px; border-radius:6px; font-weight:bold; text-decoration:none; display:inline-block;">Contratar Plan Oficina Técnica (149 €/mes)</a>', unsafe_allow_html=True)
            
    with col_d2:
        st.markdown("#### 2. Estado de Certificación Técnica" if es_espanol else "#### 2. Technical Compliance Status")
        st.metric("Total Peligros Evaluados", len(st.session_state.peligros_evaluados))
        st.metric("Reglamento (UE) 2023/1230", "100% CONFORME", delta="Apto para marcado CE")
        
    st.divider()
    st.markdown("#### Previsualización Oficial (Anti-Copia Activo):" if es_espanol else "#### Official Preview (Anti-Copy Active):")
    st.components.v1.html(html_dossier, height=650, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)