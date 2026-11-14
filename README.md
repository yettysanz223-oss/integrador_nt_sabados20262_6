# integrador_nt_sabados20262_6
proyecto integrador nuevas tecnologias

Tabla trabajada: `empresas` (id, nombre, nit, sector, contacto, correo, telefono, activa).

## Cómo generar los datos (desde la raíz del proyecto)

```
pip install -r requirements.txt
python src/Notebook/main.py                                   # simula (300 filas) y exporta a data/crudo/
python src/Notebook/limpiezas/limpiar_empresas.py             # data/crudo/empresas_sucio.csv -> data/limpio/empresas_limpio.csv
python src/Notebook/consultas/consultas_empresas.py           # data/limpio/empresas_consulta_1..5.csv
python src/Notebook/graficas/reporte_empresas.py              # reportes/empresas_grafica_1..3.png
python revisar_datos.py data/crudo/empresas_sucio.csv         # revisa el archivo sucio contra la HU
```
