# 02 — Metro Line 2 Survey Master Data Auditing & 26-Station Automated GIS Reporting Engine

## Overview
Developed during the **Metro Line 2 & 2S Transit Integration Project (MIT Consulting JSC)**:
1. **gis-report-engine/**: Python automation pipeline (generate_maps.py, extract_stations.py, cross_compare_excel_kmz.py, prepare_final_template.py) that parses Google Earth .kmz station coordinates, cross-audits Excel Origin-Destination (O-D) trip tables, renders 5 spatial buffer maps per station (200m/500m/1000m walking rings, 24 bus stops, PUDO zones, conflict points), and compiles **26 standardized 30+ page Word reports (ST01–ST26)**.
2. **pwa-survey-auditor/**: Offline-first Progressive Web App (PWA) and strict logic validation engine auditing **1,000+ passenger interviews** and modeling modal-shift probability across **63 fare & travel-time scenarios** (91.9% ceiling at 7k VND / -15m vs. 1.8% floor at 25k VND / +15m).
3. **google-forms-gps-bridge/**: Google Apps Script (TaoForm_*.gs, WebBridgeGPS.js) automating survey form generation and real-time GPS coordinate capture.
