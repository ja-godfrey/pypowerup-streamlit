# PowerUp! Streamlit

A Streamlit web application implementation of **PowerUp!** - the power analysis tool for experimental and quasi-experimental designs.

This app is designed to closely match the layout and functionality of the original PowerUp! Excel spreadsheet (`powerup.xlsm`), providing the same parameter organization, calculation flow, and design coverage in a modern web interface.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-green.svg)](LICENSE)

## Overview

PowerUp! is primarily designed to aide in the a priori power analysis calculation of:

- **Minimum Detectable Effect Size (MDES)** - The smallest true effect that can be detected with specified power
- **Minimum Required Sample Size (MRSS)** - The sample size needed to detect a given effect size
- **Statistical Power** - The probability of detecting a true effect

### Key Features

- **Excel-like Layout**: Parameter organization matches the original spreadsheet
- **All 21 Designs Supported**: Complete coverage of experimental and quasi-experimental designs
- **Three Calculation Modes**: MDES, Sample Size, and Power calculations
- **Computed Values Display**: Shows M (Multiplier), T1, T2, and degrees of freedom like the Excel version
- **Sensitivity Analysis**: Generate power curves and MDES curves
- **Interactive Parameters**: Yellow-highlighted input fields just like the Excel version

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/pypowerup-streamlit.git
cd pypowerup-streamlit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Supported Designs (21 Total)

The app supports the same designs as the original Excel spreadsheet, organized by category:

### 1. Individual Random Assignment (IRA)
| Model | Name | Description |
|-------|------|-------------|
| 1.0 | IRA | Simple Individual Random Assignment—Completely Randomized Controlled Trials |

### 2. Blocked Individual Random Assignment (BIRA)
| Model | Name | Description |
|-------|------|-------------|
| 2.1 | BIRA2_1c | 2-Level Constant Effects—Individuals Randomized within Blocks |
| 2.2 | BIRA2_1f | 2-Level Fixed Effects—Individuals Randomized within Blocks |
| 2.3 | BIRA2_1r | 2-Level Random Effects—Individuals Randomized within Blocks |
| 2.4 | BIRA3_1r | 3-Level Random Effects—Individuals Randomized within Blocks |
| 2.5 | BIRA4_1r | 4-Level Random Effects—Individuals Randomized within Blocks |

### 3. Simple Cluster Random Assignment (CRA)
| Model | Name | Description |
|-------|------|-------------|
| 3.1 | CRA2_2r | Two-Level Cluster RA—Treatment at Level 2 |
| 3.2 | CRA3_3r | Three-Level Cluster RA—Treatment at Level 3 |
| 3.3 | CRA4_4r | Four-Level Cluster RA—Treatment at Level 4 |

### 4. Blocked Cluster Random Assignment (BCRA)
| Model | Name | Description |
|-------|------|-------------|
| 4.1 | BCRA3_2f | 3-Level Fixed Effects—Treatment at Level 2 |
| 4.2 | BCRA3_2r | 3-Level Random Effects—Treatment at Level 2 |
| 4.3 | BCRA4_2r | 4-Level Random Effects—Treatment at Level 2 |
| 4.4 | BCRA4_3f | 4-Level Fixed Effects—Treatment at Level 3 |
| 4.5 | BCRA4_3r | 4-Level Random Effects—Treatment at Level 3 |

### 5. Regression Discontinuity (RD)
| Model | Name | Description |
|-------|------|-------------|
| 5.1 | RD2_1f | 2-Level Fixed Effects RD |
| 5.2 | RD2_1r | 2-Level Random Effects RD |
| 5.3 | RDC_2r | 2-Level Cluster RD—Treatment at Level 2 |
| 5.4 | RDC_3r | 3-Level Cluster RD—Treatment at Level 3 |
| 5.5 | RD3_2f | 3-Level Fixed Effects Blocked RD |

### 6. Interrupted Time-Series (ITS)
| Model | Name | Description |
|-------|------|-------------|
| 6.0a | ITS (No Comparison) | ITS without comparison units |
| 6.0b | ITS (With Comparison) | ITS with comparison units |

## Parameter Reference

Parameters are organized to match the Excel spreadsheet order:

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| α (Alpha) | Probability of Type I error | 0.01 - 0.10 |
| Two-tailed | 2 = two-tailed, 1 = one-tailed | 1 or 2 |
| Power (1-β) | Statistical power | 0.70 - 0.95 |
| ρ (ICC) | Intraclass correlation | 0.01 - 0.50 |
| ω (Omega) | Treatment effect heterogeneity | 0.01 - 0.50 |
| P | Proportion in treatment | 0.30 - 0.70 |
| R² | Variance explained by covariates | 0 - 0.90 |
| g* | Number of covariates | 0 - 20 |
| n | Level 1 sample size | 10 - 1000 |
| J | Level 2 units | 2 - 500 |
| K | Level 3 units | 2 - 200 |
| L | Level 4 units | 2 - 100 |

## Comparison with Excel Version

| Feature | Excel (powerup.xlsm) | Streamlit App |
|---------|---------------------|---------------|
| Parameter layout | Tabular with yellow cells | Matching layout with highlighted inputs |
| Computed values | M, T1, T2 displayed | Same values displayed |
| Design selection | Sheet tabs | Sidebar dropdown |
| Calculations | Automatic in cells | Click "Calculate" button |
| Sensitivity analysis | Manual | Built-in curve generation |

## Files

- `app.py` - Main Streamlit application
- `powerup.xlsm` - Original Excel spreadsheet (for reference)
- `pypowerup/` - Python library implementing the calculations
- `requirements.txt` - Python dependencies

## References

This tool is based on:

> Dong, N. & Maynard, R. A. (2013). PowerUp!: A tool for calculating minimum detectable effect sizes and minimum required sample sizes for experimental and quasi-experimental design studies, *Journal of Research on Educational Effectiveness*, 6(1), 24-67. doi: 10.1080/19345747.2012.673143.

### Related Resources
- [Original PowerUp! Excel Tool](https://www.causalevaluation.org/)
- [PyPowerUp Documentation](https://pypowerup.readthedocs.io/)
- [PowerUpR (R Package)](https://CRAN.R-project.org/package=PowerUpR)

## Authors

**Original PowerUp! Tool**: Nianbo Dong, Rebecca Maynard

**PyPowerUp Python Package**: Sophia Man Yang, Nianbo Dong, Rebecca Maynard

**Streamlit Interface**: Wrapper created to match Excel functionality

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
