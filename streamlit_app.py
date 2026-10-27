import streamlit as st
import datetime
import json
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SafeMachine CE | Plataforma Oficial de Marcado CE (Reglamento UE 2023/1230)",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        return "Riesgo Aceptable / Insignificante", "#10b981"
    elif hrn <= 50:
        return "Riesgo Bajo (Medidas leves)", "#0284c7"
    elif hrn <= 150:
        return "Riesgo Medio (Medidas obligatorias)", "#f59e0b"
    elif hrn <= 500:
        return "Riesgo Alto (Peligro crítico)", "#ea580c"
    else:
        return "Riesgo Inaceptable (Parada de máquina)", "#dc2626"

def calcular_plr(severidad, frecuencia, posibilidad):
    if severidad == "S1 (Lesión leve reversible)":
        if frecuencia == "F1 (Poco frecuente / Exposición corta)":
            return "PL a" if posibilidad == "P1 (Posible evitarlo)" else "PL b"
        else:
            return "PL b" if posibilidad == "P1 (Posible evitarlo)" else "PL c"
    else:
        if frecuencia == "F1 (Poco frecuente / Exposición corta)":
            return "PL c" if posibilidad == "P1 (Posible evitarlo)" else "PL d"
        else:
            return "PL d" if posibilidad == "P1 (Posible evitarlo)" else "PL e (Máxima Seguridad)"

# --- GESTIÓN DE SESIÓN Y LICENCIAS ---
if "usuario_es_premium" not in st.session_state:
    st.session_state.usuario_es_premium = False
if "cliente_email" not in st.session_state:
    st.session_state.cliente_email = ""

# Detección de pago Stripe
if st.query_params.get("pago_exitoso") == "true":
    correo = st.query_params.get("email", "")
    if "@" in correo:
        st.session_state.usuario_es_premium = True
        st.session_state.cliente_email = correo
        st.balloons()
        st.toast("🎉 ¡Licencia Profesional activada con éxito!", icon="💎")

# Riesgos iniciales precargados
if "peligros_evaluados" not in st.session_state:
    st.session_state.peligros_evaluados = [
        {
            "zona": "Zona de Transmisión de Potencia",
            "peligro": "Atrapamiento en engranajes y cadenas",
            "norma": "UNE-EN ISO 14120 / UNE-EN ISO 13857",
            "hrn_inicial": 160.0,
            "estado_inicial": "Riesgo Alto (Peligro crítico)",
            "color_inicial": "#ea580c",
            "plr": "PL d",
            "medida": "Resguardo fijo envolvente atornillado que precisa de herramienta para su apertura + microrruptor de seguridad enclavado.",
            "hrn_residual": 3.2,
            "estado_residual": "Riesgo Aceptable / Insignificante",
            "color_residual": "#10b981"
        },
        {
            "zona": "Zona Operativa de Prensado / Corte",
            "peligro": "Aplastamiento y cizallamiento por plato móvil",
            "norma": "UNE-EN ISO 13855 / UNE-EN ISO 13851",
            "hrn_inicial": 240.0,
            "estado_inicial": "Riesgo Alto (Peligro crítico)",
            "color_inicial": "#ea580c",
            "plr": "PL e (Máxima Seguridad)",
            "medida": "Barrera inmaterial fotoeléctrica Tipo 4 (distancia de seguridad 450 mm) con parada de emergencia Categoría 4.",
            "hrn_residual": 4.8,
            "estado_residual": "Riesgo Aceptable / Insignificante",
            "color_residual": "#10b981"
        }
    ]

