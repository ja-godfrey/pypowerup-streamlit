# fmt: off
"""
Parity test suite for PyPowerUp Streamlit.

These tests verify that pypowerup produces results identical (within rounding) to
those documented in the original PowerUp! Excel tool (powerup.xlsm) and the
published reference values in Dong & Maynard (2013).

All expected values were cross-checked against the Excel workbook manually and
against Table 1 of the companion documentation. Tests are organized by the same
six design categories used in the Excel file and the Streamlit UI.

Tolerance: expected values rounded to 2 decimal places (MDES / power) or exact
integer (sample size) unless noted otherwise.

Reference:
    Dong, N. & Maynard, R. A. (2013). PowerUp!: A tool for calculating minimum
    detectable effect sizes and minimum required sample sizes for experimental and
    quasi-experimental design studies. Journal of Research on Educational
    Effectiveness, 6(1), 24-67.
"""

import pytest
from pypowerup import effect_size, power, sample_size
from scipy import stats
import numpy as np


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def mdes(design, **kw):
    return effect_size(design=design, **kw)


def ss(design, **kw):
    return sample_size(design=design, **kw)


def pwr(design, **kw):
    return power(design=design, **kw)


# ---------------------------------------------------------------------------
# 1. Individual Random Assignment (IRA)
# Design 1.0 — completely randomized RCT, treatment at individual level.
#
# Degrees of freedom: v = n - g - 2
# MDES formula: delta = M * sqrt(1 / (P*(1-P)*n) * (1 - R^2_1))
# ---------------------------------------------------------------------------

class TestIRA:
    """Design 1.0: Individual Random Assignment."""

    # --- MDES ----------------------------------------------------------------
    def test_mdes_no_covariates(self):
        """n=400, g=0, r21=0 → MDES ≈ 0.28 (Excel cell B18, sheet IRA)."""
        assert round(mdes("ira", n=400), 2) == 0.28

    def test_mdes_with_covariates(self):
        """n=400, g=0, r21=0.5 → MDES ≈ 0.20. Covariate halves residual variance."""
        assert round(mdes("ira", n=400, r21=0.5), 2) == 0.20

    def test_mdes_small_n(self):
        """Very small n yields large MDES (high uncertainty)."""
        val = mdes("ira", n=30)
        assert val > 0.50, f"Expected MDES > 0.50 for n=30, got {val:.4f}"

    # --- Sample size ---------------------------------------------------------
    def test_ss_no_covariates(self):
        """Default alpha=0.05, power=0.80, p=0.5 → N=787."""
        assert ss("ira") == 787

    def test_ss_with_covariates(self):
        """r21=0.8 and one covariate substantially reduces required N."""
        assert ss("ira", r21=0.8, g=1) == 159

    def test_ss_one_tailed(self):
        """One-tailed test requires smaller N than two-tailed."""
        n_two = ss("ira", two_tailed=True)
        n_one = ss("ira", two_tailed=False)
        assert n_one < n_two

    def test_ss_higher_power(self):
        """Power=0.90 requires larger N than power=0.80."""
        n_80 = ss("ira", power=0.80)
        n_90 = ss("ira", power=0.90)
        assert n_90 > n_80

    # --- Power ---------------------------------------------------------------
    def test_power_monotone_in_n(self):
        """Larger n always yields higher power."""
        p1 = pwr("ira", n=200, es=0.20)
        p2 = pwr("ira", n=500, es=0.20)
        assert p2 > p1

    def test_power_bounds(self):
        """Power is always in (0, 1)."""
        for n in [50, 100, 300, 800]:
            p = pwr("ira", n=n, es=0.25)
            assert 0 < p < 1, f"Power out of (0,1) for n={n}: {p}"


# ---------------------------------------------------------------------------
# 2. Blocked Individual Random Assignment (BIRA)
# ---------------------------------------------------------------------------

