# integrador_nt_sabados20262_6
proyecto integrador nuevas tecnologias

## Estructura

```
├── src/
│   ├── simular_retos.py     # HU F01: genera 500 retos sucios (generar_retos)
│   ├── exportar_retos.py    # HU X01: exporta a data/crudo (csv, xlsx, json)
│   └── limpiar_retos.py     # HU L01: limpia con pandas y guarda data/limpio
├── data/
│   ├── crudo/               # retos_sucio.csv / .xlsx / .json
│   └── limpio/              # retos_limpio.csv
├── notebook/                # simulaciones de las demas tablas y notebooks
├── requirements.txt
└── README.md
```

## Como ejecutar

Siempre desde la raiz del proyecto:

```bash
pip install -r requirements.txt
python src/simular_retos.py    # solo imprime shape, head y nulos
python src/exportar_retos.py   # crea data/crudo/retos_sucio.{csv,xlsx,json}
python src/limpiar_retos.py    # crea data/limpio/retos_limpio.csv
```

Los archivos de `data/` pesan menos de 300 KB y quedan versionados en Git.
Si se pierden, se regeneran con los comandos de arriba. Los datos salen igual en
cada corrida, salvo la columna `id` (usa `uuid4`, que no depende de la semilla).
