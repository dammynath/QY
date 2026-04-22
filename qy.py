import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import io

# ------------------------------------------------------------
# 1. Page configuration
# ------------------------------------------------------------
st.set_page_config(page_title="Quantum Yield Calculator", layout="wide")
st.title("🌟 Quantum Yield Calculator (Comparative Method)")
st.markdown("Upload absorbance and fluorescence spectra for a **reference** (e.g., Rhodamine 6G) and your **sample** (quantum dot).")

# ------------------------------------------------------------
# 2. Solvent refractive indices (at room temperature, ~589 nm)
# ------------------------------------------------------------
solvent_ri = {
    "Water": 1.333,
    "Ethanol": 1.361,
    "Methanol": 1.329,
    "DMSO": 1.479,
    "DMF": 1.430,
    "Acetone": 1.359,
    "Toluene": 1.496,
    "Chloroform": 1.446,
    "Hexane": 1.375,
    "Custom": 1.000   # user can enter value
}

# ------------------------------------------------------------
# 3. Helper functions (with defensive checks)
# ------------------------------------------------------------
def load_file(uploaded_file):
    """Load CSV or Excel file into a pandas DataFrame. Return None if invalid."""
    if uploaded_file is None:
        return None
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        if df.shape[1] < 2:
            st.error("File must have at least two columns (wavelength, value).")
            return None
        
        # Rename columns for consistency
        df.columns = ['wavelength', 'value'] + list(df.columns[2:])
        df = df[['wavelength', 'value']].dropna()
        
        if df.empty:
            st.error("File contains no valid data after removing missing values.")
            return None
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def get_value_at_wavelength(df, target_wl, kind='linear'):
    """Interpolate value at exact wavelength. Return None if df is None or empty."""
    if df is None or df.empty:
        return None
    wl = df['wavelength'].values
    val = df['value'].values
    # Sort by wavelength
    idx = np.argsort(wl)
    wl = wl[idx]
    val = val[idx]
    f = interp1d(wl, val, kind=kind, fill_value='extrapolate')
    return float(f(target_wl))

def integrate_spectrum(df, wl_range, baseline_method='constant', baseline_region=None):
    """
    Integrate PL spectrum over wl_range (start, end) in nm.
    baseline_method: 'constant' (subtract mean over baseline_region), 'linear', or 'none'.
    Return None if df is None or empty.
    """
    if df is None or df.empty:
        return None
    wl = df['wavelength'].values
    intensity = df['value'].values
    
    # Baseline correction
    if baseline_method == 'constant' and baseline_region:
        mask = (wl >= baseline_region[0]) & (wl <= baseline_region[1])
        if np.any(mask):
            baseline = np.mean(intensity[mask])
            intensity = intensity - baseline
    elif baseline_method == 'linear' and baseline_region:
        mask = (wl >= baseline_region[0]) & (wl <= baseline_region[1])
        if np.sum(mask) >= 2:
            p = np.polyfit(wl[mask], intensity[mask], 1)
            baseline_line = np.polyval(p, wl)
            intensity = intensity - baseline_line
    
    # Restrict to integration range
    mask = (wl >= wl_range[0]) & (wl <= wl_range[1])
    if not np.any(mask):
        return 0.0
    wl_sel = wl[mask]
    int_sel = intensity[mask]
    # Trapezoidal integration
    area = np.trapz(int_sel, wl_sel)
    return area

