@echo off
rem Repo NAO: abre la ventana de despliegue de la Carrera Individual (Copa NAO CCM MX 2026).
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
  start "" ".venv\Scripts\pythonw.exe" deploy\deploy_dialog.py
) else (
  start "" uv run pythonw deploy\deploy_dialog.py
)
