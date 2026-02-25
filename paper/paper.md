---
title: 'pypowerup-streamlit: A Browser-Based Power Analysis Tool for Experimental and Quasi-Experimental Designs'
tags:
  - Python
  - Streamlit
  - power analysis
  - effect size
  - experimental design
  - education research
  - causal inference
authors:
  - given-names: Jason
    surname: Godfrey
    orcid: 0000-0002-1977-9427
    affiliation: 1
affiliations:
  - name: Accelerate
    index: 1
date: 25 February 2026
bibliography: paper.bib
---

## Summary

`pypowerup-streamlit` is a browser-based statistical power analysis application covering 21 experimental and quasi-experimental designs commonly used in education, social science, and policy evaluation research. Built on the `pypowerup` Python library [@yang2021] and delivered via Streamlit [@streamlit2019], it provides an accessible graphical interface for three standard a priori calculations: Minimum Detectable Effect Size (MDES), Minimum Required Sample Size (MRSS), and statistical power ($1 - \beta$). The application spans multilevel designs from simple individual random assignment through four-level cluster randomized trials, regression discontinuity designs, and interrupted time-series designs. Numerical correctness is verified by a 77-test parity suite against the original PowerUp! Excel reference values [@dong2013], and built-in sensitivity analysis renders interactive charts for systematic parameter exploration.

## Statement of Need

Adequate statistical power is a prerequisite for credible experimental and quasi-experimental research. Standards bodies, including the What Works Clearinghouse [@what2008], require that evaluations be adequately powered prior to launch, yet accessible and high-quality power analysis tools for multilevel designs remain limited.

The canonical reference tool in this domain is the PowerUp! Excel workbook [@dong2013], which implements closed-form power formulas for multilevel designs based on the framework of Hedges and colleagues [@hedberg2007]. While that workbook has proven enormously useful, it carries several practical constraints: it requires Microsoft Excel with macro support enabled; parameter entries are session-specific and are lost unless manually copied; calculations cannot be embedded in reproducible analysis pipelines; and the macro-based format is opaque to version control systems.

The `pypowerup` Python package [@yang2021] addressed the programmatic gap by exposing the same calculation engine as a Python API. However, the package targets users who are comfortable writing Python code, excluding the large proportion of applied researchers and program evaluators who work in point-and-click environments. PowerUpR [@bulus2019] offers equivalent functionality for R users with the same constraint. Neither package provides a graphical interface.

`pypowerup-streamlit` fills this gap: a no-install, browser-accessible application that covers all 21 designs from the original workbook, requires no programming knowledge, and adds capabilities the Excel tool does not offer, including interactive sensitivity analysis, structured reproducible export, and an auto-generated methods paragraph for manuscript insertion.

## State of the Field

The three established tools for PowerUp!-style multilevel power analysis are compared in \autoref{tab:comparison}.

| Feature | PowerUp! Excel [@dong2013] | PowerUpR [@bulus2019] | `pypowerup` [@yang2021] | `pypowerup-streamlit` |
|---|---|---|---|---|
| No install / browser-based | No | No | No | Yes |
| Programming required | No | Yes (R) | Yes (Python) | No |
| Designs supported | 21 | Partial | 21 | 21 |
| Sensitivity curves | No | Limited | No | Yes |
| Reproducible export | No | Script | Script | CSV / JSON / Excel / LaTeX |
| Numerical parity tests | Reference | Partial | Partial | 77 tests |

: Comparison of power analysis tools for multilevel experimental designs. \label{tab:comparison}

Contributing a graphical interface to `pypowerup` was considered but is architecturally out of scope: `pypowerup` is designed as a stateless calculation API, and embedding a Streamlit front-end within it would couple user interface concerns to the library's design contract. Contributing to PowerUpR would duplicate effort for a separate language ecosystem without serving the primary target audience of non-programmers. A standalone Streamlit application consuming `pypowerup` as a dependency was therefore the appropriate architectural choice.