def compute_fwhm(df, wl_range, baseline_method='constant', baseline_region=None):
    """
    Compute peak wavelength and FWHM of the PL spectrum.
    Returns (peak_wavelength, fwhm) in nm. Returns (None, None) if df is invalid.
    """
    if df is None or df.empty:
        return None, None
    wl = df['wavelength'].values
    intensity = df['value'].values
    
    # Apply same baseline correction as for integration
    if baseline_method == 'constant' and baseline_region:
        mask = (wl >= baseline_region[0]) & (wl <= baseline_region[1])
        if np.any(mask):
            baseline = np.mean(intensity[mask])
            intensity = intensity - baseline
    elif baseline_method == 'linear' and baseline_region:
        mask = (wl >= baseline_region[0]) & (wl <= baseline_region[1])
        if np.sum(mask) >= 2:
            p = np.polyfit(wl[mask], intensity[mask], 1)
            baseline_line = np.polyval(p, wl)
            intensity = intensity - baseline_line
    
    # Restrict to region of interest (avoid noise)
    mask_range = (wl >= wl_range[0]) & (wl <= wl_range[1])
    if not np.any(mask_range):
        return None, None
    wl_peak = wl[mask_range]
    int_peak = intensity[mask_range]
    
    # Find peak
    max_idx = np.argmax(int_peak)
    peak_wl = wl_peak[max_idx]
    max_int = int_peak[max_idx]
    
    # Find half maximum
    half_max = max_int / 2.0
    # Find indices where intensity crosses half_max on left and right
    left_idx = np.where(int_peak[:max_idx] <= half_max)[0]
    right_idx = np.where(int_peak[max_idx:] <= half_max)[0]
    
    if len(left_idx) == 0 or len(right_idx) == 0:
        return peak_wl, None
    
    left_cross = left_idx[-1]   # last index before peak where intensity <= half_max
    right_cross = right_idx[0] + max_idx
    
    # Interpolate for more precise FWHM
    # Left side
    if left_cross < len(wl_peak)-1:
        wl1 = wl_peak[left_cross]
        wl2 = wl_peak[left_cross+1]
        int1 = int_peak[left_cross]
        int2 = int_peak[left_cross+1]
        if int2 != int1:
            frac = (half_max - int1) / (int2 - int1)
            left_wl = wl1 + frac * (wl2 - wl1)
        else:
            left_wl = wl1
    else:
        left_wl = wl_peak[left_cross]
    
    # Right side
    if right_cross < len(wl_peak)-1:
        wl1 = wl_peak[right_cross]
        wl2 = wl_peak[right_cross+1]
        int1 = int_peak[right_cross]
        int2 = int_peak[right_cross+1]
        if int2 != int1:
            frac = (half_max - int1) / (int2 - int1)
            right_wl = wl1 + frac * (wl2 - wl1)
        else:
            right_wl = wl1
    else:
        right_wl = wl_peak[right_cross]
    
    fwhm = right_wl - left_wl
    return peak_wl, fwhm

# ------------------------------------------------------------
# 4. Sidebar: global parameters
# ------------------------------------------------------------
st.sidebar.header("⚙️ Measurement Parameters")
ex_wl = st.sidebar.number_input("Excitation wavelength (nm)", value=500.0, step=1.0)
int_range = st.sidebar.slider("Integration wavelength range (nm)", 300, 900, (500, 800), step=5)
baseline_method = st.sidebar.selectbox("Baseline correction", ["constant", "linear", "none"])
baseline_start = st.sidebar.number_input("Baseline region start (nm)", value=450.0)
baseline_end = st.sidebar.number_input("Baseline region end (nm)", value=470.0)
baseline_region = (baseline_start, baseline_end) if baseline_method != "none" else None

ref_qy = st.sidebar.number_input("Reference quantum yield (e.g., R6G in ethanol)", value=0.95, step=0.01)

st.sidebar.subheader("Solvent Refractive Indices")
ref_solvent = st.sidebar.selectbox("Reference solvent", list(solvent_ri.keys()), index=1)  # Ethanol default
sample_solvent = st.sidebar.selectbox("Sample solvent", list(solvent_ri.keys()), index=0)  # Water default

if ref_solvent == "Custom":
    ref_ri = st.sidebar.number_input("Reference solvent RI", value=1.361)
else:
    ref_ri = solvent_ri[ref_solvent]

if sample_solvent == "Custom":
    sample_ri = st.sidebar.number_input("Sample solvent RI", value=1.333)
else:
    sample_ri = solvent_ri[sample_solvent]

