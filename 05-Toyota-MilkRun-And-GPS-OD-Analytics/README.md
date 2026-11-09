# 05 — Toyota Milk-Run Route Optimizer & GPS Trajectory O-D Matrix Mining

## Overview
1. **milkrun-route-optimizer/ (SCRACE 2026 — Toyota Vietnam Case Study)**: Web application & heuristic solver for domestic automotive parts **Milk-Run collection** and **Heijunka (level scheduling)** across suppliers and assembly/welding docks, featuring interactive Leaflet route mapping, cubic-meter (^3$) truck fill-rate optimization, and automated Excel schedule export.
2. **gps-trajectory-od-mining/**: Python spatial data mining pipeline (gps_data_mining.py, isualize_od_map.py) implementing Haversine rule-based **Stay-Point Detection** ( \le 50\text{m}, t \ge 15\text{ mins}$), automated trip extraction, and an interactive **Origin-Destination (O-D) Matrix Dashboard (od_interactive_dashboard.html)**.