## Software Design

The application is a single-file Streamlit app (`app.py`, approximately 1,500 lines) that delegates all statistical computation to `pypowerup.core`. A strict separation of concerns is maintained: no power formulas appear in the UI layer, which handles only parameter collection, validation, and results display.

**Design coverage.** Six design categories are supported across up to four hierarchical levels:

1. *Individual Random Assignment (IRA)* — completely randomized controlled trials
2. *Blocked Individual Random Assignment (BIRA)* — individuals randomized within blocks, with constant, fixed, or random effects variants at two through four levels
3. *Cluster Random Assignment (CRA)* — clusters randomized as units with treatment at the cluster level, two through four levels
4. *Blocked Cluster Random Assignment (BCRA)* — cluster randomization nested within blocks, treatment at levels 2 or 3, fixed and random effects variants
5. *Regression Discontinuity (RD)* — sharp RD designs with a design-effect adjustment ($\delta = 2.75$ by default, following [@dong2013]) at two and three levels
6. *Interrupted Time-Series (ITS)* — pre-post time-series designs with and without comparison units

**Calculation modes.** All three standard a priori queries are supported:

- **MDES** — compute the smallest effect detectable at specified $\alpha$ and $1-\beta$
- **MRSS** — compute the required sample size at the relevant level for a target effect
- **Power** — compute the probability of detection given sample sizes and an effect size

The multiplier $M = T_1 + T_2$, where $T_1 = t_{1-\alpha/2,\,\nu}$ for a two-tailed test and $T_2 = t_{1-\beta,\,\nu}$, is evaluated via SciPy's $t$-distribution. Parameter conventions follow the Excel workbook directly: $\rho_2, \rho_3, \rho_4$ are intraclass correlations; $\omega_2, \omega_3, \omega_4$ are treatment effect heterogeneity parameters; $R^2_1, R^2_2, \ldots$ are proportions of variance explained by level-specific covariates; $g$ is the number of covariates; and $n, J, K, L$ are sample sizes at levels 1 through 4.

**Sensitivity analysis.** Users sweep any level's sample size over a specified range to generate power or MDES curves, rendered interactively via Plotly and downloadable as PNG images.

**Export.** Results are available in four formats: CSV, JSON, Excel (`.xlsx`), and a LaTeX table. A plain-language methods paragraph is generated for direct insertion into research manuscripts.

**Testing and open-source practices.** A 77-test parity suite (`pypowerup/tests/test_parity.py`) verifies agreement with the Excel reference values to at least two decimal places across all six design categories and all three calculation modes. The suite includes cross-design monotonicity checks — power increases with sample size, MDES decreases with $R^2$, required sample size increases as target effect size decreases — and a direct algebraic validation of the multiplier formula against SciPy. The project is released under a BSD-3-Clause license and structured to receive community contributions via standard GitHub pull requests.

## Research Impact Statement

The PowerUp! Excel workbook [@dong2013] has been cited in hundreds of published evaluations in education, public health, and social policy, demonstrating sustained demand for multilevel power analysis tools in these fields. The designs supported — school-randomized trials, district-randomized trials, regression discontinuity studies — represent the standard approach for planning evaluations aligned with What Works Clearinghouse standards [@what2008]. Intraclass correlation values typical of education settings [@hedberg2007] are used as defaults throughout the application, grounding its parameter space in empirically realistic values.

`pypowerup-streamlit` makes this class of analyses accessible to researchers and evaluators who work outside spreadsheet environments and without programming support. Program officers at foundations and government agencies who commission randomized evaluations but lack access to statisticians for routine power calculations represent the primary near-term user population. The addition of reproducible export formats — particularly JSON and LaTeX — directly supports the pre-registration and open science practices increasingly required in education research.

## AI Usage Disclosure

LLMs assisted in translating pypowerup for the browser. All test case validation against the Excel workbook were performed by the author. No AI-generated content was accepted without independent review and verification.

## References
