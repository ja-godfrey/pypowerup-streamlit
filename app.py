"""
PyPowerUp Streamlit App
A Streamlit interface for pypowerup - Power analysis tool for 
experimental and quasi-experimental designs.

Designed to match the layout of the original PowerUp! Excel spreadsheet.

Based on: Dong, N. & Maynard, R. A. (2013). PowerUp!: A Tool for Calculating 
Minimum Detectable Effect Sizes and Minimum Required Sample Sizes for 
Experimental and Quasi-experimental Design Studies.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import io
from datetime import datetime
from pypowerup import effect_size, power, sample_size
from scipy import stats

# Page configuration
st.set_page_config(
    page_title="PowerUp! - Power Analysis Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match Excel-like appearance
st.markdown("""
<style>
    .main-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1a5276;
        margin-bottom: 0.5rem;
        padding: 10px;
        background-color: #d4e6f1;
        border-radius: 5px;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a5276;
        background-color: #aed6f1;
        padding: 8px 12px;
        margin: 10px 0;
        border-radius: 3px;
    }
    .result-box {
        background-color: #d5f5e3;
        border: 2px solid #27ae60;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        text-align: center;
        color: #111111 !important;
    }
    .result-label {
        font-size: 1rem;
        color: #1e8449 !important;
        font-weight: 600;
    }
    .result-value {
        font-size: 2rem;
        color: #145a32 !important;
        font-weight: 700;
    }
    .result-box div {
        color: #444444 !important;
    }
    .computed-box {
        background-color: #fdebd0;
        border: 1px solid #f39c12;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #111111 !important;
    }
    .computed-box p, .computed-box strong, .computed-box code {
        color: #111111 !important;
    }
    .note-box {
        background-color: #fcf3cf;
        border-left: 4px solid #f1c40f;
        padding: 10px 15px;
        margin: 15px 0;
        font-style: italic;
        color: #111111 !important;
    }
    .helper-box {
        background-color: #e8f6f3;
        border: 1px solid #1abc9c;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #111111 !important;
    }
    .stNumberInput > div > div > input {
        background-color: #fffde7 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DESIGN CONFIGURATIONS - Following Excel spreadsheet order exactly
# ============================================================================

DESIGNS = {
    # 1.0 Individual Random Assignment
    "ira": {
        "number": "1.0",
        "name": "IRA",
        "full_name": "MDES Calculator for Individual Random Assignment (IRA) Designs—Completely Randomized Controlled Trials",
        "category": "Individual Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "p", "r21", "g", "n"],
        "sample_size_for": "n",
        "has_rho_ts": False,
    },
    # 2.1 - 2.5 Blocked Individual Random Assignment
    "bira2_1c": {
        "number": "2.1",
        "name": "BIRA2_1c",
        "full_name": "MDES Calculator for 2-Level Constant Effects Blocked Individual Random Assignment (BIRA2_1c) Designs—Individuals Randomized within Blocks",
        "category": "Blocked Individual Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "p", "r21", "g", "n", "J"],
        "sample_size_for": "J",
        "has_rho_ts": False,
    },
    "bira2_1f": {
        "number": "2.2",
        "name": "BIRA2_1f",
        "full_name": "MDES Calculator for 2-Level Fixed Effects Blocked Individual Random Assignment (BIRA2_1f) Designs—Individuals Randomized within Blocks",
        "category": "Blocked Individual Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "p", "r21", "g", "n", "J"],
        "sample_size_for": "J",
        "has_rho_ts": False,
    },
    "bira2_1r": {
        "number": "2.3",
        "name": "BIRA2_1r",
        "full_name": "MDES Calculator for 2-Level Random Effects Blocked Individual Random Assignment (BIRA2_1r) Designs—Individuals Randomized within Blocks",
        "category": "Blocked Individual Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho2", "omega2", "p", "r21", "r2t2", "g", "n", "J"],
        "sample_size_for": "J",
        "has_rho_ts": False,
    },
    "bira3_1r": {
        "number": "2.4",
        "name": "BIRA3_1r",
        "full_name": "MDES Calculator for 3-Level Random Effects Blocked Individual Random Assignment (BIRA3_1r) Designs—Individuals Randomized within Blocks",
        "category": "Blocked Individual Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho3", "rho2", "omega3", "omega2", "p", "r21", "r2t2", "r2t3", "g", "n", "J", "K"],
        "sample_size_for": "K",
        "has_rho_ts": False,
    },
    "bira4_1r": {
        "number": "2.5",
        "name": "BIRA4_1r",
        "full_name": "MDES Calculator for 4-Level Random Effects Blocked Individual Random Assignment (BIRA4_1r) Designs—Individuals Randomized within Blocks",
        "category": "Blocked Individual Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho4", "rho3", "rho2", "omega4", "omega3", "omega2", "p", "r21", "r2t2", "r2t3", "r2t4", "g", "n", "J", "K", "L"],
        "sample_size_for": "L",
        "has_rho_ts": False,
    },
    # 3.1 - 3.3 Simple Cluster Random Assignment
    "cra2_2r": {
        "number": "3.1",
        "name": "CRA2_2r",
        "full_name": "MDES Calculator for Two-Level Cluster Random Assignment Design (CRA2_2r)—Treatment at Level 2",
        "category": "Simple Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho2", "p", "r21", "r22", "g", "n", "J"],
        "sample_size_for": "J",
        "has_rho_ts": False,
    },
    "cra3_3r": {
        "number": "3.2",
        "name": "CRA3_3r",
        "full_name": "MDES Calculator for Three-Level Cluster Random Assignment Design (CRA3_3r)—Treatment at Level 3",
        "category": "Simple Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho3", "rho2", "p", "r21", "r22", "r23", "g", "n", "J", "K"],
        "sample_size_for": "K",
        "has_rho_ts": False,
    },
    "cra4_4r": {
        "number": "3.3",
        "name": "CRA4_4r",
        "full_name": "MDES Calculator for Four-Level Cluster Random Assignment Design (CRA4_4r)—Treatment at Level 4",
        "category": "Simple Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho4", "rho3", "rho2", "p", "r21", "r22", "r23", "r24", "g", "n", "J", "K", "L"],
        "sample_size_for": "L",
        "has_rho_ts": False,
    },
    # 4.1 - 4.5 Blocked Cluster Random Assignment
    "bcra3_2f": {
        "number": "4.1",
        "name": "BCRA3_2f",
        "full_name": "MDES Calculator for 3-Level Fixed Effects Blocked Cluster Random Assignment Designs (BCRA3_2f)—Treatment at Level 2",
        "category": "Blocked Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho2", "p", "r21", "r22", "g", "n", "J", "K"],
        "sample_size_for": "K",
        "has_rho_ts": False,
    },
    "bcra3_2r": {
        "number": "4.2",
        "name": "BCRA3_2r",
        "full_name": "MDES Calculator for 3-Level Random Effects Blocked Cluster Random Assignment Designs (BCRA3_2r)—Treatment at Level 2",
        "category": "Blocked Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho3", "rho2", "omega3", "p", "r21", "r22", "r2t3", "g", "n", "J", "K"],
        "sample_size_for": "K",
        "has_rho_ts": False,
    },
    "bcra4_2r": {
        "number": "4.3",
        "name": "BCRA4_2r",
        "full_name": "MDES Calculator for 4-Level Random Effects Blocked Cluster Random Assignment Designs (BCRA4_2r)—Treatment at Level 2",
        "category": "Blocked Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho4", "rho3", "rho2", "omega4", "omega3", "p", "r21", "r22", "r2t3", "r2t4", "g", "n", "J", "K", "L"],
        "sample_size_for": "L",
        "has_rho_ts": False,
    },
    "bcra4_3f": {
        "number": "4.4",
        "name": "BCRA4_3f",
        "full_name": "MDES Calculator for 4-Level Fixed Effects Blocked Cluster Random Assignment Designs (BCRA4_3f)—Treatment at Level 3",
        "category": "Blocked Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho3", "rho2", "p", "r21", "r22", "r23", "g", "n", "J", "K", "L"],
        "sample_size_for": "L",
        "has_rho_ts": False,
    },
    "bcra4_3r": {
        "number": "4.5",
        "name": "BCRA4_3r",
        "full_name": "MDES Calculator for 4-Level Random Effects Blocked Cluster Random Assignment Designs (BCRA4_3r)—Treatment at Level 3",
        "category": "Blocked Cluster Random Assignment Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho4", "rho3", "rho2", "omega4", "p", "r21", "r22", "r23", "r2t4", "g", "n", "J", "K", "L"],
        "sample_size_for": "L",
        "has_rho_ts": False,
    },
    # 5.1 - 5.6 Regression Discontinuity
    "rd2_1f": {
        "number": "5.1",
        "name": "RD2_1f",
        "full_name": "MDES Calculator for 2-Level Fixed Effects Regression Discontinuity Design (RD2_1f)",
        "category": "Regression Discontinuity Designs",
        "params_order": ["alpha", "two_tailed", "power", "p", "r21", "g", "n", "J", "design_effect"],
        "sample_size_for": "J",
        "has_rho_ts": True,
    },
    "rd2_1r": {
        "number": "5.2",
        "name": "RD2_1r",
        "full_name": "MDES Calculator for 2-Level Regression Discontinuity Designs with Random Block Effects (RD2_1r)",
        "category": "Regression Discontinuity Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho2", "omega2", "p", "r21", "r2t2", "g", "n", "J", "design_effect"],
        "sample_size_for": "J",
        "has_rho_ts": True,
    },
    "rdc_2r": {
        "number": "5.3",
        "name": "RDC_2r",
        "full_name": "MDES Calculator for Two-Level Regression Discontinuity Designs (RDC_2r)—Treatment at Level 2",
        "category": "Regression Discontinuity Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho2", "p", "r21", "r22", "g", "n", "J", "design_effect"],
        "sample_size_for": "J",
        "has_rho_ts": True,
    },
    "rdc_3r": {
        "number": "5.4",
        "name": "RDC_3r",
        "full_name": "MDES Calculator for 3-Level Regression Discontinuity Designs (RDC_3r)—Treatment at Level 3",
        "category": "Regression Discontinuity Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho3", "rho2", "p", "r21", "r22", "r23", "g", "n", "J", "K", "design_effect"],
        "sample_size_for": "K",
        "has_rho_ts": True,
    },
    "rd3_2f": {
        "number": "5.5",
        "name": "RD3_2f",
        "full_name": "MDES Calculator for 3-Level Fixed Effects Blocked Regression Discontinuity Design (RD3_2f)—Treatment at Level 2",
        "category": "Regression Discontinuity Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho2", "p", "r21", "r22", "g", "n", "J", "K", "design_effect"],
        "sample_size_for": "K",
        "has_rho_ts": True,
    },
    # 6.0 Interrupted Time-Series
    "its": {
        "number": "6.0",
        "name": "ITS",
        "full_name": "MDES Calculator for 3-Level HLM Interrupted Time-Series Design (ITS): Studies with Random Cohort Effects and Constant Level-3 Effects",
        "category": "Interrupted Time-Series Designs",
        "params_order": ["alpha", "two_tailed", "power", "rho2", "T", "n", "K", "r22", "tf", "g", "q"],
        "sample_size_for": "K",
        "has_rho_ts": False,
        "is_its": True,
    },
}