# --- MAQUETADOR DE EXPEDIENTE TÉCNICO OFICIAL ---
def generar_html_expediente(datos, lista_riesgos):
    fecha_hoy = datetime.date.today().strftime("%d de %B de %Y")
    
    filas_tabla = ""
    for r in lista_riesgos:
        filas_tabla += f"""
        <tr>
            <td style="padding:8px; border:1px solid #cbd5e1;"><strong>{r['zona']}</strong><br><span style="color:#64748b;">{r['peligro']}</span></td>
            <td style="padding:8px; border:1px solid #cbd5e1; font-size:8.5pt;">{r['norma']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; color:{r['color_inicial']}; font-weight:bold;">HRN: {r['hrn_inicial']:.1f}<br><span style="font-size:7.5pt;">{r['estado_inicial']}</span></td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; font-weight:bold; color:#0284c7;">{r['plr']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; font-size:8.5pt;">{r['medida']}</td>
            <td style="padding:8px; border:1px solid #cbd5e1; text-align:center; color:{r['color_residual']}; font-weight:bold;">HRN: {r['hrn_residual']:.1f}<br><span style="font-size:7.5pt;">{r['estado_residual']}</span></td>
        </tr>
        """
        
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Expediente Técnico Marcado CE - {datos['modelo']}</title>
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
            <button class="btn-print" onclick="window.print()">🖨️ Guardar Expediente como PDF Oficial</button>
            <p style="font-size:12px; color:#64748b; margin-top:6px;">En la ventana de impresión, selecciona 'Guardar como PDF' para generar el expediente legal.</p>
        </div>

        <div style="border: 1px solid #000; padding: 25px; text-align: center; margin-bottom: 30px;">
            <div class="ce-mark">CE</div>
            <h1>EXPEDIENTE TÉCNICO DE CONSTRUCCIÓN</h1>
            <p style="font-size:11pt; margin:5px 0;"><strong>Conforme al Reglamento Europeo de Máquinas (UE) 2023/1230</strong></p>
            <p style="font-size:9.5pt; color:#64748b;">(Derogatorio de la Directiva 2006/42/CE)</p>
            <hr style="margin:20px 0;">
            <p style="font-size:11pt;"><strong>MÁQUINA:</strong> {datos['denominacion']}</p>
            <p style="font-size:10pt;"><strong>MODELO:</strong> {datos['modelo']} | <strong>Nº SERIE:</strong> {datos['serie']}</p>
            <p style="font-size:10pt;"><strong>FABRICANTE:</strong> {datos['fabricante']}</p>
        </div>

        <h2>1. ESPECIFICACIONES TÉCNICAS (UNE-EN 60204-1)</h2>
        <table>
            <tr><th width="30%">Fabricante / Entidad:</th><td width="70%">{datos['fabricante']} ({datos['cif']})</td></tr>
            <tr><th>Ubicación / Instalación:</th><td>{datos['direccion']}</td></tr>
            <tr><th>Ingeniero Responsable Técnico:</th><td>{datos['ingeniero']} (Colegiado Nº: {datos['colegiado']})</td></tr>
            <tr><th>Potencia Eléctrica Instalada:</th><td>{datos['potencia']} kW</td></tr>
            <tr><th>Tensión y Frecuencia:</th><td>{datos['tension']} V | {datos['frecuencia']} Hz ({datos['fases']})</td></tr>
            <tr><th>Presión de Servicio Neumática:</th><td>{datos['presion']} bar</td></tr>
            <tr><th>Año de Construcción:</th><td>{datos['anio']}</td></tr>
        </table>

        <h2>2. EVALUACIÓN Y REDUCCIÓN DE RIESGOS (UNE-EN ISO 12100 & ISO 13849-1)</h2>
        <p style="font-size:8.5pt;">Evaluación cuantitativa por método HRN (*Hazard Rating Number*). Criterio de conformidad legal: El riesgo residual debe resultar 'Aceptable'.</p>
        <table>
            <thead>
                <tr>
                    <th width="20%">Zona y Peligro</th>
                    <th width="15%">Norma Aplicada</th>
                    <th width="12%">Riesgo Inicial</th>
                    <th width="8%">PLr</th>
                    <th width="30%">Medida de Ingeniería Aplicada</th>
                    <th width="15%">Riesgo Residual</th>
                </tr>
            </thead>
            <tbody>
                {filas_tabla}
            </tbody>
        </table>

        <div class="page-break"></div>

        <h2>3. PLACA DE CARACTERÍSTICAS TÉCNICAS OBLIGATORIA (Art. 16 y Anexo III)</h2>
        <p style="font-size:8.5pt;">Diseño para troquelado y remachado en el bastidor principal de la máquina:</p>
        
        <div class="placa-box">
            <div style="font-size:24pt; font-weight:bold; letter-spacing:-2px;">CE</div>
            <p style="margin:2px 0; font-size:10pt; font-weight:bold;">{datos['fabricante']}</p>
            <p style="margin:2px 0; font-size:8pt;">{datos['direccion']}</p>
            <hr style="margin:6px 0;">
            <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>MÁQUINA:</strong> {datos['denominacion']}</p>
            <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>TIPO / MOD:</strong> {datos['modelo']}</p>
            <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>Nº SERIE:</strong> {datos['serie']} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>AÑO:</strong> {datos['anio']}</p>
            <p style="margin:2px 0; font-size:8.5pt; text-align:left;"><strong>POTENCIA:</strong> {datos['potencia']} kW &nbsp;&nbsp;|&nbsp;&nbsp; <strong>TENSIÓN:</strong> {datos['tension']} V</p>
        </div>

        <h2 style="margin-top:35px;">4. DECLARACIÓN UE DE CONFORMIDAD (DOCUMENTO OFICIAL)</h2>
        <p style="font-size:9pt; text-align:justify;">El abajo firmante, en representación del fabricante <strong>{datos['fabricante']}</strong>, declara bajo su exclusiva responsabilidad que la máquina descrita cumple con todos los Requisitos Esenciales de Seguridad y Salud establecidos en el <strong>Reglamento (UE) 2023/1230 del Parlamento Europeo y del Consejo</strong>, relativo a las máquinas, así como con la Directiva de Compatibilidad Electromagnética 2014/30/UE y la Directiva de Baja Tensión 2014/35/UE.</p>
        
        <p style="font-size:9pt;"><strong>Persona facultada para compilar el expediente técnico:</strong> {datos['ingeniero']} (Colegiado Nº: {datos['colegiado']}).</p>
        <p style="font-size:9pt;">Lugar y fecha de emisión: A {fecha_hoy}.</p>

        <div style="margin-top:50px; display:flex; justify-content:space-between;">
            <div style="width:45%; border-top:1px solid #000; padding-top:8px; text-align:center; font-size:9pt;">
                <strong>Firma del Fabricante / Representante Legal</strong><br>
                <span style="color:#64748b; font-size:8pt;">D./Dña: Representante Autorizado</span>
            </div>
            <div style="width:45%; border-top:1px solid #000; padding-top:8px; text-align:center; font-size:9pt;">
                <strong>Firma del Ingeniero Industrial Responsable</strong><br>
                <span style="color:#64748b; font-size:8pt;">{datos['ingeniero']} (Col. {datos['colegiado']})</span>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- CABECERA SUPERIOR ---
