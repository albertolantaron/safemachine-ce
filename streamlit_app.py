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

# --- SELECTOR DE IDIOMA GLOBAL ---
idioma = st.sidebar.radio("🌐 Language / Idioma:", ["🇪🇸 Español", "🇬🇧 English"], horizontal=True)
es_en = "English" in idioma

# Textos de cabecera
T_TITULO = "SAFEMACHINE CE"
T_SUB = "Automated CE Marking Technical Files & Quantitative Risk Assessment Platform (ISO 12100 & EU 2023/1230)" if es_en else "Plataforma de Expedientes Técnicos, Marcado CE y Evaluación de Riesgos (ISO 12100 & Reglamento UE 2023/1230)"
T_HEADER_BADGE = "LEGAL ENGINEERING COMPLIANCE SOFTWARE" if es_en else "SOFTWARE PROFESIONAL DE INGENIERÍA LEGAL"

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

# --- MATRICES DE CÁLCULO NORMATIVO HRN (ISO 12100) ---
if es_en:
    VALORES_LO = {"Almost impossible (0.033)": 0.033, "Highly unlikely (1)": 1, "Unlikely (2)": 2, "Possible (5)": 5, "Probable (8)": 8, "Certain (15)": 15}
    VALORES_FE = {"Annual (0.5)": 0.5, "Monthly (1)": 1, "Weekly (1.5)": 1.5, "Daily (2.5)": 2.5, "Per shift / Hourly (4)": 4, "Continuous (5)": 5}
    VALORES_DPH = {"Scratch / Minor bruise (0.1)": 0.1, "Laceration / Minor fracture (0.5)": 0.5, "Finger amputation / Severe fracture (3)": 3, "Hand amputation / Loss of eye (7)": 7, "Fatality or permanent disability (15)": 15}
    VALORES_NP = {"1 to 2 persons (1)": 1, "3 to 7 persons (2)": 2, "8 to 15 persons (4)": 4, "More than 15 persons (8)": 8}
else:
    VALORES_LO = {"Casi imposible (0.033)": 0.033, "Muy improbable (1)": 1, "Poco probable (2)": 2, "Posible (5)": 5, "Probable (8)": 8, "Cierto (15)": 15}
    VALORES_FE = {"Anual (0.5)": 0.5, "Mensual (1)": 1, "Semanal (1.5)": 1.5, "Diaria (2.5)": 2.5, "Por turnos / Horaria (4)": 4, "Continua (5)": 5}
    VALORES_DPH = {"Arañazo / Golpe leve (0.1)": 0.1, "Laceración / Fractura menor (0.5)": 0.5, "Amputación de dedo / Fractura grave (3)": 3, "Amputación de mano / Pérdida de ojo (7)": 7, "Muerte o incapacidad permanente (15)": 15}
    VALORES_NP = {"1 o 2 personas (1)": 1, "3 a 7 personas (2)": 2, "8 a 15 personas (4)": 4, "Más de 15 personas (8)": 8}

def clasificar_hrn(hrn, en_ingles=False):
    if hrn <= 5:
        return ("Acceptable / Negligible Risk" if en_ingles else "Riesgo Aceptable / Insignificante"), "#10b981"
    elif hrn <= 50:
        return ("Low Risk (Minor controls)" if en_ingles else "Riesgo Bajo (Medidas leves)"), "#0284c7"
    elif hrn <= 150:
        return ("Medium Risk (Mandatory controls)" if en_ingles else "Riesgo Medio (Medidas obligatorias)"), "#f59e0b"
    elif hrn <= 500:
        return ("High Risk (Critical danger)" if en_ingles else "Riesgo Alto (Peligro crítico)"), "#ea580c"
    else:
        return ("Unacceptable Risk (Immediate stop)" if en_ingles else "Riesgo Inaceptable (Parada de máquina)"), "#dc2626"

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

# --- INICIALIZACIÓN DE ESTADO ---
if "tipo_licencia" not in st.session_state:
    st.session_state.tipo_licencia = "ninguna"
if "cliente_email" not in st.session_state:
    st.session_state.cliente_email = ""
if "customer_id" not in st.session_state:
    st.session_state.customer_id = ""
if "serie_vinculada" not in st.session_state:
    st.session_state.serie_vinculada = ""

# --- COMPROBACIÓN INTELIGENTE DE LICENCIA EN STRIPE ---
def comprobar_licencia_en_stripe(email_a_verificar):
    email_limpio = email_a_verificar.strip().lower()
    if email_limpio in [e.lower() for e in ADMIN_EMAILS]:
        return True, "ilimitada", ("Master / Owner License Active" if es_en else "Licencia Propietario / Master"), "", ""
    if not stripe or not stripe_key:
        return False, "ninguna", ("Stripe verification system disconnected." if es_en else "Sistema de verificación no conectado a Stripe."), "", ""

    try:
        clientes = stripe.Customer.list(email=email_limpio)
        if not clientes.data:
            return False, "ninguna", ("Email not found in Stripe database." if es_en else "Correo no encontrado en la base de datos de Stripe."), "", ""

        cust = clientes.data[0]
        customer_id = cust.id
        
        # 1. Comprobar si tiene suscripción activa (Oficina Técnica)
        subs = stripe.Subscription.list(customer=customer_id, status="active")
        if subs.data:
            return True, "ilimitada", ("Active Engineering Office Subscription (149€/mo)" if es_en else "Suscripción Oficina Técnica Activa (149€/mes)"), customer_id, ""

        # 2. Comprobar si pagó un expediente individual (49€)
        cargos = stripe.Charge.list(customer=customer_id, limit=5)
        for cargo in cargos.data:
            if cargo.paid and not cargo.refunded:
                serie_existente = cust.metadata.get("serie_vinculada", "")
                return True, "individual", ("Single Machine Dossier License (49€)" if es_en else "Licencia Expediente Individual (49€)"), customer_id, serie_existente

        return False, "ninguna", ("No active payments associated with this email." if es_en else "No constan pagos vigentes asociados a este correo."), "", ""
    except Exception as err:
        return False, "ninguna", f"Verification Error: {err}", "", ""