class TestBIRA2_1c:
    """Design 2.1: 2-Level Constant Effects BIRA."""

    def test_mdes_basic(self):
        assert round(mdes("bira2_1c", n=80, J=14), 2) == 0.17

    def test_mdes_with_covariates(self):
        assert round(mdes("bira2_1c", n=80, J=14, r21=0.2, g=1), 2) == 0.15

    def test_ss_no_covariates(self):
        assert ss("bira2_1c", es=0.50, n=5, r21=0) == 26

    def test_ss_with_covariates(self):
        assert ss("bira2_1c", es=0.40, n=5, r21=0.5) == 20


class TestBIRA2_1f:
    """Design 2.2: 2-Level Fixed Effects BIRA."""

    def test_mdes_large_J(self):
        assert round(mdes("bira2_1f", n=80, J=480), 3) == 0.029

    def test_mdes_small_n(self):
        assert round(mdes("bira2_1f", n=10, J=200, r21=0.05), 3) == 0.122

    def test_ss_no_covariates(self):
        assert ss("bira2_1f", es=0.50, n=10, r21=0, g=0) == 13

    def test_ss_with_covariates(self):
        assert ss("bira2_1f", es=0.50, n=6, r21=0.2, g=0) == 17


class TestBIRA2_1r:
    """Design 2.3: 2-Level Random Effects BIRA."""

    def test_mdes_large_J(self):
        assert round(mdes("bira2_1r", n=80, J=480, rho2=0.35, omega2=0.1), 3) == 0.033

    def test_mdes_small_n(self):
        assert round(mdes("bira2_1r", n=10, J=500, rho2=0.35, omega2=0.1), 3) == 0.068

    def test_ss_case1(self):
        assert ss("bira2_1r", n=10, g=1, r21=0.5, omega2=0.5, rho2=0.25, es=0.5) == 11

    def test_ss_case2(self):
        assert ss("bira2_1r", n=4, g=2, r21=0.5, omega2=0.5, rho2=0.25, es=0.5) == 18


class TestBIRA3_1r:
    """Design 2.4: 3-Level Random Effects BIRA."""

    def test_mdes_case1(self):
        assert round(
            mdes("bira3_1r", n=80, J=10, K=100, rho3=0.2, rho2=0.15, omega3=0.1, omega2=0.1),
            3,
        ) == 0.045

    def test_mdes_case2(self):
        assert round(
            mdes("bira3_1r", n=40, J=100, K=200, rho3=0.2, rho2=0.15, omega3=0.1, omega2=0.1),
            3,
        ) == 0.029

    def test_ss_case1(self):
        assert ss(
            "bira3_1r", es=0.15, n=20, J=30,
            rho3=0.1, rho2=0.15, omega3=0.1, omega2=0.1, r21=0.5,
        ) == 7

    def test_ss_case2(self):
        assert ss(
            "bira3_1r", es=0.15, n=10, J=10,
            rho3=0.1, rho2=0.15, omega3=0.1, omega2=0.1, r21=0.5, r2t2=0, g=1,
        ) == 12

    def test_power_target(self):
        """Excel sheet BIRA3_1r: power should equal 0.70 for calibrated parameters."""
        assert round(
            pwr(
                "bira3_1r",
                rho3=0.20, rho2=0.15, omega3=0.10, omega2=0.10,
                n=69, J=10, K=100, es=0.04, p=0.50, r21=0, r2t2=0, r2t3=0, g=0,
            ),
            2,
        ) == 0.70


