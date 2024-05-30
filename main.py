# Importamos librerías
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt

# Cargar datos
try:
    progreso_df = pd.read_csv('data/Progreso.csv')
    grupo_muscular_df = pd.read_csv('data/Grupo_muscular.csv')
    usuario_df = pd.read_csv('data/Usuarios.csv')
except FileNotFoundError as e:
    st.error(f"Error al cargar archivos: {e}")

# Funciones
def formulario_desarrollo_fuerza(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Set {i+1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, [repeticiones] * Sets, [descanso] * Sets

def formulario_mejora_resistencia(Sets):
    pesos = []
    for i in range(Sets):
        peso = st.number_input(f'💪 Peso para el Set {i+1}:', min_value=0.0, step=0.1, format="%.1f")
        pesos.append(peso)
    repeticiones = [st.number_input(f'🏃 Repeticiones para el Set {i+1}:', min_value=1, max_value=30, step=1) for i in range(Sets)]
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return pesos, repeticiones, [descanso] * Sets

def formulario_hipertrofia_muscular(Sets):
    peso = st.number_input('💪 Peso (kg):', min_value=0.0, step=0.1, format="%.1f")
    repeticiones = st.number_input('Repeticiones:', min_value=1, max_value=30, step=1)
    descanso = st.selectbox('Tiempo de descanso:', ('1-2 min', '2-3 min', '3-4 min'))
    return [peso] * Sets, [repeticiones] * Sets, [descanso] * Sets

def download_csv(df, filename):
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Descargar {filename}</a>'
    return href

def calcular_promedio(df):    
    df['Sets_x_Reps'] = df['Sets'] * df['Repeticiones']
    df['Peso_Total'] = df['Peso'] * df['Sets'] * df['Repeticiones']
    df['Suma_Repeticiones'] = df.groupby(['Id_Usuario', 'Dia'])['Repeticiones'].transform('sum')
    promedio_ponderado_por_persona = df.groupby(['Id_Usuario', 'Dia']).apply(
    lambda x: (x['Peso_Total'].sum() / x['Sets_x_Reps'].sum())
    ).reset_index(name='Promedio_Ponderado')
    resultado_final = df[['Id_Usuario', 'Dia', 'Suma_Repeticiones']].drop_duplicates().merge(
    promedio_ponderado_por_persona, on=['Id_Usuario', 'Dia'])
    return resultado_final

def crear_graficos(df_grupo, colores):
    df_grupo = df_grupo.reset_index(drop=True)
    if len(df_grupo) == 0:
        st.warning("No hay suficientes datos disponibles para mostrar los gráficos.")
        return
    resultado_final = calcular_promedio(df_grupo)
    resultado_final = resultado_final.merge(usuario_df[['Id_Usuario', 'Nombre']], on='Id_Usuario')
    resultado_final['Dia_ordenado'] = resultado_final.groupby('Dia').cumcount() + 1
    line_chart = alt.Chart(resultado_final).mark_line().encode(
        x='Dia_ordenado:T',
        y=alt.Y('Promedio_Ponderado', title='Promedio de Peso'),
        color=alt.Color('Nombre:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue']), title='Persona'),
        tooltip=['Nombre', 'Dia', 'Promedio_Ponderado']
    ).properties(
        title="Promedio de Peso Levantado"
    )
    st.altair_chart(line_chart, use_container_width=True)

# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# Formulario desplegable y botón de guardar
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.selectbox('Selecciona tu nombre 🤵‍♂️🙍:', usuario_df['Nombre'].unique())
    Maquina = st.selectbox('Selecciona una máquina 🏋️‍♀️🏋️‍♂️:', grupo_muscular_df['Maquina'].unique())
    Enfoque = st.selectbox('Selecciona el enfoque de entrenamiento:', ('Desarrollo de Fuerza', 'Mejora de la Resistencia', 'Hipertrofia Muscular'))
    Sets = st.number_input('Número de Sets:', min_value=1, max_value=10, step=1, value=4)
    
    if Enfoque == 'Desarrollo de Fuerza':
        pesos, repeticiones, descansos = formulario_desarrollo_fuerza(Sets)
    elif Enfoque == 'Mejora de la Resistencia':
        pesos, repeticiones, descansos = formulario_mejora_resistencia(Sets)
    else:
        pesos, repeticiones, descansos = formulario_hipertrofia_muscular(Sets)
        
    form_completo = all(pesos) and all(repeticiones) and all(descansos)
    
    if form_completo:
        if st.button('Guardar'):
            progreso_new = pd.DataFrame({
                'Dia': [Dia] * Sets,
                'Id_Usuario': usuario_df[usuario_df['Nombre'] == Persona]['Id_Usuario'].values[0],
                'Maquina': [Maquina] * Sets,
                'Sets': [Sets] * Sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Descanso': descansos
            })
            progreso_df = pd.concat([progreso_df, progreso_new], ignore_index=True)
            progreso_df.to_csv('/mnt/data/Progreso.csv', index=False)
            st.success('¡Datos registrados con éxito!')
            st.markdown(download_csv(progreso_df, 'Progreso_Actualizado'), unsafe_allow_html=True)

# Visualización de datos registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    # Unir DataFrame de progreso con el de usuarios para obtener nombres en lugar de ID de usuario
    progreso_nombre_df = progreso_df.merge(usuario_df[['Id_Usuario', 'Nombre']], on='Id_Usuario')
    # Seleccionar columnas específicas para mostrar en la tabla
    selected_columns = ['Dia', 'Nombre', 'Maquina', 'Sets', 'Repeticiones']
    # Mostrar la tabla con las columnas seleccionadas
    st.dataframe(progreso_nombre_df[selected_columns])
    st.markdown(download_csv(progreso_df, 'Progreso_Completo'), unsafe_allow_html=True)



# Visualización de gráficos
with st.expander('📊 Visualización de Gráficos'):
    st.subheader("Datos de Gráficos por Grupo Muscular")
    # Obtener todos los grupos musculares únicos
    grupos_musculares = progreso_persona_grupo['Grupo_Muscular'].unique().tolist()
    # Widget multiselect para que el usuario seleccione los grupos musculares de interés
    grupos_seleccionados = st.multiselect('Selecciona los grupos musculares:', grupos_musculares)
    
    # Iterar sobre los grupos musculares seleccionados
    for grupo in grupos_seleccionados:
        with st.expander(f'Grupo Muscular: {grupo}'):
            # Filtrar el DataFrame por el grupo muscular seleccionado
            progreso_grupo_seleccionado = progreso_persona_grupo[progreso_persona_grupo['Grupo_Muscular'] == grupo]

            # Verificar si hay suficientes datos para mostrar el gráfico
            if not progreso_grupo_seleccionado.empty:
                # Gráfico de línea para el progreso por grupo muscular
                grafica_grupo_muscular = alt.Chart(progreso_grupo_seleccionado).mark_line().encode(
                    x='Dia:T',
                    y='Peso:Q',
                    color='Maquina:N',
                    tooltip=['Dia', 'Peso', 'Maquina']
                ).properties(
                    title=f"Progreso para el grupo muscular: {grupo}"
                )
                st.altair_chart(grafica_grupo_muscular, use_container_width=True)
            else:
                st.warning(f"No hay suficientes datos disponibles para mostrar el gráfico para el grupo muscular: {grupo}")
