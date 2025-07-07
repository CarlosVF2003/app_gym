# Gym & Running Tracker

Aplicación sencilla en Streamlit para registrar entrenamientos de gimnasio y carreras.

## Uso

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar con Streamlit:
   ```bash
   streamlit run main.py
   ```

## Características
- Registro y autenticación de usuarios.
- Inicio de sesión y registro en pestañas para una mejor experiencia.
- Catálogo editable de ejercicios de gimnasio y running.
- Registro diario con peso (kg/lb), repeticiones, series y distancia.
- Paneles de progreso interactivos con métricas ejecutivas (volumen, distancia y sesiones) y comparativas entre usuarios.
- Indicador de consistencia con promedio de días entrenados por semana.
- Filtros rápidos Hoy/7 días/30 días o personalizado para cambiar todas las gráficas.
- Gráficos de peso promedio, volumen por grupo muscular y distancia semanal.
- Barras de volumen por ejercicio y por grupo muscular.
- Recordatorios de entrenamiento desde la barra lateral.
- Carga de rutas GPX/CSV y mapa de recorridos para carreras.
- Exportación e importación de datos para sincronizar con otras plataformas.
- Manejo correcto de fechas incluso si los registros usan números de día.


## Reiniciar datos de usuarios
Si deseas borrar la información de usuarios registrada, ejecuta:
```bash
python reset_data.py
```
Se generará un archivo `data/Usuarios.csv` vacío con solo las cabeceras.