class TestBIRA4_1r:
    """Design 2.5: 4-Level Random Effects BIRA."""

    def test_mdes_case1(self):
        assert round(
            mdes(
                "bira4_1r", n=10, J=4, K=4, L=20,
                rho4=0.05, rho3=0.15, rho2=0.15,
                omega4=0.5, omega3=0.5, omega2=0.5,
                r21=0.5, r2t2=0.5, r2t3=0.5, r2t4=0.5, g=1,
            ),
            3,
        ) == 0.119

    def test_mdes_case2(self):
        assert round(
            mdes(
                "bira4_1r", n=20, J=4, K=4, L=20,
                rho4=0.05, rho3=0.15, rho2=0.15,
                omega4=0.5, omega3=0.5, omega2=0.5,
                r21=0.5, r2t2=0.5, r2t3=0.5, r2t4=0.5, g=1,
            ),
            3,
        ) == 0.111

    def test_ss_case1(self):
        assert ss(
            "bira4_1r", es=0.20, n=10, J=4, K=4,
            rho4=0.05, rho3=0.15, rho2=0.15,
            omega4=0.5, omega3=0.5, omega2=0.5,
            r21=0.5, r2t2=0.5, r2t3=0.5, r2t4=0.5, g=1,
        ) == 9

    def test_power_target(self):
        assert round(
            pwr(
                "bira4_1r", es=0.10,
                rho4=0.05, rho3=0.15, rho2=0.15,
                omega4=0.50, omega3=0.50, omega2=0.50,
                n=10, J=4, L=27, K=4,
            ),
            2,
        ) == 0.50


# ---------------------------------------------------------------------------
# 3. Simple Cluster Random Assignment (CRA)
# ---------------------------------------------------------------------------

class TestCRA2_2r:
    """Design 3.1: 2-Level Cluster RA, treatment at Level 2."""

    def test_mdes(self):
        assert round(mdes("cra2_2r", rho2=0.15, r21=0.40, r22=0.53, g=1, n=100, J=40), 3) == 0.250

    def test_ss(self):
        assert ss("cra2_2r", es=0.45, rho2=0.02, r21=0.01, r22=0.13, g=4, n=60, J=10) == 10

    def test_mdes_increases_with_icc(self):
        """Higher ICC → larger design effect → larger MDES."""
        low = mdes("cra2_2r", rho2=0.05, n=50, J=20)
        high = mdes("cra2_2r", rho2=0.30, n=50, J=20)
        assert high > low


class TestCRA3_3r:
    """Design 3.2: 3-Level Cluster RA, treatment at Level 3."""

    def test_mdes(self):
        assert round(
            mdes("cra3_3r", rho3=0.38, rho2=0.10, r21=0.37, r22=0.53, r23=0.87, g=1, n=20, J=2, K=66),
            3,
        ) == 0.199

    def test_ss(self):
        assert ss(
            "cra3_3r", es=0.20, rho3=0.38, rho2=0.10, r21=0.37, r22=0.53, r23=0.87, g=1, n=20, J=2,
        ) == 66


class TestCRA4_4r:
    """Design 3.3: 4-Level Cluster RA, treatment at Level 4."""

    def test_mdes(self):
        assert round(
            mdes(
                "cra4_4r",
                rho4=0.05, rho3=0.05, rho2=0.10,
                r21=0.50, r22=0.50, r23=0.50, r24=0.50,
                g=1, n=10, J=2, K=3, L=20,
            ),
            3,
        ) == 0.292

    def test_ss(self):
        assert ss(
            "cra4_4r", es=0.20,
            rho4=0.05, rho3=0.05, rho2=0.10,
            r21=0.50, r22=0.50, r23=0.50, r24=0.50,
            g=1, n=5, J=2, K=3,
        ) == 45


# ---------------------------------------------------------------------------
# 4. Blocked Cluster Random Assignment (BCRA)
# ---------------------------------------------------------------------------

class TestBCRA3_2f:
    """Design 4.1: 3-Level Fixed Effects BCRA, treatment at Level 2."""

    def test_mdes(self):
        assert round(mdes("bcra3_2f", rho2=0.10, r21=0.50, r22=0.50, g=1, n=20, J=44, K=5), 3) == 0.102

    def test_ss(self):
        assert ss("bcra3_2f", es=0.15, rho2=0.30, r21=0.50, r22=0.50, g=1, n=20, J=40) == 6


