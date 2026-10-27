# ⚙️ SafeMachine CE | Software de Marcado CE & Directiva de Máquinas

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)
[![Normativa](https://img.shields.io/badge/Normativa-Reglamento%20(UE)%202023%2F1230-green.svg)](https://eur-lex.europa.eu/)

Plataforma de ingeniería industrial diseñada para automatizar la **Evaluación Cuantitativa de Riesgos** y la elaboración íntegra del **Expediente Técnico de Construcción** y la **Declaración UE de Conformidad**, conforme a la legislación europea obligatoria para la puesta en servicio y comercialización de maquinaria.

---

## 🎯 Marco Normativo de Aplicación
El software implementa de forma determinista los estándares armonizados exigidos en la Unión Europea:
* **Reglamento (UE) 2023/1230** del Parlamento Europeo y del Consejo relativo a las máquinas.
* **UNE-EN ISO 12100:2012:** Seguridad de las máquinas. Principios generales para el diseño. Evaluación del riesgo y reducción del riesgo.
* **UNE-EN ISO 13849-1:** Seguridad de las máquinas. Partes de los sistemas de mando relativas a la seguridad (Cálculo del $PL_r$).
* **UNE-EN 60204-1:2019:** Seguridad de las máquinas. Equipo eléctrico de las máquinas.
* **UNE-EN ISO 13850:** Función de parada de emergencia. Principios para el diseño.

---

## 🚀 Metodología y Capacidades Técnicas

1. **Evaluación Cuantitativa de Riesgos (Método HRN - Hazard Rating Number):**
   Implementación del cálculo matemático normalizado:
   $$\text{HRN} = \text{LO} \times \text{FE} \times \text{DPH} \times \text{NP}$$
   * Cálculo del **Riesgo Inicial** frente a peligros mecánicos, eléctricos y térmicos.
   * Prescripción técnica de resguardos y enclavamientos según distancias de seguridad (ISO 13857).
   * Verificación obligatoria del **Riesgo Residual** aceptable.

2. **Determinación del Performance Level ($PL_r$):**
   Clasificación del nivel de fiabilidad requerido para los circuitos de mando según severidad ($S$), frecuencia de exposición ($F$) y posibilidad de evasión ($P$).

3. **Generación de Entregables Oficiales (PDF):**
   * **Expediente Técnico de Construcción** con marcado CE vectorial.
   * **Declaración UE de Conformidad** oficial lista para firma de Ingeniero Colegiado y Representante Legal.
   * **Placa de características técnicas** obligatoria para troquelado y remachado en bastidor (Art. 16).

---

## 💻 Instalación y Ejecución en Local

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/safemachine-ce.git

# Entrar a la carpeta
cd safemachine-ce

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run streamlit_app.py