# Parameter definitions with labels matching Excel exactly
PARAMS = {
    "alpha": {
        "label": "Alpha Level (α)",
        "comment": "Probability of a Type I error",
        "default": 0.05,
        "min": 0.001,
        "max": 0.20,
        "step": 0.01,
        "format": "%.3f",
    },
    "two_tailed": {
        "label": "Two-tailed or One-tailed Test?",
        "comment": "Enter 2 for two-tailed, 1 for one-tailed",
        "default": 2,
        "min": 1,
        "max": 2,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "power": {
        "label": "Power (1-β)",
        "comment": "Statistical power (1-probability of a Type II error)",
        "default": 0.80,
        "min": 0.10,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "es": {
        "label": "MRES = MDES",
        "comment": "Minimum Relevant Effect Size = Minimum Detectable Effect Size",
        "default": 0.25,
        "min": 0.01,
        "max": 2.0,
        "step": 0.01,
        "format": "%.3f",
    },
    "p": {
        "label": "P",
        "comment": "Proportion of sample randomized to treatment: nT / (nT + nC)",
        "default": 0.50,
        "min": 0.01,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "n": {
        "label": "n (Average Block/Cluster Size)",
        "comment": "Mean number of Level 1 units per Level 2 cluster (harmonic mean recommended)",
        "default": 55,
        "min": 1,
        "max": 100000,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "J": {
        "label": "J (Sample Size [# of Blocks])",
        "comment": "Number of Level 2 units in the sample",
        "default": 20,
        "min": 2,
        "max": 10000,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "K": {
        "label": "K (Sample Size [# of Level 3 units])",
        "comment": "Number of Level 3 units",
        "default": 20,
        "min": 2,
        "max": 10000,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "L": {
        "label": "L (Sample Size [# of Level 4 units])",
        "comment": "Number of Level 4 units",
        "default": 20,
        "min": 2,
        "max": 1000,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "g": {
        "label": "g*",
        "comment": "Number of covariates",
        "default": 1,
        "min": 0,
        "max": 50,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "r21": {
        "label": "R²₁",
        "comment": "Proportion of variance in Level 1 outcome explained by Block and Level 1 covariates",
        "default": 0.50,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "r22": {
        "label": "R²₂",
        "comment": "Proportion of variance in Level 2 outcome explained by Level 2 covariates",
        "default": 0.0,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "r23": {
        "label": "R²₃",
        "comment": "Proportion of variance in Level 3 outcome explained by Level 3 covariates",
        "default": 0.0,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "r24": {
        "label": "R²₄",
        "comment": "Proportion of variance in Level 4 outcome explained by Level 4 covariates",
        "default": 0.0,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "rho2": {
        "label": "ρ (ICC)",
        "comment": "Proportion of variance in outcome between clusters",
        "default": 0.15,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "rho3": {
        "label": "ρ₃ (ICC3)",
        "comment": "Proportion of variance among Level 3 units",
        "default": 0.15,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "rho4": {
        "label": "ρ₄ (ICC4)",
        "comment": "Proportion of variance among Level 4 units",
        "default": 0.05,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "omega2": {
        "label": "ω₂",
        "comment": "Treatment effect heterogeneity: variability in treatment effects across Level 2 units, standardized by Level-2 outcome variability",
        "default": 0.10,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "format": "%.2f",
    },
    "omega3": {
        "label": "ω₃",
        "comment": "Treatment effect heterogeneity: variability in treatment effects across Level 3 units, standardized by Level-3 outcome variability",
        "default": 0.50,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "format": "%.2f",
    },
    "omega4": {
        "label": "ω₄",
        "comment": "Treatment effect heterogeneity: variability in treatment effects across Level 4 units, standardized by Level-4 outcome variability",
        "default": 0.50,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
        "format": "%.2f",
    },
    "r2t2": {
        "label": "R²T₂",
        "comment": "Proportion of between block variance in treatment effect explained by Level 2 covariates",
        "default": 0.0,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "r2t3": {
        "label": "R²T₃",
        "comment": "Proportion of between block variance in treatment effect explained by Level 3 covariates",
        "default": 0.0,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "r2t4": {
        "label": "R²T₄",
        "comment": "Proportion of between block variance in treatment effect explained by Level 4 covariates",
        "default": 0.0,
        "min": 0.0,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
    "design_effect": {
        "label": "Design Effect",
        "comment": "Estimated from empirical data (see ρ_TS below) or based on other assumptions",
        "default": 2.75,
        "min": 1.0,
        "max": 10.0,
        "step": 0.01,
        "format": "%.2f",
    },
    "T": {
        "label": "T (number of baseline years)",
        "comment": "The number of years prior to intervention for which the baseline trend is established",
        "default": 5,
        "min": 2,
        "max": 50,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "tf": {
        "label": "tf (follow-up year of interest)",
        "comment": "Year in which outcomes are compared (0 = treatment year, 1 = first year after, etc.)",
        "default": 2,
        "min": 0,
        "max": 50,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "q": {
        "label": "Ratio of comparison units to experimental units (q)",
        "comment": "(# comparison schools / # program schools) at block level",
        "default": 2,
        "min": 1,
        "max": 100,
        "step": 1,
        "format": "%d",
        "is_int": True,
    },
    "rho_ts": {
        "label": "ρ_TS",
        "comment": "Correlation between TREATMENT indicator and the score that is used for treatment assignment",
        "default": 0.80,
        "min": 0.01,
        "max": 0.99,
        "step": 0.01,
        "format": "%.2f",
    },
}


def calculate_multiplier(alpha, power, df, two_tailed):
    """Calculate the M multiplier (same as Excel)."""
    if two_tailed == 2:
        alpha = alpha / 2
    t1 = stats.t.ppf(1 - alpha, df)
    t2 = abs(stats.t.ppf(1 - power, df))
    if power >= 0.5:
        m = t1 + t2
    else:
        m = t1 - t2
    return m, t1, t2


def get_df_for_design(design_id, params):
    """Get degrees of freedom for a design."""
    n = params.get("n", 30)
    J = params.get("J", 10)
    K = params.get("K", 10)
    L = params.get("L", 10)
    g = params.get("g", 0)
    T = params.get("T", 5)
    
    df_formulas = {
        "ira": n - g - 2,
        "bira2_1c": J * (n - 1) - g - 1,
        "bira2_1f": J * (n - 2) - g,
        "bira2_1r": J - g - 1,
        "bira3_1r": K - g - 1,
        "bira4_1r": L - g - 1,
        "cra2_2r": J - g - 2,
        "cra3_3r": K - g - 2,
        "cra4_4r": L - g - 2,
        "bcra3_2f": K * (J - 2) - g,
        "bcra3_2r": K - g - 1,
        "bcra4_2r": L - g - 1,
        "bcra4_3f": L * (K - 2) - g,
        "bcra4_3r": L - g - 1,
        "rd2_1f": J * (n - 2) - g,
        "rd2_1r": J - g - 1,
        "rdc_2r": J - g - 2,
        "rdc_3r": K - g - 2,
        "rd3_2f": K * (J - 1) - g,
        "its": K * T - g - 1,
    }
    return max(1, df_formulas.get(design_id, 10))


def estimate_design_effect(rho_ts):
    """Estimate design effect from rho_TS. Formula: 1 / (1 - rho_ts^2)"""
    if rho_ts >= 1:
        return float('inf')
    return 1 / (1 - rho_ts ** 2)


def create_export_data(result_data, design_info, computed_values):
    """Create a dictionary with all export data."""
    export = {
        "metadata": {
            "tool": "PowerUp! Streamlit",
            "generated_at": datetime.now().isoformat(),
            "design_model": design_info.get("number", ""),
            "design_name": design_info.get("name", ""),
            "calculation_type": result_data.get("mode", ""),
        },
        "result": {
            "type": result_data.get("label", ""),
            "value": result_data.get("value", 0),
        },
        "computed_values": computed_values,
        "parameters": result_data.get("params", {}),
    }
    
    # Add ITS comparison result if present
    if "value_with_comparison" in result_data:
        export["result"]["value_with_comparison"] = result_data["value_with_comparison"]
    
    return export


def export_to_csv(export_data):
    """Convert export data to CSV format."""
    rows = []
    
    # Metadata section
    rows.append(["=== POWERUP! RESULTS ===", ""])
    rows.append(["Generated", export_data["metadata"]["generated_at"]])
    rows.append(["Design Model", export_data["metadata"]["design_model"]])
    rows.append(["Design Name", export_data["metadata"]["design_name"]])
    rows.append(["Calculation Type", export_data["metadata"]["calculation_type"]])
    rows.append(["", ""])
    
    # Result section
    rows.append(["=== RESULT ===", ""])
    rows.append([export_data["result"]["type"], export_data["result"]["value"]])
    if "value_with_comparison" in export_data["result"]:
        rows.append(["MDES (with comparison)", export_data["result"]["value_with_comparison"]])
    rows.append(["", ""])
    
    # Computed values section
    rows.append(["=== COMPUTED VALUES ===", ""])
    for key, value in export_data["computed_values"].items():
        rows.append([key, value])
    rows.append(["", ""])
    
    # Parameters section
    rows.append(["=== PARAMETERS ===", ""])
    for key, value in export_data["parameters"].items():
        rows.append([key, value])
    
    df = pd.DataFrame(rows, columns=["Field", "Value"])
    return df.to_csv(index=False)


def export_to_json(export_data):
    """Convert export data to JSON format."""
    return json.dumps(export_data, indent=2, default=str)


def export_to_excel(export_data):
    """Convert export data to Excel format."""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = {
            "Field": ["Design Model", "Design Name", "Calculation Type", "Result Type", "Result Value", "Generated At"],
            "Value": [
                export_data["metadata"]["design_model"],
                export_data["metadata"]["design_name"],
                export_data["metadata"]["calculation_type"],
                export_data["result"]["type"],
                export_data["result"]["value"],
                export_data["metadata"]["generated_at"],
            ]
        }
        if "value_with_comparison" in export_data["result"]:
            summary_data["Field"].append("MDES (with comparison)")
            summary_data["Value"].append(export_data["result"]["value_with_comparison"])
        
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)
        
        # Parameters sheet
        params_data = {
            "Parameter": list(export_data["parameters"].keys()),
            "Value": list(export_data["parameters"].values())
        }
        pd.DataFrame(params_data).to_excel(writer, sheet_name="Parameters", index=False)
        
        # Computed values sheet
        computed_data = {
            "Metric": list(export_data["computed_values"].keys()),
            "Value": list(export_data["computed_values"].values())
        }
        pd.DataFrame(computed_data).to_excel(writer, sheet_name="Computed Values", index=False)
    
    return output.getvalue()


# LaTeX symbols for each parameter
PARAM_LATEX_SYMBOLS = {
    "alpha": r"\alpha",
    "two_tailed": r"t_{\text{tails}}",
    "power": r"1-\beta",
    "es": r"\delta",
    "p": r"P",
    "n": r"n",
    "J": r"J",
    "K": r"K",
    "L": r"L",
    "g": r"g^{*}",
    "r21": r"R^{2}_{1}",
    "r22": r"R^{2}_{2}",
    "r23": r"R^{2}_{3}",
    "r24": r"R^{2}_{4}",
    "rho2": r"\rho_{2}",
    "rho3": r"\rho_{3}",
    "rho4": r"\rho_{4}",
    "omega2": r"\omega_{2}",
    "omega3": r"\omega_{3}",
    "omega4": r"\omega_{4}",
    "r2t2": r"R^{2}_{T2}",
    "r2t3": r"R^{2}_{T3}",
    "r2t4": r"R^{2}_{T4}",
    "design_effect": r"\mathrm{DE}",
    "T": r"T",
    "tf": r"t_{f}",
    "q": r"q",
    "rho_ts": r"\rho_{TS}",
}

# Human-readable parameter descriptions for the academic paragraph
PARAM_PROSE = {
    "alpha": ("Type I error rate", "\\alpha = {val}"),
    "two_tailed": ("test direction", "{val}-tailed test"),
    "power": ("statistical power", "1{-}\\beta = {val}"),
    "es": ("effect size", "\\delta = {val}"),
    "p": ("treatment proportion", "P = {val}"),
    "n": ("Level-1 cluster size", "n = {val}"),
    "J": ("Level-2 units", "J = {val}"),
    "K": ("Level-3 units", "K = {val}"),
    "L": ("Level-4 units", "L = {val}"),
    "g": ("covariates", "g^{{*}} = {val}"),
    "r21": ("Level-1 R²", "R^{{2}}_{{1}} = {val}"),
    "r22": ("Level-2 R²", "R^{{2}}_{{2}} = {val}"),
    "r23": ("Level-3 R²", "R^{{2}}_{{3}} = {val}"),
    "r24": ("Level-4 R²", "R^{{2}}_{{4}} = {val}"),
    "rho2": ("Level-2 ICC", "\\rho_{{2}} = {val}"),
    "rho3": ("Level-3 ICC", "\\rho_{{3}} = {val}"),
    "rho4": ("Level-4 ICC", "\\rho_{{4}} = {val}"),
    "omega2": ("Level-2 treatment heterogeneity", "\\omega_{{2}} = {val}"),
    "omega3": ("Level-3 treatment heterogeneity", "\\omega_{{3}} = {val}"),
    "omega4": ("Level-4 treatment heterogeneity", "\\omega_{{4}} = {val}"),
    "r2t2": ("Level-2 treatment R²", "R^{{2}}_{{T2}} = {val}"),
    "r2t3": ("Level-3 treatment R²", "R^{{2}}_{{T3}} = {val}"),
    "r2t4": ("Level-4 treatment R²", "R^{{2}}_{{T4}} = {val}"),
    "design_effect": ("design effect", "\\mathrm{{DE}} = {val}"),
    "T": ("baseline periods", "T = {val}"),
    "tf": ("follow-up period", "t_f = {val}"),
    "q": ("comparison ratio", "q = {val}"),
    "rho_ts": ("treatment-score correlation", "\\rho_{{TS}} = {val}"),
}

RESULT_LATEX_LABELS = {
    "MDES": r"\delta_{\min}",
    "Power": r"1-\beta",
}


def export_to_latex(export_data):
    """Generate a publication-ready LaTeX table from export data."""
    meta = export_data["metadata"]
    result = export_data["result"]
    params = export_data["parameters"]
    computed = export_data["computed_values"]

    design_name = meta["design_name"]
    design_model = meta["design_model"]
    calc_type = meta["calculation_type"]

    # Determine result label symbol
    result_type = result["type"]
    if "MDES" in result_type or "Effect" in result_type:
        result_sym = r"\hat{\delta}_{\min}"
        result_full = "Minimum Detectable Effect Size"
    elif "Sample" in result_type or "Size" in result_type:
        result_sym = r"\hat{N}_{\min}"
        result_full = "Minimum Required Sample Size"
    else:
        result_sym = r"\hat{\pi}"
        result_full = "Statistical Power"

    def fmt_val(v):
        if isinstance(v, float):
            return f"{v:.4f}".rstrip("0").rstrip(".")
        return str(v)

    # Build parameter rows
    param_rows = []
    for pname, pval in params.items():
        sym = PARAM_LATEX_SYMBOLS.get(pname, pname)
        label = PARAMS[pname]["label"] if pname in PARAMS else pname
        param_rows.append(
            f"        & ${sym}$ & {label} & {fmt_val(pval)} \\\\"
        )
    param_block = "\n".join(param_rows)

    # Build computed rows
    m_val = fmt_val(computed.get("M (Multiplier)", ""))
    t1_val = fmt_val(computed.get("T1 (Precision)", ""))
    t2_val = fmt_val(computed.get("T2 (Power)", ""))
    df_val = fmt_val(computed.get("df", ""))

    result_val = fmt_val(result["value"])

    latex = rf"""\begin{{table}}[ht]
\centering
\caption{{Power Analysis Results: {design_name} (Model {design_model}) --- {calc_type}}}
\label{{tab:power-analysis-{design_name.lower()}}}
\begin{{tabular}}{{llll}}
\hline
\textbf{{Section}} & \textbf{{Symbol}} & \textbf{{Description}} & \textbf{{Value}} \\
\hline
\multicolumn{{4}}{{l}}{{\textit{{Input Parameters}}}} \\
{param_block}
\hline
\multicolumn{{4}}{{l}}{{\textit{{Computed Values}}}} \\
        & $M$ & Multiplier ($T_1 + T_2$) & {m_val} \\
        & $T_1$ & Critical value (precision) & {t1_val} \\
        & $T_2$ & Non-centrality value (power) & {t2_val} \\
        & $\nu$ & Degrees of freedom & {df_val} \\
\hline
\multicolumn{{4}}{{l}}{{\textit{{Result}}}} \\
        & ${result_sym}$ & {result_full} & \textbf{{{result_val}}} \\
\hline
\end{{tabular}}
\vspace{{4pt}}
\begin{{minipage}}{{\linewidth}}
\small\textit{{Note.}} Results computed using PyPowerUp! \citep{{dong2013powerup}}.
The design effect multiplier $M = T_1 + T_2$ where $T_1 = t_{{1-\alpha/k,\,\nu}}$
and $T_2 = t_{{1-\beta,\,\nu}}$ under a {("two" if params.get("two_tailed", 2) == 2 else "one")}-tailed
$t$-distribution with $\nu$ degrees of freedom.
\end{{minipage}}
\end{{table}}"""
    return latex


def generate_academic_paragraph(export_data):
    """Generate a copy-paste academic paragraph describing the power analysis."""
    meta = export_data["metadata"]
    result = export_data["result"]
    params = export_data["parameters"]
    computed = export_data["computed_values"]

    design_name = meta["design_name"]
    design_model = meta["design_model"]
    calc_type = meta["calculation_type"]

    alpha = params.get("alpha", 0.05)
    two_tailed = params.get("two_tailed", 2)
    power_val = params.get("power", 0.80)
    p = params.get("p", 0.50)
    g = params.get("g", 0)
    n = params.get("n")
    J = params.get("J")
    K = params.get("K")
    L = params.get("L")
    es = params.get("es")
    df = computed.get("df", "")
    result_val = result["value"]
    result_type = result["type"]

    tail_word = "two-tailed" if two_tailed == 2 else "one-tailed"
    alpha_str = f"\u03b1 = {alpha}"
    power_str = f"1\u2212\u03b2 = {power_val:.2f}"

    # Design-specific ICC / omega sentences
    icc_parts = []
    for lev, rho_key in [("Level 2", "rho2"), ("Level 3", "rho3"), ("Level 4", "rho4")]:
        v = params.get(rho_key)
        if v is not None:
            icc_parts.append(f"an intraclass correlation of \u03c1 = {v:.2f} at {lev}")
    for lev, om_key in [("Level 2", "omega2"), ("Level 3", "omega3"), ("Level 4", "omega4")]:
        v = params.get(om_key)
        if v is not None:
            icc_parts.append(
                f"treatment effect heterogeneity of \u03c9 = {v:.2f} at {lev}"
            )

    # R² sentence
    r2_parts = []
    for lab, key in [
        ("Level 1", "r21"), ("Level 2", "r22"), ("Level 3", "r23"), ("Level 4", "r24")
    ]:
        v = params.get(key)
        if v is not None and v > 0:
            r2_parts.append(f"R\u00b2 = {v:.2f} at {lab}")

    # Sample size sentence
    ss_parts = []
    if n is not None:
        ss_parts.append(f"n = {n} participants per cluster")
    if J is not None:
        ss_parts.append(f"J = {J} Level-2 units")
    if K is not None:
        ss_parts.append(f"K = {K} Level-3 units")
    if L is not None:
        ss_parts.append(f"L = {L} Level-4 units")

    # Result phrase
    if "MDES" in result_type or "Effect" in result_type:
        result_phrase = (
            f"the minimum detectable effect size was \u03b4 = {result_val:.4f} "
            f"(expressed as a standardized mean difference)"
        )
    elif "Sample" in result_type or "Size" in result_type:
        result_phrase = (
            f"the minimum required sample size was {int(round(result_val))} "
            f"{result_type.split('(')[0].strip().lower()} units"
        )
    else:
        result_phrase = f"the estimated statistical power was 1\u2212\u03b2 = {result_val:.4f}"

    # Assemble sentences
    sentences = []

    sentences.append(
        f"An a priori power analysis was conducted for a "
        f"{DESIGNS[meta['design_name'].lower()]['full_name'] if meta['design_name'].lower() in DESIGNS else design_name} "
        f"(Model {design_model}) to determine the {calc_type.lower()} "
        f"(Dong & Maynard, 2013; Godfrey, in press)."
    )

    test_sentence = (
        f"Assuming a {tail_word} test with {alpha_str} and {power_str}"
    )
    test_sentence += f", with {int(p * 100)}% of participants assigned to the treatment condition"
    if g > 0:
        test_sentence += f" and {g} covariate{'s' if g != 1 else ''} included in the model"
    test_sentence += "."
    sentences.append(test_sentence)

    if icc_parts:
        sentences.append(
            "The multilevel structure of the data was characterized by "
            + ", and ".join(icc_parts) + "."
        )

    if r2_parts:
        sentences.append(
            "Covariate variance explained was assumed to be " + ", ".join(r2_parts) + "."
        )

    if es is not None and "MDES" not in result_type and "Effect" not in result_type:
        sentences.append(
            f"The target minimum relevant effect size was set to \u03b4 = {es:.3f}."
        )

    if ss_parts:
        sentences.append(
            "The assumed sample allocation was " + ", ".join(ss_parts) + "."
        )

    sentences.append(
        f"Under these conditions, {result_phrase}. "
        f"The analysis used a {tail_word} $t$-distribution with \u03bd = {df} degrees of freedom, "
        f"yielding a multiplier of M = {computed.get('M (Multiplier)', ''):.2f} "
        f"(T\u2081 = {computed.get('T1 (Precision)', ''):.2f}, "
        f"T\u2082 = {computed.get('T2 (Power)', ''):.2f})."
    )

    return " ".join(sentences)


def render_download_buttons(export_data, key_suffix=""):
    """Render download buttons for CSV, JSON, Excel, and LaTeX."""
    st.markdown("---")
    st.markdown("**📥 Download Results**")

    col1, col2, col3, col4 = st.columns(4)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    design_name = export_data["metadata"]["design_name"]

    with col1:
        csv_data = export_to_csv(export_data)
        st.download_button(
            label="📄 CSV",
            data=csv_data,
            file_name=f"powerup_{design_name}_{timestamp}.csv",
            mime="text/csv",
            key=f"download_csv_{key_suffix}",
            use_container_width=True
        )

    with col2:
        json_data = export_to_json(export_data)
        st.download_button(
            label="📋 JSON",
            data=json_data,
            file_name=f"powerup_{design_name}_{timestamp}.json",
            mime="application/json",
            key=f"download_json_{key_suffix}",
            use_container_width=True
        )

    with col3:
        try:
            excel_data = export_to_excel(export_data)
            st.download_button(
                label="📊 Excel",
                data=excel_data,
                file_name=f"powerup_{design_name}_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_excel_{key_suffix}",
                use_container_width=True
            )
        except Exception:
            st.button(
                "📊 Excel (requires openpyxl)",
                disabled=True,
                key=f"download_excel_disabled_{key_suffix}",
                use_container_width=True,
            )

    with col4:
        latex_data = export_to_latex(export_data)
        st.download_button(
            label="📝 LaTeX",
            data=latex_data,
            file_name=f"powerup_{design_name}_{timestamp}.tex",
            mime="text/plain",
            key=f"download_latex_{key_suffix}",
            use_container_width=True,
        )

    # Academic paragraph
    st.markdown("---")
    st.markdown("**📖 Academic Write-Up**")
    st.caption(
        "Copy and paste this paragraph into your manuscript. "
        "Adjust sample description and covariates as appropriate for your study."
    )
    try:
        para = generate_academic_paragraph(export_data)
        st.text_area(
            label="Academic paragraph",
            value=para,
            height=200,
            label_visibility="collapsed",
            key=f"academic_para_{key_suffix}",
        )
    except Exception:
        st.info("Academic paragraph could not be generated for this design configuration.")



def main():
    # ========================================================================
    # SIDEBAR - Design Selection (like Excel Contents sheet)
    # ========================================================================
    with st.sidebar:
        st.markdown("### 📋 PowerUp! Models")
        st.markdown("---")
        
        # Calculation mode selection
        calc_mode = st.radio(
            "**Calculation Type**",
            ["MDES (Effect Size)", "Sample Size", "Power"],
            help="Select what you want to calculate"
        )
        
        st.markdown("---")
        
        # Design category selection
        categories = [
            "Individual Random Assignment Designs",
            "Blocked Individual Random Assignment Designs",
            "Simple Cluster Random Assignment Designs",
            "Blocked Cluster Random Assignment Designs",
            "Regression Discontinuity Designs",
            "Interrupted Time-Series Designs",
        ]
        
        selected_category = st.selectbox("**Design Category**", categories)
        
        # Filter designs by category
        category_designs = {k: v for k, v in DESIGNS.items() if v["category"] == selected_category}
        
        # Design selection
        design_options = list(category_designs.keys())
        design_labels = [f"{DESIGNS[d]['number']} {DESIGNS[d]['name']}" for d in design_options]
        
        selected_idx = st.selectbox(
            "**Select Design**",
            range(len(design_options)),
            format_func=lambda i: design_labels[i]
        )
        selected_design = design_options[selected_idx]
        
        st.markdown("---")
        st.markdown("### 📚 References")
        st.markdown("""
        Based on: Dong & Maynard (2013). *PowerUp!: A Tool for Calculating 
        MDES and Sample Sizes*. JREE, 6(1), 24-67.
        """)
    
    # ========================================================================
    # MAIN CONTENT - Parameter Input Form (like Excel worksheet)
    # ========================================================================
    design = DESIGNS[selected_design]
    
    # Title (like Excel Row 1)
    if calc_mode == "MDES (Effect Size)":
        title = f"Model {design['number']}: {design['full_name']}"
    elif calc_mode == "Sample Size":
        title = f"Model {design['number']}: Sample Size Calculator for {design['name']} Designs"
    else:
        title = f"Model {design['number']}: Power Calculator for {design['name']} Designs"
    
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    
    # Create two columns: Parameters and Results
    col_params, col_results = st.columns([3, 2])
    
    with col_params:
        # Assumptions header (like Excel Row 2)
        st.markdown('<div class="section-header">Assumptions &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Comments</div>', unsafe_allow_html=True)
        
        # Parameter inputs in a table-like format
        params_collected = {}
        
        # Get the parameter order for this design
        param_order = design["params_order"].copy()
        
        # For sample size mode, we need effect size instead of the sample size parameter
        if calc_mode == "Sample Size":
            ss_param = design["sample_size_for"]
            if ss_param in param_order:
                param_order.remove(ss_param)
            # Add effect size after power
            insert_idx = 0
            for i, p in enumerate(param_order):
                if p == "power":
                    insert_idx = i + 1
                    break
            param_order.insert(insert_idx, "es")
        
        # For power mode, remove power and add effect size
        if calc_mode == "Power":
            if "power" in param_order:
                power_idx = param_order.index("power")
                param_order.remove("power")
                param_order.insert(power_idx, "es")
        
        # Create parameter input table
        for param_name in param_order:
            if param_name not in PARAMS:
                continue
            
            param_def = PARAMS[param_name]
            
            col1, col2, col3 = st.columns([2, 1, 3])
            
            with col1:
                st.markdown(f"**{param_def['label']}**")
            
            with col2:
                if param_def.get("is_int"):
                    value = st.number_input(
                        param_def['label'],
                        min_value=int(param_def['min']),
                        max_value=int(param_def['max']),
                        value=int(param_def['default']),
                        step=int(param_def['step']),
                        key=f"param_{param_name}",
                        label_visibility="collapsed"
                    )
                else:
                    value = st.number_input(
                        param_def['label'],
                        min_value=float(param_def['min']),
                        max_value=float(param_def['max']),
                        value=float(param_def['default']),
                        step=float(param_def['step']),
                        format=param_def['format'],
                        key=f"param_{param_name}",
                        label_visibility="collapsed"
                    )
                params_collected[param_name] = value
            
            with col3:
                st.caption(param_def['comment'])
        
        # For RD designs, add the rho_TS helper section
        if design.get("has_rho_ts", False):
            st.markdown("---")
            st.markdown('<div class="helper-box">', unsafe_allow_html=True)
            st.markdown("**Design Effect Estimation Helper**")
            
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.markdown(f"**{PARAMS['rho_ts']['label']}**")
            with col2:
                rho_ts = st.number_input(
                    PARAMS['rho_ts']['label'],
                    min_value=0.01,
                    max_value=0.99,
                    value=0.80,
                    step=0.01,
                    format="%.2f",
                    key="param_rho_ts",
                    label_visibility="collapsed"
                )
            with col3:
                st.caption(PARAMS['rho_ts']['comment'])
            
            # Calculate and display estimated design effect
            est_de = estimate_design_effect(rho_ts)
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.markdown("**Estimated Design Effect**")
            with col2:
                st.markdown(f"**`{est_de:.4f}`**")
            with col3:
                st.caption("Estimated multiplier: 1 / (1 - ρ_TS²)")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Note box (like Excel note row)
        st.markdown("""
        <div class="note-box">
        <strong>Note:</strong> The parameters in the yellow cells need to be specified. 
        The result will be calculated automatically when you click "Calculate".
        </div>
        """, unsafe_allow_html=True)
    
    with col_results:
        st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)
        
        # Calculate button
        if st.button("🔬 **Calculate**", type="primary", use_container_width=True):
            try:
                # Prepare parameters for pypowerup
                pypowerup_params = {}
                
                # Convert two_tailed from 1/2 to True/False
                two_tailed_val = params_collected.get("two_tailed", 2) == 2
                pypowerup_params["two_tailed"] = two_tailed_val
                
                # Copy other parameters
                for k, v in params_collected.items():
                    if k == "two_tailed":
                        continue
                    pypowerup_params[k] = v
                
                # Special handling for ITS design
                is_its = design.get("is_its", False)
                
                # Calculate based on mode
                if calc_mode == "MDES (Effect Size)":
                    if is_its:
                        # Calculate both with and without comparison
                        params_no_compare = pypowerup_params.copy()
                        params_no_compare.pop("q", None)
                        result_no_compare = effect_size(design="its_nocompare", **params_no_compare)
                        
                        params_w_compare = pypowerup_params.copy()
                        result_w_compare = effect_size(design="its_wcompare", **params_w_compare)
                        
                        result_value = result_no_compare  # Primary result
                        result_w_compare_value = result_w_compare
                    else:
                        result_value = effect_size(design=selected_design, **pypowerup_params)
                    result_label = "MDES"
                    result_desc = "Minimum Detectable Effect Size"
                    
                elif calc_mode == "Sample Size":
                    if is_its:
                        params_no_compare = pypowerup_params.copy()
                        params_no_compare.pop("q", None)
                        result_value = sample_size(design="its_nocompare", **params_no_compare)
                    else:
                        result_value = sample_size(design=selected_design, **pypowerup_params)
                    result_label = f"{design['sample_size_for'].upper()} (Sample Size)"
                    result_desc = f"Minimum Required Sample Size ({design['sample_size_for'].upper()})"
                    
                else:  # Power
                    if is_its:
                        params_no_compare = pypowerup_params.copy()
                        params_no_compare.pop("q", None)
                        result_value = power(design="its_nocompare", **params_no_compare)
                    else:
                        result_value = power(design=selected_design, **pypowerup_params)
                    result_label = "Power"
                    result_desc = "Statistical Power"
                
                # Calculate intermediate values for display
                df = get_df_for_design(selected_design, params_collected)
                alpha_val = params_collected.get("alpha", 0.05)
                power_val = params_collected.get("power", 0.8)
                two_tailed_int = params_collected.get("two_tailed", 2)
                
                m, t1, t2 = calculate_multiplier(alpha_val, power_val, df, two_tailed_int)
                
                # Display computed values (like Excel)
                st.markdown('<div class="computed-box">', unsafe_allow_html=True)
                st.markdown("**Computed Values:**")
                
                comp_col1, comp_col2 = st.columns(2)
                with comp_col1:
                    st.markdown(f"**M (Multiplier):**")
                    st.markdown(f"**T₁ (Precision):**")
                    st.markdown(f"**T₂ (Power):**")
                with comp_col2:
                    st.markdown(f"`{m:.2f}`")
                    st.markdown(f"`{t1:.2f}`")
                    st.markdown(f"`{t2:.2f}`")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display main result
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-label">{result_label}</div>
                    <div class="result-value">{result_value:.4f}</div>
                    <div style="color:#444444; font-size:0.9rem;">{result_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # For ITS, show both results
                if is_its and calc_mode == "MDES (Effect Size)":
                    st.markdown(f"""
                    <div class="result-box" style="background-color: #fdf2e9; border-color: #e67e22;">
                        <div class="result-label" style="color: #d35400;">MDES (with comparison units)</div>
                        <div class="result-value" style="color: #873600;">{result_w_compare_value:.4f}</div>
                        <div style="color:#444444; font-size:0.9rem;">Using q={params_collected.get('q', 2)} comparison units per treatment</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Store result in session state
                result_store = {
                    'value': result_value,
                    'label': result_label,
                    'params': params_collected.copy(),
                    'design': selected_design,
                    'mode': calc_mode,
                    'computed': {'M (Multiplier)': m, 'T1 (Precision)': t1, 'T2 (Power)': t2, 'df': df}
                }
                if is_its and calc_mode == "MDES (Effect Size)":
                    result_store['value_with_comparison'] = result_w_compare_value
                
                st.session_state['last_result'] = result_store
                
                # Download buttons
                export_data = create_export_data(result_store, design, result_store['computed'])
                render_download_buttons(export_data, key_suffix="new")
                
            except Exception as e:
                st.error(f"Calculation Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        # Show previous result if exists
        elif 'last_result' in st.session_state:
            result = st.session_state['last_result']
            if result['design'] == selected_design and result['mode'] == calc_mode:
                st.info("Previous calculation result shown below. Click 'Calculate' to update.")
                
                # Recalculate intermediate values
                df = get_df_for_design(selected_design, result['params'])
                alpha_val = result['params'].get("alpha", 0.05)
                power_val = result['params'].get("power", 0.8)
                two_tailed_int = result['params'].get("two_tailed", 2)
                m, t1, t2 = calculate_multiplier(alpha_val, power_val, df, two_tailed_int)
                
                st.markdown('<div class="computed-box">', unsafe_allow_html=True)
                st.markdown("**Computed Values:**")
                comp_col1, comp_col2 = st.columns(2)
                with comp_col1:
                    st.markdown(f"**M (Multiplier):**")
                    st.markdown(f"**T₁ (Precision):**")
                    st.markdown(f"**T₂ (Power):**")
                with comp_col2:
                    st.markdown(f"`{m:.2f}`")
                    st.markdown(f"`{t1:.2f}`")
                    st.markdown(f"`{t2:.2f}`")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="result-box">
                    <div class="result-label">{result['label']}</div>
                    <div class="result-value">{result['value']:.4f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Download buttons for previous result
                computed_vals = result.get('computed', {'M (Multiplier)': m, 'T1 (Precision)': t1, 'T2 (Power)': t2, 'df': df})
                export_data = create_export_data(result, design, computed_vals)
                render_download_buttons(export_data, key_suffix="prev")
    
    # ========================================================================
    # SENSITIVITY ANALYSIS SECTION
    # ========================================================================
    st.markdown("---")
    st.markdown('<div class="section-header">📈 Sensitivity Analysis</div>', unsafe_allow_html=True)
    
    if 'last_result' in st.session_state and st.session_state['last_result']['design'] == selected_design:
        import plotly.graph_objects as go
        
        result = st.session_state['last_result']
        
        col_curve1, col_curve2 = st.columns(2)
        
        with col_curve1:
            st.markdown("**Power Curve**")
            
            # Determine which sample size parameter to vary
            ss_param = design["sample_size_for"]
            ss_label = PARAMS[ss_param]["label"]
            
            ss_range = st.slider(
                f"Range of {ss_param.upper()}",
                min_value=5,
                max_value=500,
                value=(10, 200),
                key="power_curve_range"
            )
            
            if st.button("Generate Power Curve", key="gen_power_curve"):
                with st.spinner("Generating..."):
                    x_vals = np.linspace(ss_range[0], ss_range[1], 40).astype(int)
                    y_vals = []
                    
                    base_params = result['params'].copy()
                    base_params["two_tailed"] = base_params.get("two_tailed", 2) == 2
                    
                    # Remove power if present, add es if not present
                    if "power" in base_params:
                        del base_params["power"]
                    if "es" not in base_params:
                        if result['mode'] == "MDES (Effect Size)":
                            base_params["es"] = result['value']
                        else:
                            base_params["es"] = 0.25
                    
                    design_key = "its_nocompare" if design.get("is_its") else selected_design
                    if design.get("is_its"):
                        base_params.pop("q", None)
                    
                    for x in x_vals:
                        try:
                            base_params[ss_param] = int(x)
                            pwr = power(design=design_key, **base_params)
                            y_vals.append(pwr)
                        except:
                            y_vals.append(None)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name='Power'))
                    fig.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Power = 0.80")
                    fig.update_layout(
                        xaxis_title=ss_label,
                        yaxis_title="Statistical Power",
                        yaxis_range=[0, 1],
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with col_curve2:
            st.markdown("**MDES Curve**")
            
            ss_param = design["sample_size_for"]
            
            mdes_range = st.slider(
                f"Range of {ss_param.upper()}",
                min_value=5,
                max_value=500,
                value=(10, 200),
                key="mdes_curve_range"
            )
            
            if st.button("Generate MDES Curve", key="gen_mdes_curve"):
                with st.spinner("Generating..."):
                    x_vals = np.linspace(mdes_range[0], mdes_range[1], 40).astype(int)
                    y_vals = []
                    
                    base_params = result['params'].copy()
                    base_params["two_tailed"] = base_params.get("two_tailed", 2) == 2
                    
                    # Remove es if present, ensure power is present
                    if "es" in base_params:
                        del base_params["es"]
                    if "power" not in base_params:
                        base_params["power"] = 0.8
                    
                    design_key = "its_nocompare" if design.get("is_its") else selected_design
                    if design.get("is_its"):
                        base_params.pop("q", None)
                    
                    for x in x_vals:
                        try:
                            base_params[ss_param] = int(x)
                            es_val = effect_size(design=design_key, **base_params)
                            y_vals.append(es_val)
                        except:
                            y_vals.append(None)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name='MDES', line=dict(color='green')))
                    fig.add_hline(y=0.2, line_dash="dash", line_color="blue", annotation_text="Small Effect (0.20)")
                    fig.add_hline(y=0.5, line_dash="dash", line_color="orange", annotation_text="Medium Effect (0.50)")
                    fig.update_layout(
                        xaxis_title=PARAMS[ss_param]["label"],
                        yaxis_title="Minimum Detectable Effect Size",
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run a calculation first to enable sensitivity analysis.")
    
    # ========================================================================
    # FOOTER - References (like Excel References sheet)
    # ========================================================================
    st.markdown("---")
    with st.expander("📚 About PowerUp! and References"):
        st.markdown("""
        ### About PowerUp!
        
        This tool is a Streamlit implementation of **PowerUp!**, originally developed as an Excel spreadsheet.
        
        PowerUp! is designed to aide in the a priori power analysis calculation of:
        - **Minimum Detectable Effect Size (MDES)** - The smallest effect that can be detected with specified power and sample size
        - **Minimum Required Sample Size (MRSS)** - The sample size needed to detect a specified effect with given power
        - **Statistical Power** - The probability of detecting a true effect given sample size and effect size
        
        ### Supported Designs (21 Total)
        
        | Category | # | Designs |
        |----------|---|---------|
        | Individual RA | 1 | IRA |
        | Blocked Individual RA | 5 | BIRA2_1c, BIRA2_1f, BIRA2_1r, BIRA3_1r, BIRA4_1r |
        | Cluster RA | 3 | CRA2_2r, CRA3_3r, CRA4_4r |
        | Blocked Cluster RA | 5 | BCRA3_2f, BCRA3_2r, BCRA4_2r, BCRA4_3f, BCRA4_3r |
        | Regression Discontinuity | 5 | RD2_1f, RD2_1r, RDC_2r, RDC_3r, RD3_2f |
        | Interrupted Time-Series | 2 | ITS (with/without comparison) |
        
        ### Design Effect Estimation (for RD designs)
        
        The design effect can be estimated from ρ_TS using the formula:
        
        **Design Effect = 1 / (1 - ρ_TS²)**
        
        Where ρ_TS is the correlation between the treatment indicator and the score used for treatment assignment.
        
        ### Reference
        
        > Dong, N. & Maynard, R. A. (2013). PowerUp!: A tool for calculating minimum detectable effect sizes 
        > and minimum required sample sizes for experimental and quasi-experimental design studies, 
        > *Journal of Research on Educational Effectiveness*, 6(1), 24-67. 
        > doi: 10.1080/19345747.2012.673143.
        
        ### Links
        - [Original PowerUp! Excel Tool](https://www.causalevaluation.org/)
        - [PyPowerUp Python Package](https://pypowerup.readthedocs.io/)
        - [PowerUpR (R Package)](https://CRAN.R-project.org/package=PowerUpR)
        """)


if __name__ == "__main__":
    main()