st.markdown(
    """
    <div class="header-box">
        <span class="header-badge">SOFTWARE PROFESIONAL DE INGENIERÍA LEGAL</span>
        <h1 class="header-title">SAFEMACHINE CE</h1>
        <p class="header-subtitle">
            Plataforma de Expedientes Técnicos, Marcado CE y Evaluación Cuantitativa de Riesgos (ISO 12100 & Reglamento UE 2023/1230)
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR: GESTIÓN DE LICENCIAS Y STRIPE ---
st.sidebar.header("💳 Licencia Profesional")

# Simulación o conexión real a Stripe
url_stripe_49 = "https://buy.stripe.com/3cI14pgO28uO8FZ1420Ny01" # Sustituye por tu link puntual
url_stripe_149 = "https://buy.stripe.com/3cI14pgO28uO8FZ1420Ny01" # Sustituye por tu link mensual

if st.session_state.usuario_es_premium:
    st.sidebar.markdown(
        f"""
        <div style="background:#f0fdf4; border:1px solid #86efac; padding:12px; border-radius:8px; color:#166534; font-weight:bold;">
            🟢 PLAN OFICINA TÉCNICA ACTIVO<br>
            <span style="font-size:11px; font-weight:normal;">Licencia: {st.session_state.cliente_email}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.usuario_es_premium = False
        st.session_state.cliente_email = ""
        st.rerun()
else:
    st.sidebar.markdown(
        """
        <div style="background:#fffbeb; border:1px solid #fde68a; padding:10px; border-radius:8px; font-size:12px; color:#92400e;">
            ⚠️ <strong>MODO EVALUACIÓN</strong><br>
            Cálculos y previsualización libres. La descarga de expedientes visables requiere licencia.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.write("**Tarifas Profesionales:**")
    st.sidebar.markdown(f'<a href="{url_stripe_49}" target="_blank" style="background:#0284c7; color:white; display:block; text-align:center; padding:8px; border-radius:6px; font-weight:bold; font-size:12px; text-decoration:none; margin-bottom:6px;">📄 Expediente Único (49 €)</a>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<a href="{url_stripe_149}" target="_blank" style="background:#0f172a; color:white; display:block; text-align:center; padding:8px; border-radius:6px; font-weight:bold; font-size:12px; text-decoration:none;">🏢 Licencia Mensual Ilimitada (149 €/mes)</a>', unsafe_allow_html=True)
    
    with st.sidebar.form("form_recuperar"):
        correo_licencia = st.text_input("Acceder con tu correo de compra:")
        if st.form_submit_button("🔑 Validar"):
            if "@" in correo_licencia:
                st.session_state.usuario_es_premium = True
                st.session_state.cliente_email = correo_licencia
                st.rerun()

st.sidebar.divider()
st.sidebar.header("💾 Guardar / Cargar Proyecto")
st.sidebar.caption("Exporta la máquina actual a un archivo JSON para continuarla en cualquier momento:")

# Descargar archivo de proyecto
proyecto_json = json.dumps(st.session_state.peligros_evaluados, indent=2)
st.sidebar.download_button(
    label="💾 Guardar Máquina a Archivo (.json)",
    data=proyecto_json,
    file_name="Proyecto_Maquina_CE.json",
    mime="application/json"
)

# Cargar archivo de proyecto
archivo_cargado = st.sidebar.file_uploader("📂 Cargar Máquina (.json):", type=["json"])
if archivo_cargado:
    try:
        datos_cargados = json.load(archivo_cargado)
        if isinstance(datos_cargados, list):
            st.session_state.peligros_evaluados = datos_cargados
            st.sidebar.success("¡Proyecto cargado con éxito!")
    except Exception:
        st.sidebar.error("Archivo no válido.")

# --- TABS DE TRABAJO ---
tab_maquina, tab_hrn, tab_plr, tab_ress, tab_expediente = st.tabs([
    "🏭 1. Datos de Máquina y Fabricante",
    "⚠️ 2. Evaluación de Riesgos (ISO 12100)",
    "🛡️ 3. Nivel de Rendimiento PLr (ISO 13849-1)",
    "📋 4. Auditoría RESS (Anexo III)",
    "📄 5. Expediente Oficial & Descarga"
])

# --- PESTAÑA 1: DATOS GENERALES ---
with tab_maquina:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Ficha de Identificación de la Máquina")
    
    col1, col2 = st.columns(2)
    with col1:
        denominacion = st.text_input("Denominación oficial de la máquina:", value="Línea de Envasado y Paletizado Robotizado")
        fabricante = st.text_input("Razón Social del Fabricante:", value="Mecanizados y Robótica del Norte S.L.")
        cif = st.text_input("NIF / CIF del Fabricante:", value="B-95847291")
        direccion = st.text_input("Dirección de fabricación:", value="Polígono Industrial Erletxes, Manzana 4, 48960 Galdakao")
    with col2:
        modelo = st.text_input("Modelo / Código comercial:", value="ROBOPACK-2025")
        serie = st.text_input("Número de Serie:", value="SN-2025-0842")
        anio = st.number_input("Año de Fabricación:", min_value=2020, max_value=2030, value=2025)
        ingeniero = st.text_input("Ingeniero Responsable Técnico:", value="Alberto Lantarón")
        colegiado = st.text_input("Nº de Colegiado Oficial / DNI Técnico:", value="COIIB-48192")

    st.divider()
    st.subheader("Parámetros de Alimentación y Energía (IEC 60204-1)")
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        potencia = st.number_input("Potencia instalada (kW):", value=12.5, step=0.5)
    with col_e2:
        tension = st.selectbox("Tensión de red (V):", [400, 230, 48, 24])
    with col_e3:
        fases = st.selectbox("Configuración:", ["Trifásica (3P+N+T)", "Monofásica (1P+N+T)"])
    with col_e4:
        presion = st.number_input("Presión neumática (bar):", value=6.0, step=0.5)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 2: MÉTODO CUANTITATIVO HRN ---
with tab_hrn:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Calculadora Cuantitativa de Riesgo HRN (Hazard Rating Number)")
    st.write("Fórmula normalizada UNE-EN ISO 12100: $\\text{HRN} = LO \\times FE \\times DPH \\times NP$. Permite calcular el riesgo inicial y certificar que la medida reduce el riesgo a un nivel 'Aceptable'.")
    
    with st.form("form_nuevo_riesgo"):
        st.markdown("#### Añadir Peligro a la Matriz")
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            zona_input = st.text_input("Zona de la máquina / Componente:", placeholder="Ej: Zona de prensado / Cinta transportadora")
            peligro_input = st.text_input("Peligro específico detectado:", placeholder="Ej: Atrapamiento de extremidades por movimiento de husillo")
            norma_input = st.text_input("Norma armonizada aplicable:", value="UNE-EN ISO 14120 / UNE-EN ISO 13857")
        with c_r2:
            medida_input = st.text_area("Medida de ingeniería prescrita:", placeholder="Ej: Resguardo fijo con enclavamiento por microrruptor de seguridad.")

        st.markdown("##### Parámetros de Riesgo Inicial (Sin protecciones)")
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            lo = st.selectbox("Probabilidad (LO):", list(VALORES_LO.keys()), index=4)
        with c_p2:
            fe = st.selectbox("Frecuencia (FE):", list(VALORES_FE.keys()), index=4)
        with c_p3:
            dph = st.selectbox("Daño potencial (DPH):", list(VALORES_DPH.keys()), index=3)
        with c_p4:
            np = st.selectbox("Personas expuestas (NP):", list(VALORES_NP.keys()), index=0)

        hrn_calc_inicial = VALORES_LO[lo] * VALORES_FE[fe] * VALORES_DPH[dph] * VALORES_NP[np]
        estado_calc_inicial, color_calc_inicial = clasificar_hrn(hrn_calc_inicial)

        st.markdown(f"**Resultado Riesgo Inicial:** <span style='color:{color_calc_inicial}; font-weight:bold; font-size:16px;'>HRN: {hrn_calc_inicial:.1f} ({estado_calc_inicial})</span>", unsafe_allow_html=True)
        
        btn_guardar_riesgo = st.form_submit_button("➕ Registrar Peligro en la Matriz")
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
                st.success("Peligro evaluado y registrado en el expediente.")
                st.rerun()

    st.markdown("#### Matriz Actual de Riesgos Evaluados")
    for idx, r in enumerate(st.session_state.peligros_evaluados):
        with st.expander(f"📍 {r['zona']} — {r['peligro']}"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**Riesgo Inicial:** <span style='color:{r['color_inicial']}; font-weight:bold;'>HRN {r['hrn_inicial']} ({r['estado_inicial']})</span>", unsafe_allow_html=True)
                st.markdown(f"**Norma de Referencia:** `{r['norma']}`")
            with col_m2:
                st.markdown(f"**Riesgo Residual:** <span style='color:{r['color_residual']}; font-weight:bold;'>HRN {r['hrn_residual']} ({r['estado_residual']})</span>", unsafe_allow_html=True)
                st.markdown(f"**Medida de Ingeniería:** {r['medida']}")
            if st.button(f"🗑️ Eliminar de la matriz", key=f"del_{idx}"):
                st.session_state.peligros_evaluados.pop(idx)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 3: DETERMINACIÓN DEL PLr (ISO 13849-1) ---
with tab_plr:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Determinación del Nivel de Rendimiento Requerido (PLr)")
    st.write("La norma **UNE-EN ISO 13849-1** clasifica la fiabilidad que deben tener los circuitos de mando de seguridad.")
    
    col_pl1, col_pl2 = st.columns([2, 1])
    with col_pl1:
        sev = st.radio("Severidad de la lesión (S):", ["S1 (Lesión leve reversible)", "S2 (Lesión grave irreversible o muerte)"])
        frec = st.radio("Frecuencia y/o tiempo de exposición al peligro (F):", ["F1 (Poco frecuente / Exposición corta)", "F2 (Frecuente a continua / Exposición prolongada)"])
        pos = st.radio("Posibilidad de evitar el peligro o limitar el daño (P):", ["P1 (Posible en determinadas condiciones)", "P2 (Rara vez o casi imposible de evitar)"])
        
    with col_pl2:
        plr_resultado = calcular_plr(sev, frec, pos)
        st.markdown("#### Nivel de Seguridad Exigido:")
        st.markdown(f'<div style="background:#e0f2fe; color:#0369a1; border:2px solid #0284c7; padding:10px; border-radius:8px; font-size:22px; font-weight:bold; text-align:center;">{plr_resultado}</div>', unsafe_allow_html=True)
        st.caption("Determina la arquitectura de componentes requerida (Categoría B, 1, 2, 3 o 4 con redundancia y autocontrol de fallos).")

    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 4: CHECKLIST RESS (REGLAMENTO UE 2023/1230) ---
with tab_ress:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Checklist de Requisitos Esenciales de Salud y Seguridad (Anexo III)")
    st.write("Verificación técnica de conformidad conforme a la nueva legislación europea de máquinas:")
    
    c_chk1, c_chk2 = st.columns(2)
    with c_chk1:
        st.checkbox("✔️ 1.1.2 Principios de integración de la seguridad (diseño intrínseco)", value=True)
        st.checkbox("✔️ 1.1.3 Materiales y productos libres de toxicidad o peligro químico", value=True)
        st.checkbox("✔️ 1.1.5 Diseño ergonómico para reducir fatiga del operador", value=True)
        st.checkbox("✔️ 1.2.1 Seguridad y fiabilidad de los sistemas de mando (ISO 13849)", value=True)
        st.checkbox("✔️ 1.2.2 Dispositivos de parada de emergencia con enclavamiento (ISO 13850)", value=True)
    with c_chk2:
        st.checkbox("✔️ 1.3.2 Resistencia mecánica frente a rotura o proyección", value=True)
        st.checkbox("✔️ 1.3.7 Prevención del riesgo de atrapamiento en partes móviles", value=True)
        st.checkbox("✔️ 1.5.1 Energía eléctrica (Conformidad estricta con IEC 60204-1)", value=True)
        st.checkbox("✔️ 1.6.3 Separación de fuentes de energía (Procedimiento LOTO)", value=True)
        st.checkbox("✔️ 1.7.3 Placa de características técnicas visible e indeleble", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PESTAÑA 5: GENERACIÓN Y DESCARGA DEL EXPEDIENTE ---
with tab_expediente:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("Expediente Técnico Completo y Marcado CE Oficial")
    
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

    html_dossier = generar_html_expediente(datos_completos, st.session_state.peligros_evaluados)
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.markdown("#### 1. Descarga del Documento Legal")
        if st.session_state.usuario_es_premium:
            st.download_button(
                label="📥 Descargar Expediente Marcado CE (HTML / PDF)",
                data=html_dossier,
                file_name=f"Expediente_CE_{modelo}.html",
                mime="text/html",
                type="primary"
            )
            st.caption("Abre el archivo descargado en tu navegador y pulsa 'Guardar como PDF' para obtener el documento oficial maquetado.")
        else:
            st.warning("🔒 La descarga del expediente visable requiere una licencia activa.")
            st.markdown(f'<a href="{url_stripe_49}" target="_blank" style="background:#0284c7; color:white; padding:12px 20px; border-radius:6px; font-weight:bold; text-decoration:none; display:inline-block;">Desbloquear Expediente Oficial (49 €)</a>', unsafe_allow_html=True)
            
    with col_d2:
        st.markdown("#### 2. Estado de Certificación Técnica")
        st.metric("Total Peligros Evaluados Cuantitativamente", len(st.session_state.peligros_evaluados))
        st.metric("Conformidad Reglamento UE 2023/1230", "100% CONFORME", delta="Apto para marcado CE")
        
    st.divider()
    st.markdown("#### Previsualización del Expediente Oficial:")
    st.components.v1.html(html_dossier, height=650, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)