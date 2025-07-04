# Importamos librerías
import pandas as pd
import streamlit as st
from pathlib import Path
from base64 import b64encode
import altair as alt
import login

# Autenticación
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    modo = st.sidebar.radio('Autenticación', ['Iniciar Sesión', 'Registrar'])
    if modo == 'Iniciar Sesión':
        login.login_form()
    else:
        login.signup_form()
    st.stop()

# Cargar datos
DATA_DIR = Path(__file__).parent / 'data'
try:
    progreso_df = pd.read_csv(DATA_DIR / 'Progreso.csv')
    grupo_muscular_df = pd.read_csv(DATA_DIR / 'Grupo_muscular.csv')
    usuario_df = pd.read_csv(DATA_DIR / 'Usuarios.csv')
except FileNotFoundError as e:
    st.error(f"Error al cargar archivos: {e}")

# Unir las tablas
progreso_df = progreso_df.merge(grupo_muscular_df, on='Maquina')
progreso_df = progreso_df.merge(usuario_df, on='Id_Usuario')

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
        lambda x: x['Peso_Total'].sum() / x['Sets_x_Reps'].sum()
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
    resultado_final['Dia_ordenado'] = resultado_final.groupby('Id_Usuario').cumcount() + 1

    # Gráfico de promedio de peso levantado
    line_chart = alt.Chart(resultado_final).mark_line().encode(
        x='Dia_ordenado:T',
        y=alt.Y('Promedio_Ponderado', title='Promedio de Peso'),
        color=alt.Color('Nombre:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue']), title='Persona'),
        tooltip=['Nombre', 'Dia', 'Promedio_Ponderado']
    ).properties(
        title="Promedio de Peso Levantado"
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Gráfico de total de repeticiones
    bar_chart = alt.Chart(resultado_final).mark_bar().encode(
        x='Dia_ordenado:T',
        y=alt.Y('Suma_Repeticiones', title='Total de Repeticiones'),
        color=alt.Color('Nombre:N', scale=alt.Scale(domain=['Carlos', 'Cinthia'], range=['black', 'lightblue']), title='Persona'),
        tooltip=['Nombre', 'Dia', 'Suma_Repeticiones']
    ).properties(
        title="Total de Repeticiones"
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # Gráficos por grupo muscular
    if 'Grupo_Muscular' in df_grupo.columns:
        grupos_musculares = df_grupo['Grupo_Muscular'].unique().tolist()
        for grupo in grupos_musculares:
            df_grupo_grupo = df_grupo[df_grupo['Grupo_Muscular'] == grupo]
            if not df_grupo_grupo.empty:
                grafica_grupo_muscular = alt.Chart(df_grupo_grupo).mark_line().encode(
                    x='Dia_ordenado:T',
                    y='Peso:Q',
                    color='Nombre:N',
                    tooltip=['Dia', 'Peso', 'Nombre']
                ).properties(
                    title=f"Progreso por {grupo}"
                )
                st.altair_chart(grafica_grupo_muscular, use_container_width=True)
            else:
                st.warning(f"No hay suficientes datos disponibles para mostrar el gráfico de {grupo}.")
    else:
        st.warning("No se encontró la columna 'Grupo_Muscular' en el DataFrame.")


def calcular_metricas(df):
    df = df.copy()
    df['Peso_Total'] = df['Peso'] * df['Repeticiones'] * df['Sets']
    volumen = df.groupby('Id_Usuario')['Peso_Total'].sum().reset_index(name='Volumen')
    record = df.groupby(['Id_Usuario', 'Maquina'])['Peso'].max().reset_index(name='Record_Peso')
    dias_totales = df['Dia'].astype(str).nunique()
    dias = df.groupby('Id_Usuario')['Dia'].nunique().reset_index(name='Dias_Entrenados')
    dias['Consistencia'] = (dias['Dias_Entrenados'] / dias_totales * 100).round(2)
    return volumen, record, dias[['Id_Usuario', 'Consistencia']]


# Título de la aplicación
st.title('🏋️‍♂️ Nuestro Progreso en el Gym 🏋️‍♀️')

# Formulario desplegable y botón de guardar
with st.expander('📝 Registro de Datos'):
    Dia = st.text_input('Ingresa el Día 📆:')
    Persona = st.session_state['usuario']
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
                'Id_Usuario': st.session_state['id_usuario'],
                'Maquina': [Maquina] * Sets,
                'Sets': [Sets] * Sets,
                'Peso': pesos,
                'Repeticiones': repeticiones,
                'Descanso': descansos
            })
            progreso_df = pd.concat([progreso_df, progreso_new], ignore_index=True)
            progreso_df.to_csv(DATA_DIR / 'Progreso.csv', index=False)
            st.success('¡Datos registrados con éxito!')
            st.markdown(download_csv(progreso_df, 'Progreso_Actualizado'), unsafe_allow_html=True)

# Visualización de datos registrados
with st.expander('📓 Datos Registrados'):
    st.subheader("Visualización de datos registrados")
    datos_visualizacion = progreso_df[['Dia', 'Nombre', 'Maquina', 'Sets', 'Repeticiones']]
    st.dataframe(datos_visualizacion)
    st.markdown(download_csv(progreso_df, 'Progreso_Completo'), unsafe_allow_html=True)

# Visualización de gráficos
with st.expander('📊 Visualización de Gráficos'):
    st.subheader("Datos de Gráficos por Persona y Maquina")
    opcion_persona = st.selectbox('Selecciona una persona para graficar:', usuario_df['Nombre'].unique())
    progreso_persona = progreso_df[progreso_df['Nombre'] == opcion_persona]
    crear_graficos(progreso_persona, colores={'Carlos': 'black', 'Cinthia': 'lightblue'})
    
    # Gráficos por grupo muscular
    st.subheader("Datos de Gráficos por Grupo Muscular")
    if 'Grupo_Muscular' in progreso_df.columns:
        grupos_musculares = progreso_df['Grupo_Muscular'].unique().tolist()
        for grupo in grupos_musculares:
            st.write(f"Grupo Muscular: {grupo}")
            progreso_grupo = progreso_df[progreso_df['Grupo_Muscular'] == grupo]
            crear_graficos(progreso_grupo, colores={'Carlos': 'black', 'Cinthia': 'lightblue'})
    else:
        st.warning("No hay suficientes datos disponibles para mostrar los gráficos por grupo muscular.")

with st.expander('📈 Métricas de Progreso'):
    vol, rec, cons = calcular_metricas(progreso_df)
    st.subheader('Volumen Total')
    st.dataframe(vol)
    st.subheader('Récords Personales')
    st.dataframe(rec)
    st.subheader('Consistencia (%)')
    st.dataframe(cons)

with st.expander('🛠️ Administrar ejercicios'):
    st.subheader('Catálogo de Ejercicios')
    edited = st.experimental_data_editor(grupo_muscular_df, num_rows="dynamic")
    if st.button('Guardar Catálogo'):
        edited.to_csv(DATA_DIR / 'Grupo_muscular.csv', index=False)
        grupo_muscular_df = edited
        st.success('Catálogo actualizado')
