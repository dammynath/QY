# Quantum Yield Calculator – Documentation

## 3. Input File Format

All uploaded files (absorbance and PL) must be in CSV or Excel (.xlsx) format and contain exactly two columns:

| Column 1 | Column 2 |
|----------|----------|
| Wavelength (nm) | Absorbance (a.u.) or Fluorescence Intensity (a.u.) |

- The first column is assumed to be wavelength.
- The second column is the measured value.
- Headers are optional but recommended (e.g., "Wavelength", "Intensity").

**Example CSV:**
```csv
Wavelength,Intensity
500,123.4
501,156.7
502,198.2

3. Input File Format
All uploaded files (absorbance and PL) must be in CSV or Excel (.xlsx) format and contain exactly two columns:

Column 1	Column 2
Wavelength (nm)	Absorbance (a.u.) or Fluorescence Intensity (a.u.)
The first column is assumed to be wavelength.

The second column is the measured value.

Headers are optional but recommended (e.g., "Wavelength", "Intensity").

Example CSV:

csv
Wavelength,Intensity
500,123.4
501,156.7
502,198.2
4. How to Use the App
Step 1 – Set parameters in the sidebar
Parameter	Description
Excitation wavelength (nm)	The wavelength at which both reference and sample were excited. Must be identical for both.
Integration range (nm)	Wavelength range over which the PL spectra will be integrated (e.g., 500–800 nm). Should cover the entire emission peak.
Baseline correction	constant – subtracts the average intensity in a non-emissive region.
linear – subtracts a linear fit through the baseline region.
none – no correction.
Baseline region (nm)	Wavelength interval where no fluorescence occurs (e.g., 450–470 nm). Used for constant/linear baseline.
Reference quantum yield	Literature QY of the reference at the chosen excitation wavelength (e.g., 0.95 for Rhodamine 6G in ethanol).
Reference solvent	Solvent of the reference solution (affects refractive index correction).
Sample solvent	Solvent of the sample solution.
Step 2 – Upload the four required files
Reference absorbance (e.g., Rhodamine 6G in ethanol)

Reference PL spectrum (same reference, same excitation)

Sample absorbance (quantum dot in its solvent)

Sample PL spectrum (same excitation)

Step 3 – View results
The app displays:

Absorbance values at the excitation wavelength

Integrated PL areas (corrected)

Sample PL peak wavelength and FWHM

Refractive index correction factor

Final quantum yield (as decimal and percentage)

Step 4 – Download results
Click the "Download results as CSV" button to save all parameters and calculated values.

5. Calculation Formula
The quantum yield of the sample is given by:


Where:

Φ
sample
Φ 
sample
​
  = Quantum yield of the sample (to be determined)

Φ
ref
Φ 
ref
​
  = Quantum yield of the reference (known, e.g., 0.95)

I
sample
I 
sample
​
  = Integrated fluorescence intensity of the sample (area under corrected PL spectrum)

I
ref
I 
ref
​
  = Integrated fluorescence intensity of the reference

A
sample
A 
sample
​
  = Absorbance of the sample at the excitation wavelength

A
ref
A 
ref
​
  = Absorbance of the reference at the excitation wavelength

n
sample
n 
sample
​
  = Refractive index of the sample’s solvent

n
ref
n 
ref
​
  = Refractive index of the reference’s solvent

Important: The integrated intensity I must be obtained from baseline-corrected spectra, and the same integration range must be used for both sample and reference.

6. Solvent Refractive Indices (Built-in)
Solvent	Refractive Index (at ~589 nm, 20°C)
Water	1.333
Ethanol	1.361
Methanol	1.329
DMSO	1.479
DMF	1.430
Acetone	1.359
Toluene	1.496
Chloroform	1.446
Hexane	1.375
Custom	User-defined value
If your solvent is not listed, select "Custom" and enter its refractive index.

7. Important Precautions for Accurate QY
7.1 Absorbance (Optical Density)
Keep absorbance at the excitation wavelength ≤ 0.05 for both reference and sample. Higher absorbance causes inner-filter effects (reabsorption of emitted light and attenuation of the excitation beam).

If absorbance is too high, dilute the solution and re-measure.

7.2 Instrument Settings
Use identical settings for reference and sample:

Excitation and emission slit widths (bandwidth)

Detector gain / voltage

Integration time / scan speed

Same cuvette type (path length, material – quartz for UV/Vis)

Measure both samples in the same session to avoid lamp drift.

7.3 Baseline Correction
Choose a baseline region where the sample has no fluorescence (e.g., below the excitation wavelength or far above the emission peak).

The same baseline method and region must be applied to both reference and sample spectra.

For samples with very broad emission (like many quantum dots), ensure the baseline region is truly free of emission.

7.4 Integration Range
The integration range must fully cover the emission peak of both reference and sample.

Avoid including regions with strong Raman scattering or second-order diffraction artefacts (e.g., >700 nm for excitation at 500 nm).

The app allows you to set the range visually – verify that the shaded area in the PL plots correctly captures the entire emission.

7.5 Reference Quantum Yield
Use a reference whose QY is well-established for your exact excitation wavelength and solvent.

Common references:

Rhodamine 6G in ethanol: QY = 0.95 (at 488–550 nm)

Quinine sulfate in 0.1 M H₂SO₄: QY = 0.546 (at 350 nm)

Fluorescein in 0.1 M NaOH: QY = 0.95 (at 490 nm)

If possible, validate your setup by measuring a secondary reference before using the app.

7.6 Temperature
Fluorescence quantum yields can be temperature-dependent.

Perform measurements at a controlled temperature (e.g., 20–25°C) and ensure both samples are equilibrated.

7.7 Degassing (Optional)
Dissolved oxygen can quench fluorescence, especially for organic dyes.

For highest accuracy, degas solutions with argon or nitrogen before measurement.

7.8 Scattering (Important for Quantum Dots)
Quantum dots can scatter excitation light, which may be misinterpreted as emission.

Check your PL spectrum: if there is a sharp peak at the excitation wavelength (Rayleigh scatter) or at twice the excitation wavelength (Raman), consider using a long-pass filter or subtract a blank of the solvent.

The app does not automatically correct for scattering – user vigilance is required.

8. Interpreting Results
A quantum yield cannot exceed 1 (100%) in theory. Values above 1 indicate measurement errors (e.g., too high absorbance, mismatched integration ranges, or incorrect reference QY).

For quantum dots, typical QY values range from 10% to 90% depending on material, size, and surface passivation.

If the calculated QY is >1.1, re-check:

Absorbance values (should be ≤0.05)

Baseline correction (was the baseline region correctly chosen?)

Integration range (does it include all emission?)

Reference QY (is it correct for your excitation wavelength?)

9. Troubleshooting
Problem	Possible Solution
App cannot read file	Ensure file is CSV or XLSX with two columns. No extra sheets.
Absorbance interpolation fails	Check that the absorbance file contains the exact excitation wavelength, or data points close enough for interpolation.
Integrated area is zero	The integration range may not cover any emission. Extend the range.
Negative area after baseline correction	The baseline region may be higher than the emission signal. Choose a flatter, truly non-emissive region.
FWHM not calculated	The PL peak may be too weak or the baseline correction removed too much signal. Try a narrower integration range or a different baseline method.
QY > 100%	Likely absorbance too high or reference QY overestimated. Dilute sample and re-measure.
10. Example Workflow
Prepare solutions:

Reference: Rhodamine 6G in ethanol, diluted to A ≈ 0.04 at 500 nm.

Sample: Quantum dots in water, diluted to A ≈ 0.03 at 500 nm.

Measure spectra (same instrument settings):

Absorbance: 300–800 nm for both.

PL: Excitation at 500 nm, emission scan 500–800 nm.

Upload files to the app in the correct slots.

Set parameters:

Excitation = 500 nm

Integration = 500–750 nm

Baseline region = 450–470 nm (no emission)

Baseline method = constant

Reference QY = 0.95

Reference solvent = Ethanol, Sample solvent = Water

The app computes and displays the QY.

Download results for your report.

11. References
Lakowicz, J. R. (2006). Principles of Fluorescence Spectroscopy, 3rd ed. Springer.

Brouwer, A. M. (2011). Standards for photoluminescence quantum yield measurements in solution. Pure Appl. Chem., 83(12), 2213–2228.

Würth, C., Grabolle, M., Pauli, J., Spieles, M., & Resch-Genger, U. (2013). Relative and absolute determination of fluorescence quantum yields of transparent samples. Nat. Protoc., 8(8), 1535–1550.

12. License & Credits
This software is released under the MIT License (see LICENSE file). Developed for research and educational use. Contributions are welcome.

For questions, please open an issue on the GitHub repository.