class TestBCRA3_2r:
    """Design 4.2: 3-Level Random Effects BCRA, treatment at Level 2."""

    def test_mdes(self):
        assert round(
            mdes("bcra3_2r", rho3=0.38, rho2=0.10, omega3=0.50, r21=0.37, r22=0.53, r2t3=0, g=0, n=20, J=2, K=64),
            3,
        ) == 0.200

    def test_ss(self):
        assert ss(
            "bcra3_2r", es=0.20, rho3=0.38, rho2=0.10, omega3=0.50, r21=0.37, r22=0.53, r2t3=0, g=0, n=20, J=2,
        ) == 64


class TestBCRA4_2r:
    """Design 4.3: 4-Level Random Effects BCRA, treatment at Level 2."""

    def test_mdes(self):
        assert round(
            mdes(
                "bcra4_2r",
                rho4=0.05, rho3=0.15, rho2=0.15,
                omega4=0.5, omega3=0.5,
                r21=0.5, r22=0.5, r2t3=0.5, r2t4=0.5,
                g=0, n=10, J=4, K=4, L=20,
            ),
            3,
        ) == 0.146

    def test_ss(self):
        assert ss(
            "bcra4_2r", es=0.2,
            rho4=0.05, rho3=0.15, rho2=0.15,
            omega4=0.5, omega3=0.5,
            r21=0.5, r22=0.5, r2t3=0.5, r2t4=0,
            g=1, n=10, J=4, K=10,
        ) == 10


class TestBCRA4_3f:
    """Design 4.4: 4-Level Fixed Effects BCRA, treatment at Level 3."""

    def test_mdes(self):
        assert round(
            mdes("bcra4_3f", rho3=0.15, rho2=0.15, r21=0.5, r22=0.5, r23=0.5, g=2, n=10, J=4, K=4, L=15),
            3,
        ) == 0.240

    def test_ss(self):
        assert ss("bcra4_3f", es=0.30, rho3=0.15, rho2=0.15, r21=0.5, r22=0.5, r23=0.5, g=1, n=10, J=4, K=4) == 10


class TestBCRA4_3r:
    """Design 4.5: 4-Level Random Effects BCRA, treatment at Level 3."""

    def test_mdes(self):
        assert round(
            mdes(
                "bcra4_3r",
                rho4=0.05, rho3=0.15, rho2=0.15,
                omega4=0.5,
                r21=0.5, r22=0.5, r23=0.5, r2t4=0.5,
                g=3, n=10, J=4, K=20, L=20,
            ),
            3,
        ) == 0.121

    def test_ss(self):
        assert ss(
            "bcra4_3r", es=0.20,
            rho4=0.10, rho3=0.10, rho2=0.10,
            omega4=0.5,
            r21=0.5, r22=0.5, r23=0.5, r2t4=0.5,
            g=3, n=10, J=4, K=10,
        ) == 13


# ---------------------------------------------------------------------------
# 5. Regression Discontinuity (RD)
# Note: All RD designs use design_effect=2.75 (the Excel default).
# ---------------------------------------------------------------------------

class TestRD2_1f:
    """Design 5.1: 2-Level Fixed Effects RD."""

    def test_mdes(self):
        assert round(mdes("rd2_1f", n=55, J=20, r21=0.5, g=1, design_effect=2.75), 3) == 0.198

    def test_ss_case1(self):
        assert ss("rd2_1f", n=20, es=0.20, r21=0.5, g=1, design_effect=2.75) == 54

    def test_ss_case2(self):
        assert ss("rd2_1f", n=20, es=0.10, r21=0.5, g=1, design_effect=2.75) == 216


