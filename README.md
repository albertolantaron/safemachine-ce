# ⚙️ SafeMachine CE | Automated Machinery Safety & CE Marking Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live%20App-FF4B4B.svg)](https://safemachine-ce.streamlit.app)
[![Compliance](https://img.shields.io/badge/EU%20Regulation-2023%2F1230-emerald.svg)](https://eur-lex.europa.eu/)
[![ISO Standard](https://img.shields.io/badge/ISO-12100%20%7C%2013849--1-blue.svg)](https://www.iso.org/)

An enterprise-grade **Legal Engineering & Machinery Safety platform** designed to automate **Quantitative Risk Assessments (ISO 12100)** and compile official **Technical Construction Files** and **EU Declarations of Conformity** pursuant to the mandatory European Machinery Regulation **(EU) 2023/1230**.

---

### 🚀 [Try the Live Web Application Here](https://safemachine-ce.streamlit.app)

---

## 🎯 European Regulatory Framework
SafeMachine CE deterministically implements harmonized European and international safety standards required for the legal placing of industrial machinery on the EU market:

* **Regulation (EU) 2023/1230** of the European Parliament and of the Council on machinery.
* **EN ISO 12100:2012:** Safety of machinery — General principles for design — Risk assessment and risk reduction.
* **EN ISO 13849-1:** Safety of machinery — Safety-related parts of control systems (Calculation of $PL_r$).
* **EN 60204-1:2019:** Safety of machinery — Electrical equipment of machines.
* **EN ISO 13850:** Safety of machinery — Emergency stop function — Principles for design.
* **EN ISO 13857:** Safety distances to prevent hazard zones being reached by upper and lower limbs.

---

## 🔬 Core Engineering Capabilities

### 1. Quantitative Risk Assessment (HRN Method - ISO 12100)
Implements the standardized mathematical formula:
$$\text{HRN} = \text{LO} \times \text{FE} \times \text{DPH} \times \text{NP}$$
* **LO (Likelihood of Occurrence):** Evaluates hazard probability.
* **FE (Frequency of Exposure):** Quantifies operator exposure intervals.
* **DPH (Degree of Possible Harm):** Assesses injury severity from scratch to fatality.
* **NP (Number of Persons at Risk):** Weighs exposure headcounts.
* Automatically verifies that residual risk drops to **"Acceptable"** following the prescription of engineering controls (interlocked guarding, light curtains, emergency trips).

### 2. Determination of Required Performance Level ($PL_r$)
Calculates the required reliability for safety-related control circuits (Categories B, 1, 2, 3, or 4) based on:
* **Severity of injury ($S_1 / S_2$)**
* **Frequency and time of exposure ($F_1 / F_2$)**
* **Possibility of avoiding hazard ($P_1 / P_2$)**

### 3. Automated Official Deliverables
* **Technical Construction File (Expediente Técnico de Construcción):** Comprehensive legal dossier including electrical (EN 60204-1), pneumatic, and operational specs.
* **EU Declaration of Conformity:** Formal document ready for Chartered Engineer and Legal Representative sign-off.
* **Metallic Nameplate Generator:** Dimensional layout and compliance specs for indelible chassis marking (Article 16 & Annex III).

---

## 💻 Local Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/albertolantaron/safemachine-ce.git

# 2. Enter directory
cd safemachine-ce

# 3. Install requirements
pip install -r requirements.txt

# 4. Run application
streamlit run streamlit_app.py