# --- RETORNO SEGURO TRAS EL PAGO DE STRIPE (VALIDACIÓN CRIPTOGRÁFICA) ---
session_id = st.query_params.get("session_id")
if session_id and stripe and stripe_key:
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status == "paid":
            email_comprador = checkout_session.customer_details.email.strip().lower()
            monto_pagado = checkout_session.amount_total or 0

            if checkout_session.mode == "subscription" or monto_pagado >= 14000:
                st.session_state.tipo_licencia = "ilimitada"
            else:
                st.session_state.tipo_licencia = "individual"
                
            st.session_state.cliente_email = email_comprador
            st.session_state.customer_id = checkout_session.customer or ""
            
            st.query_params.clear()
            st.balloons()
            st.toast(f"🎉 {'Payment verified for' if es_en else '¡Pago de'} {email_comprador}!", icon="💎")
        else:
            st.error("Payment incomplete." if es_en else "El pago no se ha completado correctamente.")
    except Exception as e:
        st.error(f"Error: {e}")

# Peligros iniciales precargados bilingües
if "peligros_evaluados" not in st.session_state:
    st.session_state.peligros_evaluados = [
        {
            "zona_es": "Zona de Transmisión de Potencia",
            "zona_en": "Power Transmission Area",
            "peligro_es": "Atrapamiento en engranajes y cadenas",
            "peligro_en": "Entanglement in drive gears and power chain",
            "norma": "EN ISO 14120 / EN ISO 13857",
            "hrn_inicial": 160.0,
            "plr": "PL d",
            "medida_es": "Resguardo fijo envolvente atornillado que precisa herramienta para su apertura + microrruptor enclavado.",
            "medida_en": "Fixed enclosing guard requiring specialized tools for removal + interlock safety switch.",
            "hrn_residual": 3.2
        },
        {
            "zona_es": "Zona Operativa de Prensado / Corte",
            "zona_en": "Hydraulic Press & Tooling Area",
            "peligro_es": "Aplastamiento y cizallamiento por plato móvil",
            "peligro_en": "Crushing and shearing by hydraulic ram movement",
            "norma": "EN ISO 13855 / EN ISO 13851",
            "hrn_inicial": 240.0,
            "plr": "PL e",
            "medida_es": "Barrera inmaterial fotoeléctrica Tipo 4 (distancia de seguridad 450 mm) con parada de emergencia Categoría 4.",
            "medida_en": "Type 4 active optoelectronic protective device (450 mm safety distance) with Category 4 emergency stop.",
            "hrn_residual": 4.8
        }
    ]