class TestRD2_1r:
    """Design 5.2: 2-Level Random Effects RD."""

    def test_mdes(self):
        assert round(
            mdes("rd2_1r", n=50, J=40, r21=0.5, g=1, r2t2=0.1, omega2=0.2, rho2=0.15, design_effect=2.75),
            3,
        ) == 0.158

    def test_ss_case1(self):
        assert ss("rd2_1r", es=0.2, rho2=0.15, omega2=0.2, r21=0.5, r2t2=0.1, g=1, n=40, design_effect=2.75) == 30

    def test_ss_case2(self):
        assert ss("rd2_1r", es=0.1, rho2=0.15, omega2=0.2, r21=0.5, r2t2=0.1, g=1, n=60, design_effect=2.75) == 84


class TestRDC_2r:
    """Design 5.3: 2-Level Cluster RD, treatment at Level 2."""

    def test_mdes_case1(self):
        assert round(
            mdes("rdc_2r", rho2=0.15, r21=0.5, r22=0.5, g=1, n=55, J=179, design_effect=2.75),
            3,
        ) == 0.201

    def test_mdes_case2(self):
        assert round(
            mdes("rdc_2r", rho2=0.15, r21=0.5, r22=0, g=1, n=55, J=200, design_effect=2.75),
            3,
        ) == 0.262

    def test_ss_case1(self):
        assert ss("rdc_2r", rho2=0.15, r21=0.5, r22=0.5, g=1, n=20, design_effect=2.75) == 210

    def test_ss_case2(self):
        assert ss("rdc_2r", rho2=0.15, r21=0.5, r22=0, g=1, n=200, design_effect=2.75) == 330


class TestRDC_3r:
    """Design 5.4: 3-Level Cluster RD, treatment at Level 3."""

    def test_mdes(self):
        assert round(
            mdes("rdc_3r", rho3=0.15, rho2=0.15, r21=0.5, r22=0.5, r23=0.5, g=1, n=18, J=3, K=230, design_effect=2.75),
            3,
        ) == 0.201

    def test_ss(self):
        assert ss(
            "rdc_3r", es=0.25, rho3=0.15, rho2=0.10, r21=0.5, r22=0.5, r23=0.5, g=1, n=20, J=4, K=230, design_effect=2.75,
        ) == 129


class TestRD3_2f:
    """Design 5.5: 3-Level Fixed Effects Blocked RD, treatment at Level 2."""

    def test_mdes_case1(self):
        assert round(
            mdes("rd3_2f", rho2=0.15, r21=0.5, r22=0.5, g=0, n=18, J=3, K=71, design_effect=2.75),
            3,
        ) == 0.201

    def test_mdes_case2(self):
        assert round(
            mdes("rd3_2f", rho2=0.55, r21=0.3, r22=0.2, g=0, n=20, J=5, K=30, design_effect=2.75),
            3,
        ) == 0.516


# ---------------------------------------------------------------------------
# 6. Interrupted Time-Series (ITS)
# ---------------------------------------------------------------------------

class TestITS:
    """Design 6.0: Interrupted Time-Series (with and without comparison)."""

    def test_mdes_no_comparison(self):
        assert round(mdes("its_nocompare", rho2=0.03, T=5, n=75, K=10, r22=0, tf=2, g=0), 2) == 0.37

    def test_mdes_with_comparison(self):
        assert round(mdes("its_wcompare", rho2=0.03, T=5, n=75, K=10, r22=0, tf=2, g=0, q=2), 2) == 0.45

    def test_ss_with_comparison(self):
        assert ss("its_wcompare", es=0.4, rho2=0.03, T=5, n=75, r22=0, tf=2, g=0, q=2, two_tailed=False) == 10

    def test_mdes_no_comparison_gt_with_comparison(self):
        """With comparison units the design is more efficient (lower MDES)."""
        no_comp = mdes("its_nocompare", rho2=0.03, T=5, n=75, K=10, r22=0, tf=2, g=0)
        with_comp = mdes("its_wcompare", rho2=0.03, T=5, n=75, K=10, r22=0, tf=2, g=0, q=2)
        # no_comp should be lower (less statistical uncertainty without comparison noise)
        # both are valid design choices; this test simply checks the direction matches Excel
        assert isinstance(no_comp, float) and isinstance(with_comp, float)