# ------------------------------------------------------------
# 5. File uploads for Reference
# ------------------------------------------------------------
st.header("📘 Reference (e.g., Rhodamine 6G)")
col1, col2 = st.columns(2)
with col1:
    ref_abs_file = st.file_uploader("Upload Reference Absorbance", type=["csv", "xlsx"], key="ref_abs")
with col2:
    ref_pl_file = st.file_uploader("Upload Reference PL spectrum", type=["csv", "xlsx"], key="ref_pl")

# ------------------------------------------------------------
# 6. File uploads for Sample (Quantum Dot)
# ------------------------------------------------------------
st.header("🔬 Sample (Quantum Dot)")
col3, col4 = st.columns(2)
with col3:
    sample_abs_file = st.file_uploader("Upload Sample Absorbance", type=["csv", "xlsx"], key="sample_abs")
with col4:
    sample_pl_file = st.file_uploader("Upload Sample PL spectrum", type=["csv", "xlsx"], key="sample_pl")

# ------------------------------------------------------------
# 7. Process data and compute (with defensive checks)
# ------------------------------------------------------------
if ref_abs_file and ref_pl_file and sample_abs_file and sample_pl_file:
    
    # Load all data
    ref_abs_df = load_file(ref_abs_file)
    ref_pl_df = load_file(ref_pl_file)
    sample_abs_df = load_file(sample_abs_file)
    sample_pl_df = load_file(sample_pl_file)
    
    # Check that all DataFrames are valid (not None)
    if any(df is None for df in [ref_abs_df, ref_pl_df, sample_abs_df, sample_pl_df]):
        st.error("One or more files could not be loaded. Please check file formats and content.")
        st.stop()
    
    # Get absorbance at excitation wavelength
    A_ref = get_value_at_wavelength(ref_abs_df, ex_wl)
    A_sample = get_value_at_wavelength(sample_abs_df, ex_wl)
    
    if A_ref is None or A_sample is None:
        st.error(f"Could not interpolate absorbance at {ex_wl} nm. Check your absorbance files.")
        st.stop()
    
    # Integrate PL spectra
    I_ref = integrate_spectrum(ref_pl_df, int_range, baseline_method, baseline_region)
    I_sample = integrate_spectrum(sample_pl_df, int_range, baseline_method, baseline_region)
    
    if I_ref is None or I_sample is None:
        st.error("Integration failed. Check PL files and range.")
        st.stop()
    
    # Compute FWHM and peak wavelength for sample PL
    peak_wl, fwhm = compute_fwhm(sample_pl_df, int_range, baseline_method, baseline_region)
    
    # Quantum yield calculation
    ri_corr = (sample_ri / ref_ri) ** 2
    qy = ref_qy * (I_sample / I_ref) * (A_ref / A_sample) * ri_corr
    
    # --------------------------------------------------------
    # 8. Display results
    # --------------------------------------------------------
    st.header("📊 Results")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Reference Absorbance", f"{A_ref:.5f}")
    col_res2.metric("Sample Absorbance", f"{A_sample:.5f}")
    col_res3.metric("Refractive Index Correction", f"{ri_corr:.4f}")
    
    col_res4, col_res5, col_res6 = st.columns(3)
    col_res4.metric("Reference Integrated Area", f"{I_ref:.2f}")
    col_res5.metric("Sample Integrated Area", f"{I_sample:.2f}")
    col_res6.metric("Sample PL Peak (nm)", f"{peak_wl:.1f}" if peak_wl else "N/A")
    
    col_res7, col_res8 = st.columns(2)
    col_res7.metric("Sample FWHM (nm)", f"{fwhm:.1f}" if fwhm else "N/A")
    col_res8.metric("Quantum Yield", f"{qy:.4f}  ({qy*100:.2f}%)")
    
    # --------------------------------------------------------
    # 9. Plotting
    # --------------------------------------------------------
    st.subheader("📈 Spectra")
    
    # Create subplots
    fig = make_subplots(rows=2, cols=2, 
                        subplot_titles=("Reference Absorbance", "Reference PL", 
                                        "Sample Absorbance", "Sample PL"))
    
    # Reference Absorbance
    fig.add_trace(go.Scatter(x=ref_abs_df['wavelength'], y=ref_abs_df['value'], 
                             mode='lines', name='Ref Abs'), row=1, col=1)
    fig.add_vline(x=ex_wl, line_dash="dash", line_color="red", row=1, col=1)
    
    # Reference PL
    fig.add_trace(go.Scatter(x=ref_pl_df['wavelength'], y=ref_pl_df['value'], 
                             mode='lines', name='Ref PL'), row=1, col=2)
    fig.add_vrect(x0=int_range[0], x1=int_range[1], fillcolor="gray", opacity=0.2, 
                  line_width=0, row=1, col=2)
    
    # Sample Absorbance
    fig.add_trace(go.Scatter(x=sample_abs_df['wavelength'], y=sample_abs_df['value'], 
                             mode='lines', name='Sample Abs'), row=2, col=1)
    fig.add_vline(x=ex_wl, line_dash="dash", line_color="red", row=2, col=1)
    
    # Sample PL
    fig.add_trace(go.Scatter(x=sample_pl_df['wavelength'], y=sample_pl_df['value'], 
                             mode='lines', name='Sample PL'), row=2, col=2)
    fig.add_vrect(x0=int_range[0], x1=int_range[1], fillcolor="gray", opacity=0.2, 
                  line_width=0, row=2, col=2)
    if peak_wl:
        fig.add_vline(x=peak_wl, line_dash="dash", line_color="green", row=2, col=2)
    
    fig.update_layout(height=800, showlegend=False)
    fig.update_xaxes(title_text="Wavelength (nm)", row=1, col=1)
    fig.update_xaxes(title_text="Wavelength (nm)", row=1, col=2)
    fig.update_xaxes(title_text="Wavelength (nm)", row=2, col=1)
    fig.update_xaxes(title_text="Wavelength (nm)", row=2, col=2)
    fig.update_yaxes(title_text="Absorbance", row=1, col=1)
    fig.update_yaxes(title_text="Intensity (a.u.)", row=1, col=2)
    fig.update_yaxes(title_text="Absorbance", row=2, col=1)
    fig.update_yaxes(title_text="Intensity (a.u.)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --------------------------------------------------------
    # 10. Download results
    # --------------------------------------------------------
    results_df = pd.DataFrame({
        "Parameter": ["Excitation wavelength (nm)", "Integration range (nm)", 
                      "Baseline method", "Baseline region (nm)",
                      "Reference QY", "Reference solvent (RI)", "Sample solvent (RI)",
                      "A_ref", "A_sample", "I_ref", "I_sample", 
                      "Refractive index correction", "Sample PL peak (nm)", "Sample FWHM (nm)",
                      "Quantum yield"],
        "Value": [ex_wl, f"{int_range[0]}–{int_range[1]}", 
                  baseline_method, f"{baseline_region[0]}–{baseline_region[1]}" if baseline_region else "None",
                  ref_qy, f"{ref_solvent} ({ref_ri:.3f})", f"{sample_solvent} ({sample_ri:.3f})",
                  f"{A_ref:.5f}", f"{A_sample:.5f}", f"{I_ref:.2f}", f"{I_sample:.2f}",
                  f"{ri_corr:.4f}", f"{peak_wl:.1f}" if peak_wl else "N/A", 
                  f"{fwhm:.1f}" if fwhm else "N/A", f"{qy:.4f} ({qy*100:.2f}%)"]
    })
    
    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download results as CSV", data=csv, 
                       file_name="quantum_yield_results.csv", mime="text/csv")
    
else:
    st.info("👈 Please upload all four files (absorbance and PL for both reference and sample) to begin calculation.")

# ------------------------------------------------------------
# 11. Footer
# ------------------------------------------------------------
st.markdown("---")
st.markdown("Developed for quantum yield determination using the comparative method. Ensure that all spectra are measured under identical instrument settings and that the reference's quantum yield is known at the chosen excitation wavelength.")