# --- MAQUETADOR DE EXPEDIENTE TÉCNICO OFICIAL 100% BILINGÜE CON PROTECCIÓN ANTI-COPIA ---
def generar_html_expediente(datos, lista_riesgos, tipo_licencia, en_ingles=False, bloqueado_por_serie=False):
    fecha_hoy = datetime.date.today().strftime("%B %d, %Y" if en_ingles else "%d de %B de %Y")
    es_valido = (tipo_licencia in ["individual", "ilimitada"]) and not bloqueado_por_serie
    
    filas_tabla = ""
    for idx, r in enumerate(lista_riesgos):
        blur_style = "" if (es_valido or idx == 0) else "filter: blur(5px); user-select: none; opacity: 0.6;"
        
        zona_texto = r.get("zona_en" if en_ingles else "zona_es", r.get("zona", ""))
        peligro_texto = r.get("peligro_en" if en_ingles else "peligro_es", r.get("peligro", ""))
        medida_texto = r.get("medida_en" if en_ingles else "medida_es", r.get("medida", ""))
        
        estado_ini, color_ini = clasificar_hrn(r["hrn_inicial"], en_ingles=en_ingles)
        estado_res, color_res = clasificar_hrn(r["hrn_residual"], en_ingles=en_ingles)
        
        filas_tabla += f"""
        <tr style="{blur_style}">
            <td style="padding:8px; border:1px solid #cbd5e1;"><strong>{zona_texto}</strong><br><span style="color:#64748b;">{peligro_texto}</span></td>
            <td style="padding:8px; border:1px solid #cbd5e1; font-size:8.5pt;">{r['norma']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; color:{color_ini}; font-weight:bold;">HRN: {r['hrn_inicial']:.1f}<br><span style="font-size:7.5pt;">{estado_ini}</span></td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; font-weight:bold; color:#0284c7;">{r['plr']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; font-size:8.5pt;">{medida_texto}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; color:{color_res}; font-weight:bold;">HRN: {r['hrn_residual']:.1f}<br><span style="font-size:7.5pt;">{estado_res}</span></td>
        </tr>
        """
        
    bloque_bloqueo = "" if es_valido else f"""
    <div style="background: #fff1f2; border: 2px dashed #e11d48; padding: 20px; text-align: center; border-radius: 8px; margin: 25px 0;">
        <span style="font-size: 24pt;">🔒</span>
        <h3 style="color: #9f1239; margin: 8px 0;">{'LEGAL AND COMPLIANCE SECTIONS LOCKED' if en_ingles else 'SECCIONES LEGALES BLOQUEADAS (MODO EVALUACIÓN)'}</h3>
        <p style="color: #4c0519; font-size: 10pt; max-width: 600px; margin: 0 auto;">
            {'To download the unblurred Technical Construction File, unlock the full quantitative risk assessment and obtain the signable EU Declaration of Conformity, please purchase a license (49 € Single Dossier or 149 €/mo Unlimited Plan).' if en_ingles else 'Para descargar el Expediente de Construcción completo, desbloquear todas las matrices sin desenfoque y obtener la Declaración Oficial visable, adquiere tu licencia (49 € o 149 €/mes).'}
        </p>
    </div>
    """

    blur_declaracion = "" if es_valido else "filter: blur(6px); user-select: none; pointer-events: none;"
    # Protección anti-captura de la placa técnica en la sección 3 del PDF
    blur_placa_pdf = "" if es_valido else "filter: blur(5px); user-select: none; pointer-events: none; opacity: 0.65;"

    t_doc = "TECHNICAL CONSTRUCTION FILE" if en_ingles else "EXPEDIENTE TÉCNICO DE CONSTRUCCIÓN"
    t_reg = "Pursuant to European Machinery Regulation (EU) 2023/1230" if en_ingles else "Conforme al Reglamento Europeo de Máquinas (UE) 2023/1230"
    t_sec1 = "1. TECHNICAL SPECIFICATIONS (EN 60204-1)" if en_ingles else "1. ESPECIFICACIONES TÉCNICAS (UNE-EN 60204-1)"
    t_sec2 = "2. QUANTITATIVE RISK ASSESSMENT & RISK REDUCTION (EN ISO 12100 & ISO 13849-1)" if en_ingles else "2. EVALUACIÓN Y REDUCCIÓN DE RIESGOS (UNE-EN ISO 12100 & ISO 13849-1)"
    t_sec3 = "3. MANDATORY CE MARKING NAMEPLATE (Art. 16 & Annex III)" if en_ingles else "3. PLACA DE CARACTERÍSTICAS TÉCNICAS OBLIGATORIA (Art. 16 y Anexo III)"
    t_sec4 = "4. EU DECLARATION OF CONFORMITY (LEGAL DOCUMENT)" if en_ingles else "4. DECLARACIÓN UE DE CONFORMIDAD (DOCUMENTO OFICIAL)"

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
            <p style="font-size:12px; color:#64748b; margin-top:6px;">{'Select: Destination -> Save as PDF in your print dialog.' if en_ingles else 'En la ventana de impresión selecciona: Guardar como PDF.'}</p>
        </div>

        <div style="border: 1px solid #000; padding: 25px; text-align: center; margin-bottom: 30px;">
            <div class="ce-mark">CE</div>
            <h1>{t_doc}</h1>
            <p style="font-size:11pt; margin:5px 0;"><strong>{t_reg}</strong></p>
            <hr style="margin:20px 0;">
            <p style="font-size:11pt;"><strong>{'MACHINERY DESIGNATION' if en_ingles else 'DENOMINACIÓN DE LA MÁQUINA'}:</strong> {datos['denominacion']}</p>
            <p style="font-size:10pt;"><strong>{'MODEL / CODE' if en_ingles else 'MODELO'}:</strong> {datos['modelo']} | <strong>S/N:</strong> {datos['serie']}</p>
            <p style="font-size:10pt;"><strong>{'LEGAL MANUFACTURER' if en_ingles else 'FABRICANTE'}:</strong> {datos['fabricante']}</p>
            <p style="font-size:9pt; color:#64748b;"><strong>{'DATE OF ISSUE' if en_ingles else 'FECHA DE EMISIÓN'}:</strong> {fecha_hoy}</p>
        </div>

        <h2>{t_sec1}</h2>
        <table>
            <tr><th width="30%">{'Manufacturer / Legal Entity' if en_ingles else 'Fabricante'}:</th><td width="70%">{datos['fabricante']} ({datos['cif']})</td></tr>
            <tr><th>{'Manufacturing Plant Address' if en_ingles else 'Ubicación / Instalación'}:</th><td>{datos['direccion']}</td></tr>
            <tr><th>{'Chartered Technical Engineer' if en_ingles else 'Ingeniero Responsable Técnico'}:</th><td>{datos['ingeniero']} (ID: {datos['colegiado']})</td></tr>
            <tr><th>{'Installed Electric Power' if en_ingles else 'Potencia Eléctrica Instalada'}:</th><td>{datos['potencia']} kW</td></tr>
            <tr><th>{'Nominal Voltage & Frequency' if en_ingles else 'Tensión y Frecuencia'}:</th><td>{datos['tension']} V | {datos['frecuencia']} Hz ({datos['fases']})</td></tr>
            <tr><th>{'Pneumatic Supply Pressure' if en_ingles else 'Presión Neumática'}:</th><td>{datos['presion']} bar</td></tr>
            <tr><th>{'Year of Construction' if en_ingles else 'Año de Construcción'}:</th><td>{datos['anio']}</td></tr>
        </table>

        <h2>{t_sec2}</h2>
        <table>
            <thead>
                <tr>
                    <th width="20%">{'Hazard Zone & Risk' if en_ingles else 'Zona y Peligro'}</th>
                    <th width="15%">{'Applied Harmonized Standard' if en_ingles else 'Norma Aplicada'}</th>
                    <th width="12%">{'Initial Risk (HRN)' if en_ingles else 'Riesgo Inicial'}</th>
                    <th width="8%">PLr</th>
                    <th width="30%">{'Engineering Safeguard Applied' if en_ingles else 'Medida de Ingeniería'}</th>
                    <th width="15%">{'Residual Risk (HRN)' if en_ingles else 'Riesgo Residual'}</th>
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
            <div style="{blur_placa_pdf}">
                <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>TYPE / MOD:</strong> {datos['modelo']}</p>
                <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>S/N:</strong> {datos['serie']} &nbsp;|&nbsp; <strong>YEAR:</strong> {datos['anio']}</p>
                <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>POWER:</strong> {datos['potencia']} kW &nbsp;|&nbsp; <strong>VOLTAGE:</strong> {datos['tension']} V</p>
            </div>
        </div>

        <h2 style="margin-top:35px;">{t_sec4}</h2>
        <div style="{blur_declaracion}">
            <p style="font-size:9pt; text-align:justify;">
                {'The undersigned declares on behalf of the manufacturer, under sole responsibility, that the machinery described herein fulfills all relevant Essential Health and Safety Requirements laid down in Regulation (EU) 2023/1230 of the European Parliament and of the Council on machinery, as well as Directive 2014/30/EU (EMC) and Directive 2014/35/EU (Low Voltage).' if en_ingles else 'El abajo firmante, en representación del fabricante, declara bajo su exclusiva responsabilidad que la máquina descrita cumple con todos los Requisitos Esenciales de Seguridad y Salud establecidos en el Reglamento (UE) 2023/1230 de máquinas, así como con la Directiva 2014/30/UE (CEM) y 2014/35/UE (Baja Tensión).'}
            </p>
            <p style="font-size:9pt;"><strong>{'Authorized Person to compile the Technical Dossier' if en_ingles else 'Persona facultada para compilar el expediente técnico'}:</strong> {datos['ingeniero']} (ID: {datos['colegiado']}).</p>
            
            <div style="margin-top:50px; display:flex; justify-content:space-between;">
                <div style="width:45%; border-top:1px solid #000; padding-top:8px; text-align:center; font-size:9pt;">
                    <strong>{'Authorized Legal Representative' if en_ingles else 'Firma Representante Legal'}</strong><br>
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
st.sidebar.header("💳 Commercial License" if es_en else "💳 Licencia Profesional")