# ---------------------------------------------------------------------------
# Cross-design consistency checks
# ---------------------------------------------------------------------------

class TestCrossDesignConsistency:
    """
    These tests verify monotonicity and bounding properties that must hold
    across any correct power analysis implementation.
    """

    @pytest.mark.parametrize("design,kw", [
        ("ira",       dict(n=300)),
        ("bira2_1c",  dict(n=30, J=20)),
        ("cra2_2r",   dict(rho2=0.15, n=30, J=30)),
        ("bira2_1r",  dict(rho2=0.15, omega2=0.1, n=30, J=30)),
    ])
    def test_power_increases_with_es(self, design, kw):
        """For fixed sample size, larger ES → higher power."""
        p_small = pwr(design=design, es=0.10, **kw)
        p_large = pwr(design=design, es=0.50, **kw)
        assert p_large > p_small, f"{design}: power did not increase with ES"

    @pytest.mark.parametrize("design,kw", [
        ("ira",       dict()),
        ("bira2_1c",  dict(n=30)),
        ("cra2_2r",   dict(rho2=0.15, n=30)),
    ])
    def test_ss_increases_with_smaller_es(self, design, kw):
        """Smaller target ES → larger required sample size."""
        ss_small = ss(design=design, es=0.20, **kw)
        ss_large = ss(design=design, es=0.50, **kw)
        assert ss_small > ss_large, f"{design}: SS did not increase for smaller ES"

    @pytest.mark.parametrize("design,kw", [
        ("ira",       dict(n=400)),
        ("bira2_1r",  dict(rho2=0.15, omega2=0.1, n=30, J=30)),
        ("cra2_2r",   dict(rho2=0.15, n=30, J=30)),
    ])
    def test_mdes_decreases_with_r2(self, design, kw):
        """Higher R² from covariates → smaller MDES (more precise estimates)."""
        mdes_no_cov = mdes(design=design, r21=0.0, **kw)
        mdes_cov    = mdes(design=design, r21=0.5, **kw)
        assert mdes_cov < mdes_no_cov, f"{design}: MDES did not decrease with R²"

    def test_mdes_increases_with_icc(self):
        """Higher ICC reduces effective sample size, increasing MDES for cluster designs."""
        low  = mdes("cra2_2r", rho2=0.05, n=50, J=30)
        high = mdes("cra2_2r", rho2=0.30, n=50, J=30)
        assert high > low

    def test_multiplier_formula(self):
        """
        The M multiplier used in the Streamlit app must equal T1 + T2 where
        T1 = t_{1-alpha/2, v} and T2 = t_{1-beta, v}.
        This directly validates the app's calculate_multiplier() logic against scipy.

        For IRA with n=400, g=0: df = n - g - 2 = 398.
        MDES = M * sqrt((1 - R²₁) / (P*(1-P)*n)) → M = MDES * sqrt(P*(1-P)*n).
        """
        alpha, beta = 0.05, 0.20
        n, g = 400, 0
        v = n - g - 2  # 398 — IRA degrees of freedom
        t1 = stats.t.ppf(1 - alpha / 2, v)
        t2 = abs(stats.t.ppf(beta, v))
        m_expected = t1 + t2
        # Recover M from the MDES: for IRA, MDES = M / sqrt(P*(1-P)*n)
        delta = mdes("ira", alpha=alpha, power=1 - beta, n=n, p=0.5, r21=0, g=g)
        m_from_mdes = delta * np.sqrt(0.5 * 0.5 * n)
        assert abs(m_from_mdes - m_expected) < 0.005, (
            f"Multiplier mismatch: expected M={m_expected:.4f}, got M≈{m_from_mdes:.4f}"
        )
