# 🔬 Quantum Yield Calculator (Comparative Method)

A **Streamlit** web application for determining the fluorescence quantum yield (QY) of quantum dots or other fluorophores using the comparative method.  
The app integrates absorbance and photoluminescence (PL) spectra, applies baseline correction, and calculates the QY with full solvent refractive index correction.

## ✨ Features

- Upload absorbance and PL spectra (Excel or CSV) for **reference** (e.g., Rhodamine 6G) and **sample** (quantum dot)
- Automatic interpolation of absorbance at the chosen excitation wavelength
- Integration of PL spectra over a user‑defined wavelength range
- Baseline correction (constant offset or linear) using a non‑emissive region
- Calculation of **peak wavelength** and **FWHM** of the sample’s PL spectrum
- Built‑in refractive indices for common solvents (water, ethanol, methanol, DMSO, DMF, acetone, toluene, chloroform, hexane) – custom RI also allowed
- Interactive plots (Plotly) with zoom, pan, and hover
- Download results as a CSV file

## 📦 Requirements

Install the dependencies listed in `requirements.txt`.  
We recommend using a Python virtual environment (Python ≥ 3.8).

## 🚀 Quick Start

1. **Clone or download** this repository.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt