import pandas as pd
import streamlit as st
import altair as alt

USUARIOS_CSV = 'data/Usuarios.csv'
PROGRESO_CSV = 'data/Progreso.csv'
CATALOGO_CSV = 'data/Grupo_muscular.csv'


def load_dfs():
    cols = ['Dia', 'Id_Usuario', 'Ejercicio', 'Peso', 'Sets',
            'Repeticiones', 'Unidad', 'Distancia', 'Tipo', 'Tiempo']
    try:
        progreso = pd.read_csv(PROGRESO_CSV)
        for c in cols:
            if c not in progreso.columns:
                progreso[c] = None
        progreso = progreso[cols]
    except FileNotFoundError:
        progreso = pd.DataFrame(columns=cols)
    try:
        catalogo = pd.read_csv(CATALOGO_CSV)
        if 'Tipo' not in catalogo.columns:
            catalogo['Tipo'] = 'Gimnasio'
    except FileNotFoundError:
        catalogo = pd.DataFrame(columns=['Grupo_Muscular', 'Ejercicio', 'Tipo'])
    try:
        usuarios = pd.read_csv(USUARIOS_CSV)
    except FileNotFoundError:
        usuarios = pd.DataFrame(columns=['Id_Usuario', 'Nombre', 'Color', 'Username', 'Password'])
    return progreso, catalogo, usuarios


def save_df(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)


progreso_df, grupo_muscular_df, usuario_df = load_dfs()


# ------ Autenticación ------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None


def login_form():
    st.header('Iniciar sesión')
    user = st.text_input('Usuario')
    pwd = st.text_input('Contraseña', type='password')
    if st.button('Ingresar'):
        row = usuario_df[(usuario_df['Username'] == user) & (usuario_df['Password'] == pwd)]
        if not row.empty:
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = row.iloc[0]['Id_Usuario']
            try:
                st.experimental_rerun()
            except Exception:
                pass
        else:
            st.error('Credenciales inválidas')


def register_form():
    st.header('Registro')
    name = st.text_input('Nombre para mostrar')
    user = st.text_input('Usuario', key='reg_user')
    pwd = st.text_input('Contraseña', type='password', key='reg_pwd')
    if st.button('Registrar'):
        if user in usuario_df['Username'].values:
            st.error('El usuario ya existe')
        else:
            new_id = f'U{len(usuario_df) + 1}'
            new_row = {'Id_Usuario': new_id, 'Nombre': name, 'Color': 'gray', 'Username': user, 'Password': pwd}
            usuario_df.loc[len(usuario_df)] = new_row
            save_df(usuario_df, USUARIOS_CSV)
            st.success('Usuario registrado, ahora puede iniciar sesión')


def logout():
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    try:
        st.experimental_rerun()
    except Exception:
        pass


if not st.session_state['authenticated']:
    login_form()
    st.divider()
    register_form()
    st.stop()


usuario_actual = usuario_df[usuario_df['Id_Usuario'] == st.session_state['user_id']].iloc[0]
st.sidebar.write(f"Usuario: {usuario_actual['Nombre']}")
st.sidebar.button('Cerrar sesión', on_click=logout)

st.title('🏋️‍♂️ Registro de Entrenamiento')

# ------ Catálogo de Ejercicios ------
with st.expander('📚 Catálogo de Ejercicios'):
    st.dataframe(grupo_muscular_df)
    with st.form('add_exercise'):
        grupo = st.text_input('Grupo Muscular')
        ejercicio = st.text_input('Ejercicio')
        tipo_ej = st.selectbox('Tipo', ['Gimnasio', 'Carrera'])
        submitted = st.form_submit_button('Agregar')
        if submitted and grupo and ejercicio:
            grupo_muscular_df.loc[len(grupo_muscular_df)] = [grupo, ejercicio, tipo_ej]
            save_df(grupo_muscular_df, CATALOGO_CSV)
            try:
                st.experimental_rerun()
            except Exception:
                pass
    if not grupo_muscular_df.empty:
        borrar = st.selectbox('Eliminar ejercicio', grupo_muscular_df['Ejercicio'].unique())
        if st.button('Eliminar'):
            grupo_muscular_df = grupo_muscular_df[grupo_muscular_df['Ejercicio'] != borrar]
            save_df(grupo_muscular_df, CATALOGO_CSV)
            try:
                st.experimental_rerun()
            except Exception:
                pass

# ------ Registro de entrenamiento ------
with st.expander('📝 Registrar Entrenamiento'):
    tipo = st.selectbox('Tipo', ['Gimnasio', 'Carrera'])
    dia = st.text_input('Día')
    if tipo == 'Gimnasio':
        ejercicios = grupo_muscular_df[grupo_muscular_df['Tipo'] == 'Gimnasio']['Ejercicio']
        ejercicio = st.selectbox('Ejercicio', ejercicios.unique())
        sets = st.number_input('Sets', min_value=1, max_value=10, step=1, value=4)
        unidad = st.selectbox('Unidad', ['kg', 'lb'])
        peso = st.number_input('Peso', min_value=0.0, step=0.1)
        reps = st.number_input('Repeticiones', min_value=1, step=1, value=10)
        if st.button('Guardar') and dia:
            peso_kg = peso * 0.453592 if unidad == 'lb' else peso
            nuevo = pd.DataFrame({
                'Dia': [dia],
                'Id_Usuario': [st.session_state['user_id']],
                'Ejercicio': [ejercicio],
                'Peso': [peso_kg],
                'Sets': [sets],
                'Repeticiones': [reps],
                'Unidad': [unidad],
                'Distancia': [None],
                'Tipo': ['Gimnasio'],
                'Tiempo': [None]
            })
            progreso_df = pd.concat([progreso_df, nuevo], ignore_index=True)
            save_df(progreso_df, PROGRESO_CSV)
            st.success('Entrenamiento guardado')
    else:
        ejercicios = grupo_muscular_df[grupo_muscular_df['Tipo'] == 'Carrera']['Ejercicio']
        ejercicio = st.selectbox('Ejercicio', ejercicios.unique())
        distancia = st.number_input('Distancia (km)', min_value=0.0, step=0.1)
        tiempo = st.number_input('Tiempo (min)', min_value=0.0, step=1.0)
        if st.button('Guardar') and dia:
            nuevo = pd.DataFrame({
                'Dia': [dia],
                'Id_Usuario': [st.session_state['user_id']],
                'Ejercicio': [ejercicio],
                'Peso': [0],
                'Sets': [1],
                'Repeticiones': [1],
                'Unidad': ['km'],
                'Distancia': [distancia],
                'Tipo': ['Carrera'],
                'Tiempo': [tiempo]
            })
            progreso_df = pd.concat([progreso_df, nuevo], ignore_index=True)
            save_df(progreso_df, PROGRESO_CSV)
            st.success('Entrenamiento guardado')

# ------ Panel de progreso ------
with st.expander('📊 Progreso'):
    usuario_datos = progreso_df[progreso_df['Id_Usuario'] == st.session_state['user_id']]
    if usuario_datos.empty:
        st.info('Aún no hay datos registrados')
    else:
        gimnasio = usuario_datos[usuario_datos['Tipo'] == 'Gimnasio'].copy()
        gimnasio['Peso_kg'] = gimnasio.apply(lambda r: r['Peso'] if r['Unidad'] != 'lb' else r['Peso'] * 0.453592, axis=1)
        gimnasio['Volumen'] = gimnasio['Peso_kg'] * gimnasio['Repeticiones'] * gimnasio['Sets']
        total_volumen = gimnasio['Volumen'].sum()
        dias = usuario_datos['Dia'].nunique()
        st.metric('Volumen total', f"{total_volumen:.2f} kg")
        st.metric('Días registrados', dias)

        gimnasio['1RM'] = gimnasio['Peso_kg'] * (1 + gimnasio['Repeticiones'] / 30)
        max_1rm = gimnasio.groupby('Ejercicio')['1RM'].max().reset_index(name='Proyección 1RM')
        st.subheader('Proyección de 1RM por ejercicio')
        st.dataframe(max_1rm)

        pr = gimnasio.groupby('Ejercicio')['Peso_kg'].max().reset_index(name='PR (kg)')
        st.subheader('Récords personales')
        st.dataframe(pr)

        st.subheader('Peso promedio por ejercicio')
        promedio = gimnasio.groupby('Ejercicio')['Peso_kg'].mean().reset_index(name='Promedio (kg)')
        st.dataframe(promedio)

        grafica = alt.Chart(gimnasio).mark_line().encode(
            x='Dia:T', y='Peso_kg', color='Ejercicio'
        )
        st.altair_chart(grafica, use_container_width=True)

        gimnasio['Fecha'] = pd.to_datetime(gimnasio['Dia'], errors='coerce')
        gimnasio['Semana'] = gimnasio['Fecha'].dt.to_period('W').astype(str)
        semanal = gimnasio.groupby('Semana')['Volumen'].sum().reset_index()
        st.subheader('Volumen semanal')
        graf_sem = alt.Chart(semanal).mark_line(point=True).encode(
            x='Semana', y='Volumen'
        )
        st.altair_chart(graf_sem, use_container_width=True)

        gimnasio['Mes'] = gimnasio['Fecha'].dt.to_period('M').astype(str)
        mensual = gimnasio.groupby('Mes')['Volumen'].sum().reset_index()
        st.subheader('Volumen mensual')
        graf_mens = alt.Chart(mensual).mark_bar().encode(
            x='Mes', y='Volumen'
        )
        st.altair_chart(graf_mens, use_container_width=True)

        carreras = usuario_datos[usuario_datos['Tipo'] == 'Carrera']
        if not carreras.empty:
            total_km = carreras['Distancia'].sum()
            st.metric('Kilómetros acumulados', f"{total_km:.2f} km")
            graf_km = alt.Chart(carreras).mark_line().encode(
                x='Dia:T', y='Distancia', color='Ejercicio'
            )
            st.altair_chart(graf_km, use_container_width=True)

            carreras['Fecha'] = pd.to_datetime(carreras['Dia'], errors='coerce')
            carreras['Semana'] = carreras['Fecha'].dt.to_period('W').astype(str)
            run_sem = carreras.groupby('Semana')['Distancia'].sum().reset_index()
            st.subheader('Distancia semanal')
            graf_run_sem = alt.Chart(run_sem).mark_line(point=True).encode(
                x='Semana', y='Distancia'
            )
            st.altair_chart(graf_run_sem, use_container_width=True)

        st.subheader('Comparativa con otros usuarios')
        ejercicio_comp = st.selectbox('Ejercicio', progreso_df['Ejercicio'].unique())
        pr_usuarios = progreso_df[progreso_df['Tipo'] == 'Gimnasio']
        pr_usuarios['Peso_kg'] = pr_usuarios.apply(lambda r: r['Peso'] if r['Unidad'] != 'lb' else r['Peso'] * 0.453592, axis=1)
        comp = pr_usuarios[pr_usuarios['Ejercicio'] == ejercicio_comp]
        comp = comp.groupby('Id_Usuario')['Peso_kg'].max().reset_index()
        comp = comp.merge(usuario_df[['Id_Usuario', 'Nombre']], on='Id_Usuario')
        graf_comp = alt.Chart(comp).mark_bar().encode(x='Nombre', y='Peso_kg')
        st.altair_chart(graf_comp, use_container_width=True)

    with st.expander('🚧 En progreso'):
        st.markdown(
            '- Seguimiento de entrenamientos personalizados\n'
            '- Módulo de running con GPS\n'
            '- Notificaciones y recordatorios\n'
            '- Sincronización con plataformas de salud'
        )

