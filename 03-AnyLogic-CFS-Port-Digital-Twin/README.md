# 03 — AnyLogic 8 Warehouse (CFS) & Container Terminal Digital Twin Models

## Overview
Contains Discrete-Event Simulation (DES) & Multi-Method models authored by **Doan Quang Dang**:
1. **Phu Huu CFS Warehouse Optimization (Published in JTST — Grant KHSV2514/HD-UTH)**:
   - **Journal Link**: https://jtst.ut.edu.vn/articles/6a1e8bd27dc7071ce848c1b8
   - Modeled LCL cargo handling (270 packages/shift across 5 dock doors) in AnyLogic 8 (**MAPE = 3.04%**, Two-Way ANOVA across 10 scenarios).
   - **Cost-Optimal SOP (KB4: 2 Ext – 4 Int)**: Cuts peak dock buffer queue ({\max}$) by **63.3%** and saves **356.4M VND/year**.
   - **Speed-Optimal SOP (KB9: 3 Ext – 5 Int)**: Reduces shift makespan by **20.1% (-92 mins)**.
2. **SP-ITC International Container Terminal Simulation (JTST-2026-1148)**:
   - Synchronized Quay Cranes (QCs), terminal trailers, and yard RTGs for a 2,782-move vessel call, proving **5 QCs + 20 Trailers** achieves an optimal **21.8-hour makespan** ({\text{QC}} = 85.4\%$).
3. **web-simulation-dashboard/**: Interactive HTML5 Warehouse Flow Simulation Dashboard (simulation_dashboard.html).