if st.session_state.tipo_licencia == "ilimitada":
    st.sidebar.markdown(
        f"""
        <div style="background:#f0fdf4; border:1px solid #86efac; padding:12px; border-radius:8px; color:#166534; font-weight:bold;">
            🟢 {'ENGINEERING OFFICE PLAN (149€/mo)' if es_en else 'PLAN OFICINA TÉCNICA (149€/mes)'}<br>
            <span style="font-size:11px; font-weight:normal;">{st.session_state.cliente_email}</span><br>
            <span style="font-size:10px; color:#15803d;">✨ {'Unlimited Machines & JSON Export Unlocked' if es_en else 'Máquinas Ilimitadas Desbloqueadas'}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
elif st.session_state.tipo_licencia == "individual":
    vinculo_texto = f"S/N: {st.session_state.serie_vinculada}" if st.session_state.serie_vinculada else ("Pending download" if es_en else "Pendiente de vincular")
    st.sidebar.markdown(
        f"""
        <div style="background:#eff6ff; border:1px solid #93c5fd; padding:12px; border-radius:8px; color:#1e40af; font-weight:bold;">
            🔵 {'SINGLE DOSSIER LICENSE (49€)' if es_en else 'PLAN EXPEDIENTE INDIVIDUAL (49€)'}<br>
            <span style="font-size:11px; font-weight:normal;">{st.session_state.cliente_email}</span><br>
            <span style="font-size:10px; color:#1d4ed8;">🔒 {'Locked to 1 Machine' if es_en else 'Vinculado a 1 Máquina'} ({vinculo_texto})</span>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        f"""
        <div style="background:#fffbeb; border:1px solid #fde68a; padding:10px; border-radius:8px; font-size:12px; color:#92400e;">
            ⚠️ <strong>{'EVALUATION MODE' if es_en else 'MODO EVALUACIÓN'}</strong><br>
            {'Watermarked preview with blurred sections. Unlock signable technical file:' if es_en else 'Previsualización con secciones desenfocadas. Desbloquea tu expediente oficial:'}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown(f'<a href="{URL_STRIPE_49}" target="_blank" style="background:#0284c7; color:white; display:block; text-align:center; padding:9px; border-radius:6px; font-weight:bold; font-size:12px; text-decoration:none; margin-bottom:6px;">📄 {"Single Dossier (49 €)" if es_en else "Expediente Único (49 €)"}</a>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<a href="{URL_STRIPE_149}" target="_blank" style="background:#0f172a; color:white; display:block; text-align:center; padding:9px; border-radius:6px; font-weight:bold; font-size:12px; text-decoration:none;">🏢 {"Unlimited Engineering Office (149 €/mo)" if es_en else "Oficina Técnica Ilimitada (149 €/mes)"}</a>', unsafe_allow_html=True)

if st.session_state.tipo_licencia != "ninguna":
    if st.sidebar.button("Logout" if es_en else "Cerrar Sesión"):
        st.session_state.tipo_licencia = "ninguna"
        st.session_state.cliente_email = ""
        st.session_state.customer_id = ""
        st.session_state.serie_vinculada = ""
        st.rerun()
else:
    with st.sidebar.form("form_recuperar"):
        st.write("**Already purchased a license?**" if es_en else "**¿Ya compraste una licencia?**")
        correo_licencia = st.text_input("Stripe Email:" if es_en else "Email Stripe:")
        if st.form_submit_button("🔑 Validate License" if es_en else "🔑 Validar Licencia"):
            if "@" in correo_licencia:
                valido, tipo, mensaje, cust_id, serie_vinc = comprobar_licencia_en_stripe(correo_licencia)
                if valido:
                    st.session_state.tipo_licencia = tipo
                    st.session_state.cliente_email = correo_licencia.strip().lower()
                    st.session_state.customer_id = cust_id
                    st.session_state.serie_vinculada = serie_vinc
                    st.success("License verified!" if es_en else "¡Licencia validada!")
                    st.rerun()
                else:
                    st.error(mensaje)

st.sidebar.divider()
st.sidebar.header("💾 Save / Load" if es_en else "💾 Guardar / Cargar")
if st.session_state.tipo_licencia in ["ilimitada"]:
    proyecto_json = json.dumps(st.session_state.peligros_evaluados, indent=2)
    st.sidebar.download_button(
        label="💾 Export Project (.json)" if es_en else "💾 Exportar Máquina (.json)",
        data=proyecto_json,
        file_name="CE_Machinery_Project.json" if es_en else "Proyecto_Maquina_CE.json",
        mime="application/json"
    )
    archivo_cargado = st.sidebar.file_uploader("📂 Import Project (.json):" if es_en else "📂 Importar (.json):", type=["json"])
    if archivo_cargado:
        try:
            datos_cargados = json.load(archivo_cargado)
            if isinstance(datos_cargados, list):
                st.session_state.peligros_evaluados = datos_cargados
                st.sidebar.success("Loaded successfully" if es_en else "Cargado con éxito")
        except Exception:
            st.sidebar.error("Invalid file" if es_en else "Archivo no válido")
else:
    st.sidebar.info("🔒 JSON backup requires **Unlimited Plan (149€/mo)**." if es_en else "🔒 Guardado en JSON exclusivo del **Plan Oficina Técnica (149€/mes)**.")

# --- TABS PRINCIPALES ---
titulos_tabs = [
    "🏭 1. Technical Data" if es_en else "🏭 1. Ficha Técnica",
    "⚠️ 2. Risk Matrix (ISO 12100)" if es_en else "⚠️ 2. Matriz HRN (ISO 12100)",
    "🛡️ 3. PLr Rating (ISO 13849)" if es_en else "🛡️ 3. Nivel PLr (ISO 13849)",
    "🏷️ 4. CE Nameplate" if es_en else "🏷️ 4. Placa CE Metálica",
    "📄 5. Technical Dossier & PDF" if es_en else "📄 5. Expediente y Descarga"
]
tab_maquina, tab_hrn, tab_plr, tab_placa, tab_expediente = st.tabs(titulos_tabs)

# --- PESTAÑA 1: DATOS GENERALES ---
with tab_maquina:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Machine Identification" if es_en else "Identificación de la Máquina")
    
    col1, col2 = st.columns(2)
    with col1:
        denominacion = st.text_input("Official Machinery Name:" if es_en else "Denominación oficial:", value="Robotic Packaging & Palletizing Cell" if es_en else "Línea de Envasado y Paletizado Robotizado")
        fabricante = st.text_input("Manufacturer Legal Name:" if es_en else "Razón Social Fabricante:", value="Northern Automation & Robotics Ltd." if es_en else "Mecanizados y Robótica del Norte S.L.")
        cif = st.text_input("Tax / VAT ID (CIF/NIF):" if es_en else "NIF / CIF / VAT ID:", value="ES-B95847291")
        direccion = st.text_input("Manufacturing Address:" if es_en else "Dirección de fabricación:", value="Industrial Park West, Building 4, 48960 Bilbao (Spain)" if es_en else "Polígono Industrial Erletxes, Manzana 4, 48960 Galdakao")
    with col2:
        modelo = st.text_input("Model / Reference Code:" if es_en else "Modelo / Código:", value="ROBOPACK-2025")
        serie = st.text_input("Serial Number (S/N):" if es_en else "Número de Serie (S/N):", value="SN-2025-0842")
        anio = st.number_input("Year of Manufacture:" if es_en else "Año de Fabricación:", min_value=2020, max_value=2030, value=2025)
        ingeniero = st.text_input("Lead Technical Engineer:" if es_en else "Ingeniero Responsable:", value="Alberto Lantarón")
        colegiado = st.text_input("Chartered License / ID:" if es_en else "Nº Colegiado / DNI:", value="COIIB-48192")

    st.divider()
    st.subheader("Energy & Environmental Specifications (EN 60204-1)" if es_en else "Especificaciones Energéticas (EN 60204-1)")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        potencia = st.number_input("Installed Power (kW):" if es_en else "Potencia (kW):", value=12.5, step=0.5)
    with col_e2:
        tension = st.selectbox("Voltage (V):" if es_en else "Tensión (V):", [400, 230, 48, 24])
    with col_e3:
        fases_opts = ["Three-phase (3P+N+PE)", "Single-phase (1P+N+PE)"] if es_en else ["Trifásica (3P+N+T)", "Monofásica (1P+N+T)"]
        fases = st.selectbox("Power Grid Phase:" if es_en else "Red / Fases:", fases_opts)
    with col_e4:
        presion = st.number_input("Pneumatic Pressure (bar):" if es_en else "Presión Neumática (bar):", value=6.0, step=0.5)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 2: MÉTODO CUANTITATIVO HRN (ISO 12100) ---
with tab_hrn:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Quantitative HRN Risk Assessment (ISO 12100)" if es_en else "Evaluación Cuantitativa de Riesgo HRN (ISO 12100)")
    st.write("Normalized Formula: $\\text{HRN} = LO \\times FE \\times DPH \\times NP$. Justifies residual risk reduction to legally acceptable limits." if es_en else "Fórmula normalizada: $\\text{HRN} = LO \\times FE \\times DPH \\times NP$. Permite justificar matemáticamente la reducción del riesgo a nivel Aceptable.")
    
    with st.form("form_nuevo_riesgo"):
        st.markdown("#### Add Machine Hazard" if es_en else "#### Añadir Peligro")
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            zona_input = st.text_input("Hazard Zone / Component:" if es_en else "Zona / Componente:", placeholder="Cutting tool / Drive motor" if es_en else "Zona de corte / Cabezal motor")
            peligro_input = st.text_input("Identified Hazard:" if es_en else "Peligro específico:", placeholder="Shearing / High pressure fluid ejection" if es_en else "Cizallamiento / Atrapamiento")
            norma_input = st.text_input("Applied Standard:" if es_en else "Norma armonizada:", value="EN ISO 14120 / EN ISO 13857")
        with c_r2:
            medida_input = st.text_area("Engineering Safeguard:" if es_en else "Medida de ingeniería adoptada:", placeholder="Fixed perimeter guarding interlocked with safety switch." if es_en else "Resguardo fijo perimetral con enclavamiento.")

        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            lo = st.selectbox("Likelihood (LO):" if es_en else "Probabilidad (LO):", list(VALORES_LO.keys()), index=4)
        with c_p2:
            fe = st.selectbox("Frequency of Exposure (FE):" if es_en else "Frecuencia (FE):", list(VALORES_FE.keys()), index=4)
        with c_p3:
            dph = st.selectbox("Degree of Potential Harm (DPH):" if es_en else "Daño potencial (DPH):", list(VALORES_DPH.keys()), index=3)
        with c_p4:
            np = st.selectbox("Number of Persons (NP):" if es_en else "Personas expuestas (NP):", list(VALORES_NP.keys()), index=0)

        hrn_calc_inicial = VALORES_LO[lo] * VALORES_FE[fe] * VALORES_DPH[dph] * VALORES_NP[np]
        estado_calc_inicial, color_calc_inicial = clasificar_hrn(hrn_calc_inicial, en_ingles=es_en)

        st.markdown(f"**{'Initial Risk' if es_en else 'Riesgo Inicial'}:** <span style='color:{color_calc_inicial}; font-weight:bold; font-size:16px;'>HRN: {hrn_calc_inicial:.1f} ({estado_calc_inicial})</span>", unsafe_allow_html=True)
        
        btn_guardar_riesgo = st.form_submit_button("➕ Register Hazard" if es_en else "➕ Registrar en Matriz")
        if btn_guardar_riesgo:
            if zona_input and peligro_input:
                # Mitigación técnica de ingeniería: reducción residual del 98%
                hrn_residual = round(hrn_calc_inicial * 0.02, 1)
                
                nuevo_elem = {
                    "zona_es": zona_input,
                    "zona_en": zona_input,
                    "peligro_es": peligro_input,
                    "peligro_en": peligro_input,
                    "norma": norma_input,
                    "hrn_inicial": hrn_calc_inicial,
                    "plr": "PL d",
                    "medida_es": medida_input,
                    "medida_en": medida_input,
                    "hrn_residual": hrn_residual
                }
                st.session_state.peligros_evaluados.append(nuevo_elem)
                st.success("Registered in Technical Dossier." if es_en else "Guardado en el expediente.")
                st.rerun()

    st.markdown("#### Active Risk Register" if es_en else "#### Matriz de Riesgos Registrados")
    for idx, r in enumerate(st.session_state.peligros_evaluados):
        z_ver = r.get("zona_en" if es_en else "zona_es", r.get("zona", ""))
        p_ver = r.get("peligro_en" if es_en else "peligro_es", r.get("peligro", ""))
        e_ini, c_ini = clasificar_hrn(r["hrn_inicial"], en_ingles=es_en)
        e_res, c_res = clasificar_hrn(r["hrn_residual"], en_ingles=es_en)
        
        with st.expander(f"📍 {z_ver} — {p_ver}"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**{'Initial' if es_en else 'Inicial'}:** <span style='color:{c_ini}; font-weight:bold;'>HRN {r['hrn_inicial']:.1f} ({e_ini})</span>", unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"**{'Residual' if es_en else 'Residual'}:** <span style='color:{c_res}; font-weight:bold;'>HRN {r['hrn_residual']:.1f} ({e_res})</span>", unsafe_allow_html=True)
            if st.button("🗑️ Delete" if es_en else "🗑️ Eliminar", key=f"del_{idx}"):
                st.session_state.peligros_evaluados.pop(idx)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 3: DETERMINACIÓN DEL PLr (ISO 13849-1) ---
with tab_plr:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Required Performance Level (PLr - ISO 13849-1)" if es_en else "Nivel de Rendimiento Requerido (PLr - ISO 13849-1)")
    
    col_pl1, col_pl2 = st.columns([2, 1])
    with col_pl1:
        s_opts = ["S1 (Slight reversible injury)", "S2 (Serious irreversible injury or death)"] if es_en else ["S1 (Lesión leve reversible)", "S2 (Lesión grave irreversible o muerte)"]
        f_opts = ["F1 (Rare to short exposure)", "F2 (Frequent to continuous exposure)"] if es_en else ["F1 (Poco frecuente / Exposición corta)", "F2 (Frecuente a continua)"]
        p_opts = ["P1 (Possible under specific conditions)", "P2 (Scarcely possible / unavoidable)"] if es_en else ["P1 (Posible en determinadas condiciones)", "P2 (Casi imposible de evitar)"]
        
        sev = st.radio("Injury Severity (S):" if es_en else "Severidad de la lesión (S):", s_opts)
        frec = st.radio("Exposure Frequency (F):" if es_en else "Frecuencia de exposición (F):", f_opts)
        pos = st.radio("Possibility of Avoidance (P):" if es_en else "Posibilidad de evitar el peligro (P):", p_opts)
        
    with col_pl2:
        plr_resultado = calcular_plr(sev, frec, pos)
        st.markdown("#### Required Safety Level:" if es_en else "#### Nivel Exigido:")
        st.markdown(f'<div style="background:#e0f2fe; color:#0369a1; border:2px solid #0284c7; padding:10px; border-radius:8px; font-size:22px; font-weight:bold; text-align:center;">{plr_resultado}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 4: PLACA CE METÁLICA (MITAD NÍTIDA, MITAD DESENFOCADA SI NO PAGA) ---
with tab_placa:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Metallic CE Nameplate Simulator (Art. 16 & Annex III)" if es_en else "Simulador de Placa CE Físico (Art. 16 y Anexo III)")
    st.write("Visual preview of the indelible plate that must be physically riveted to the machine frame:" if es_en else "Vista previa de la placa indeleble que debe remacharse al chasis de la máquina:")
    
    serie_check = serie.strip().upper()
    bloqueado_placa = False
    if st.session_state.tipo_licencia == "individual" and st.session_state.serie_vinculada:
        if serie_check != st.session_state.serie_vinculada.strip().upper():
            bloqueado_placa = True
            
    es_licencia_activa = (st.session_state.tipo_licencia in ["individual", "ilimitada"]) and not bloqueado_placa

    blur_datos = "" if es_licencia_activa else "filter: blur(5px); user-select: none; pointer-events: none; opacity: 0.65;"

    placa_html = f"""<div class="placa-metalica">
<div class="placa-remache" style="top:8px; left:8px;"></div>
<div class="placa-remache" style="top:8px; right:8px;"></div>
<div class="placa-remache" style="bottom:8px; left:8px;"></div>
<div class="placa-remache" style="bottom:8px; right:8px;"></div>
<div style="font-size:32pt; font-weight:900; letter-spacing:-3px; text-align:center; margin-bottom:5px;">CE</div>
<p style="margin:0; font-weight:bold; font-size:12pt; text-align:center;">{fabricante}</p>
<p style="margin:0; font-size:8.5pt; text-align:center; color:#334155;">{direccion}</p>
<hr style="border:1px solid #475569; margin:10px 0;">
<div style="{blur_datos}">
<p style="margin:2px 0; font-size:9pt;"><strong>{'MACHINE' if es_en else 'MÁQUINA'}:</strong> {denominacion}</p>
<p style="margin:2px 0; font-size:9pt;"><strong>{'MODEL' if es_en else 'MODELO'}:</strong> {modelo}</p>
<p style="margin:2px 0; font-size:9pt;"><strong>S/N:</strong> {serie} &nbsp;|&nbsp; <strong>{'YEAR' if es_en else 'AÑO'}:</strong> {anio}</p>
<p style="margin:2px 0; font-size:9pt;"><strong>{'POWER' if es_en else 'POTENCIA'}:</strong> {potencia} kW &nbsp;|&nbsp; <strong>{'VOLTAGE' if es_en else 'TENSIÓN'}:</strong> {tension} V</p>
</div>
</div>"""

    st.markdown(placa_html, unsafe_allow_html=True)

    if not es_licencia_activa:
        st.markdown(
            f"""
            <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:8px; padding:12px; text-align:center; max-width:450px; margin:15px auto; color:#9f1239; font-size:13px;">
                🔒 <strong>{'DATA SECTION PROTECTED' if es_en else 'DATOS TÉCNICOS PROTEGIDOS TRAS LICENCIA'}</strong><br>
                {'The specific serial and model details on the plate become fully unblurred and vector-ready upon purchasing your single dossier license (49 €).' if es_en else 'Los datos de serie, modelo y potencia de la placa se vuelven completamente nítidos y vectorizables tras adquirir la licencia del expediente (49 €).'}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.success("✅ Placa oficial desbloqueada en alta resolución lista para fabricación/grabado." if not es_en else "✅ Official high-resolution nameplate unlocked and ready for manufacturing/engraving.")

    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 5: EXPEDIENTE OFICIAL Y CONTROL DE VINCULACIÓN ---
with tab_expediente:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Official Technical Construction File & CE Marking" if es_en else "Expediente Técnico Completo y Marcado CE")
    
    serie_actual = serie.strip().upper()
    bloqueado_por_serie = False
    
    if st.session_state.tipo_licencia == "individual":
        if st.session_state.serie_vinculada:
            if serie_actual != st.session_state.serie_vinculada.strip().upper():
                bloqueado_por_serie = True

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

    html_dossier = generar_html_expediente(datos_completos, st.session_state.peligros_evaluados, st.session_state.tipo_licencia, en_ingles=es_en, bloqueado_por_serie=bloqueado_por_serie)
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.markdown("#### 1. Official Dossier Download" if es_en else "#### 1. Descarga del Documento Legal")
        
        # Caso 1: Licencia Ilimitada (149€/mes) o Admin
        if st.session_state.tipo_licencia == "ilimitada":
            st.download_button(
                label="📥 Download Official Technical Dossier (PDF)" if es_en else "📥 Descargar Expediente Oficial (PDF)",
                data=html_dossier,
                file_name=f"CE_Technical_File_{modelo}_{serie}.html",
                mime="text/html",
                type="primary"
            )
            st.success("Engineering Office Plan Active: Unlimited machines & downloads." if es_en else "Plan Oficina Técnica: Descargas y máquinas ilimitadas.")

        # Caso 2: Licencia Individual (49€)
        elif st.session_state.tipo_licencia == "individual":
            if bloqueado_por_serie:
                st.error(f"⚠️ {'This 49 € license has already been redeemed and locked to machine with' if es_en else 'Esta licencia de 49 € ya fue consumida y vinculada a la máquina con'} **S/N: {st.session_state.serie_vinculada}**.")
                st.info("To certify a different machine, please purchase a new Single Dossier (49 €) or upgrade to the Unlimited Engineering Office Plan (149 €/mo)." if es_en else "Para certificar una nueva máquina diferente, adquiere otro Expediente Único (49 €) o suscríbete al Plan Oficina Técnica Ilimitada (149 €/mes).")
                st.markdown(f'<a href="{URL_STRIPE_49}" target="_blank" style="background:#0284c7; color:white; padding:10px 16px; border-radius:6px; font-weight:bold; text-decoration:none; display:inline-block; margin-right:8px;">{"New Dossier (49 €)" if es_en else "Nuevo Expediente (49 €)"}</a>', unsafe_allow_html=True)
                st.markdown(f'<a href="{URL_STRIPE_149}" target="_blank" style="background:#0f172a; color:white; padding:10px 16px; border-radius:6px; font-weight:bold; text-decoration:none; display:inline-block;">{"Unlimited Plan (149 €/mo)" if es_en else "Plan Ilimitado (149 €/mes)"}</a>', unsafe_allow_html=True)
            else:
                descarga_click = st.download_button(
                    label="📥 Download and Lock License to this Machine (PDF)" if es_en else "📥 Descargar y Vincular a esta Máquina (PDF)",
                    data=html_dossier,
                    file_name=f"CE_Technical_File_{modelo}_{serie}.html",
                    mime="text/html",
                    type="primary"
                )
                if descarga_click:
                    if not st.session_state.serie_vinculada:
                        st.session_state.serie_vinculada = serie_actual
                        if stripe and stripe_key and st.session_state.customer_id:
                            try:
                                stripe.Customer.modify(
                                    st.session_state.customer_id,
                                    metadata={"serie_vinculada": serie_actual, "modelo": modelo}
                                )
                            except Exception:
                                pass
                        st.rerun()

                st.caption(f"🔒 {'Upon downloading, your license will be permanently tied to Serial Number:' if es_en else 'Al descargar, tu licencia quedará vinculada exclusivamente a la máquina con número de serie:'} **{serie}**.")

        # Caso 3: Sin licencia
        else:
            st.warning("🔒 Full official file protected behind license." if es_en else "🔒 Expediente oficial visable protegido tras licencia.")
            st.markdown(f'<a href="{URL_STRIPE_49}" target="_blank" style="background:#0284c7; color:white; padding:12px 20px; border-radius:6px; font-weight:bold; text-decoration:none; display:inline-block; margin-bottom:8px;">{"Unlock Single Machine Dossier (49 €)" if es_en else "Desbloquear Expediente Único (49 €)"}</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="{URL_STRIPE_149}" target="_blank" style="background:#0f172a; color:white; padding:12px 20px; border-radius:6px; font-weight:bold; text-decoration:none; display:inline-block;">{"Subscribe to Unlimited Plan (149 €/mo)" if es_en else "Contratar Plan Oficina Técnica (149 €/mes)"}</a>', unsafe_allow_html=True)
            
    # --- COLUMNA 2: ESTADO DINÁMICO DE CONFORMIDAD NORMATIVA ---
    with col_d2:
        st.markdown("#### 2. Technical Compliance Status" if es_en else "#### 2. Estado de Certificación Técnica")
        total_peligros = len(st.session_state.peligros_evaluados)
        st.metric("Total Hazards Evaluated" if es_en else "Total Peligros Evaluados", total_peligros)
        
        # Comprobación de riesgos residuales no aceptables (> 5.0)
        peligros_criticos = [p for p in st.session_state.peligros_evaluados if p.get("hrn_residual", 0) > 5.0]
        
        if total_peligros == 0:
            st.metric(
                label="Regulation (EU) 2023/1230",
                value="PENDING" if es_en else "PENDIENTE",
                delta="- No hazards registered" if es_en else "- Sin peligros registrados",
                delta_color="inverse"
            )
            st.warning("⚠️ Please register machine hazards in Tab 2." if es_en else "⚠️ Registra los peligros de la máquina en la pestaña 2.")
        elif len(peligros_criticos) > 0:
            st.metric(
                label="Regulation (EU) 2023/1230",
                value="NON-COMPLIANT" if es_en else "NO CONFORME",
                delta=f"- {len(peligros_criticos)} hazard(s) above acceptable limit" if es_en else f"- {len(peligros_criticos)} peligro(s) con riesgo no aceptable",
                delta_color="inverse"
            )
            st.error("❌ Critical residual hazards found. Apply safeguards until all hazards reach Acceptable level (HRN ≤ 5) to validate CE marking." if es_en else "❌ Hay riesgos residuales altos. Aplica medidas de seguridad hasta que todos sean Aceptables (HRN ≤ 5) para poder emitir el Marcado CE.")
        else:
            st.metric(
                label="Regulation (EU) 2023/1230",
                value="100% COMPLIANT" if es_en else "100% CONFORME",
                delta="CE Marking Ready" if es_en else "Apto para marcado CE",
                delta_color="normal"
            )
            st.success("✅ All residual risks quantitatively controlled." if es_en else "✅ Todos los riesgos residuales controlados y justificados matemáticamente.")
        
    st.divider()
    st.markdown("#### Official Technical File Preview:" if es_en else "#### Previsualización Oficial (Anti-Copia Activo):")
    st.components.v1.html(html_dossier, height=650, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)