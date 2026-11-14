# integrador_nt_sabados20262_6
Proyecto integrador de Nuevas Tecnologias. Tabla trabajada: **retos**.

## Estructura

```
├── src/
│   ├── simular_retos.py     # HU F01: genera 500 retos sucios (generar_retos)
│   ├── exportar_retos.py    # HU X01: exporta a data/crudo (csv, xlsx, json)
│   ├── limpiar_retos.py     # HU L01: limpia con pandas -> data/limpio/retos_limpio.csv
│   ├── consultas_retos.py   # HU Q01: 5 consultas (2 con groupby) -> data/limpio/retos_consulta_N.csv
│   └── reporte_retos.py     # HU G01: 3 graficas + conclusiones -> reportes/
├── data/
│   ├── crudo/               # retos_sucio.csv / .xlsx / .json
│   └── limpio/              # retos_limpio.csv y retos_consulta_1..5.csv
├── reportes/                # retos_grafica_1.png, _2.png, _3.png
├── notebook/                # borradores y simulaciones de otras tablas
├── requirements.txt
└── README.md
```

## Como ejecutar

Siempre desde la raiz del proyecto, en este orden:

```bash
pip install -r requirements.txt
python src/simular_retos.py     # solo imprime shape, head y nulos
python src/exportar_retos.py    # crea data/crudo/retos_sucio.{csv,xlsx,json}
python src/limpiar_retos.py     # crea data/limpio/retos_limpio.csv
python src/consultas_retos.py   # crea data/limpio/retos_consulta_{1..5}.csv
python src/reporte_retos.py     # crea reportes/retos_grafica_{1,2,3}.png
```

Los archivos de `data/` y `reportes/` pesan poco y quedan versionados en Git.
Si se pierden, se regeneran con los comandos de arriba. Los datos salen igual en
cada corrida, salvo la columna `id` (usa `uuid4`, que no depende de la semilla)
y el rango de fechas, que Faker calcula respecto a la fecha de hoy.
