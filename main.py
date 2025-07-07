import pandas as pd
import streamlit as st
import altair as alt
from datetime import date

st.set_page_config(
    page_title="Gym & Running Tracker",
    page_icon="🏃",
    layout="centered",
)

# Simple styling for better UX
st.markdown(
    """
    <style>
        body {font-family: 'Segoe UI', sans-serif; background-color: var(--backgr\
ound-color);} 
        .block-container {padding-top: 2rem;}
        [data-testid=stMetric] {background:#222;border-radius:4px;padding:0.5em;\
 color:#fff;}
    </style>
    """,
    unsafe_allow_html=True,
)

USUARIOS_CSV = 'data/Usuarios.csv'
PROGRESO_CSV = 'data/Progreso.csv'
CATALOGO_CSV = 'data/Grupo_muscular.csv'


def load_dfs():
    cols = ['Dia', 'Id_Usuario', 'Ejercicio', 'Peso', 'Sets',
            'Repeticiones', 'Unidad', 'Distancia', 'Tipo', 'Tiempo', 'Notas']
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


def auth_tabs():
    tabs = st.tabs(['Iniciar sesión', 'Registro'])

    with tabs[0]:
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

    with tabs[1]:
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
                st.success('Usuario registrado')


def logout():
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    try:
        st.experimental_rerun()
    except Exception:
        pass


if not st.session_state['authenticated']:
    auth_tabs()
    st.stop()

usuario_actual = usuario_df[usuario_df['Id_Usuario'] == st.session_state['user_id']].iloc[0]
st.sidebar.write(f"Usuario: {usuario_actual['Nombre']}")
st.sidebar.button('Cerrar sesión', on_click=logout)

rem_date = st.sidebar.date_input(
    'Próximo entrenamiento',
    st.session_state.get('next_workout', date.today())
)
if st.sidebar.button('Guardar recordatorio'):
    st.session_state['next_workout'] = rem_date
    st.sidebar.success('Recordatorio guardado')
if st.session_state.get('next_workout'):
    st.sidebar.info(f"Próximo entrenamiento: {st.session_state['next_workout']}")

st.title('🏋️‍♂️ Registro de Entrenamiento')

tabs = st.tabs(['Registro', 'Progreso', 'Catálogo', 'Sincronización'])

with tabs[0]:
    st.header('📝 Registrar Entrenamiento')
    tipo = st.selectbox('Tipo', ['Gimnasio', 'Carrera'])
    dia = st.date_input('Día', date.today())
    nota = st.text_area('Notas', key='nota')
    if tipo == 'Gimnasio':
        ejercicios = grupo_muscular_df[grupo_muscular_df['Tipo'] == 'Gimnasio']['Ejercicio']
        ejercicio = st.selectbox('Ejercicio', ejercicios.unique())
        c1, c2, c3 = st.columns(3)
        with c1:
            sets = st.number_input('Sets', min_value=1, max_value=10, step=1, value=4)
        with c2:
            unidad = st.selectbox('Unidad', ['kg', 'lb'])
            peso = st.number_input('Peso', min_value=0.0, step=0.1)
        with c3:
            reps = st.number_input('Repeticiones', min_value=1, step=1, value=10)
        if st.button('Guardar') and dia:
            dia_str = dia.strftime('%Y-%m-%d') if isinstance(dia, date) else str(dia)
            nuevo = pd.DataFrame({
                'Dia': [dia_str],
                'Id_Usuario': [st.session_state['user_id']],
                'Ejercicio': [ejercicio],
                'Peso': [peso],
                'Sets': [sets],
                'Repeticiones': [reps],
                'Unidad': [unidad],
                'Distancia': [None],
                'Tipo': ['Gimnasio'],
                'Tiempo': [None],
                'Notas': [nota]
            })
            progreso_df = pd.concat([progreso_df, nuevo], ignore_index=True)
            save_df(progreso_df, PROGRESO_CSV)
            st.success('Entrenamiento guardado')
    else:
        ejercicios = grupo_muscular_df[grupo_muscular_df['Tipo'] == 'Carrera']['Ejercicio']
        ejercicio = st.selectbox('Ejercicio', ejercicios.unique())
        col1, col2 = st.columns(2)
        with col1:
            distancia = st.number_input('Distancia (km)', min_value=0.0, step=0.1)
        with col2:
            tiempo = st.number_input('Tiempo (min)', min_value=0.0, step=1.0)
        ruta = st.file_uploader('Ruta GPX/CSV (opcional)', type=['gpx', 'csv'])
        if st.button('Guardar') and dia:
            dia_str = dia.strftime('%Y-%m-%d') if isinstance(dia, date) else str(dia)
            nuevo = pd.DataFrame({
                'Dia': [dia_str],
                'Id_Usuario': [st.session_state['user_id']],
                'Ejercicio': [ejercicio],
                'Peso': [0],
                'Sets': [1],
                'Repeticiones': [1],
                'Unidad': ['km'],
                'Distancia': [distancia],
                'Tipo': ['Carrera'],
                'Tiempo': [tiempo],
                'Notas': [nota]
            })
            progreso_df = pd.concat([progreso_df, nuevo], ignore_index=True)
            save_df(progreso_df, PROGRESO_CSV)
            st.success('Entrenamiento guardado')
        if ruta is not None:
            try:
                coords = pd.read_csv(ruta)
                if {'lat', 'lon'}.issubset(coords.columns):
                    st.map(coords[['lat', 'lon']])
            except Exception:
                pass

with tabs[1]:
    st.header('📊 Progreso')
    data_user = progreso_df[progreso_df['Id_Usuario'] == st.session_state['user_id']].copy()
    if data_user.empty:
        st.info('Aún no hay datos registrados')
    else:
        data_user['Fecha'] = pd.to_datetime(data_user['Dia'], errors='coerce')
        mask1970 = data_user['Fecha'].dt.year == 1970
        if mask1970.any():
            max_day = pd.to_numeric(data_user.loc[mask1970, 'Dia'], errors='coerce').max()
            base = pd.to_datetime(date.today()) - pd.Timedelta(days=int(max_day) - 1)
            data_user.loc[mask1970, 'Fecha'] = pd.to_numeric(data_user.loc[mask1970, 'Dia'], errors='coerce').apply(
                lambda d: base + pd.Timedelta(days=int(d) - 1)
            )
        rango_opt = st.selectbox('Rango', ['Hoy', '7 días', '30 días', 'Personalizado'])
        hoy = pd.to_datetime(date.today())
        if rango_opt == 'Hoy':
            inicio, fin = hoy, hoy
        elif rango_opt == '7 días':
            inicio, fin = hoy - pd.Timedelta(days=6), hoy
        elif rango_opt == '30 días':
            inicio, fin = hoy - pd.Timedelta(days=29), hoy
        else:
            r = st.date_input(
                'Selecciona rango',
                value=[data_user['Fecha'].min(), data_user['Fecha'].max()],
            )
            if len(r) == 2:
                inicio = pd.to_datetime(r[0])
                fin = pd.to_datetime(r[1])
            else:
                inicio = data_user['Fecha'].min()
                fin = data_user['Fecha'].max()
        periodo = (fin - inicio).days + 1
        datos_periodo = data_user[(data_user['Fecha'] >= inicio) & (data_user['Fecha'] <= fin)]
        prev = data_user[(data_user['Fecha'] >= inicio - pd.Timedelta(days=periodo)) & (data_user['Fecha'] < inicio)]

        c1, c2 = st.columns(2)
        show_gym = c1.checkbox('Gimnasio', True)
        show_run = c2.checkbox('Carrera', True)
        datos_sel = datos_periodo[(datos_periodo['Tipo'] == 'Gimnasio') & show_gym | (datos_periodo['Tipo'] == 'Carrera') & show_run]

        gym = datos_sel[datos_sel['Tipo'] == 'Gimnasio'].copy()
        gym['Peso_kg'] = gym.apply(lambda r: r['Peso'] if r['Unidad'] != 'lb' else r['Peso'] * 0.453592, axis=1)
        gym['Volumen'] = gym['Peso_kg'] * gym['Repeticiones'] * gym['Sets']
        run = datos_sel[datos_sel['Tipo'] == 'Carrera']

        prev_gym = prev[prev['Tipo'] == 'Gimnasio'].copy()
        prev_gym['Peso_kg'] = prev_gym.apply(lambda r: r['Peso'] if r['Unidad'] != 'lb' else r['Peso'] * 0.453592, axis=1)
        prev_gym['Volumen'] = prev_gym['Peso_kg'] * prev_gym['Repeticiones'] * prev_gym['Sets']
        prev_run = prev[prev['Tipo'] == 'Carrera']

        total_vol = gym['Volumen'].sum()
        prev_vol = prev_gym['Volumen'].sum()
        delta_vol = total_vol - prev_vol

        total_km = run['Distancia'].sum()
        prev_km = prev_run['Distancia'].sum()
        delta_km = total_km - prev_km

        sesiones = datos_sel['Fecha'].nunique()

        gym['1RM'] = gym['Peso_kg'] * (1 + gym['Repeticiones'] / 30)
        if not gym.empty:
            pr_row = gym.loc[gym['1RM'].idxmax()]
            ultimo_pr = f"{pr_row['Ejercicio']} {pr_row['1RM']:.1f} kg"
        elif not run.empty:
            ultimo_pr = f"Distancia máx {run['Distancia'].max():.1f} km"
        else:
            ultimo_pr = '-'

        m1, m2, m3, m4 = st.columns(4)
        m1.metric('Carga total', f"{total_vol:.1f} kg", f"{delta_vol:+.1f}")
        m2.metric('Distancia', f"{total_km:.1f} km", f"{delta_km:+.1f}")
        m3.metric('Sesiones', sesiones)
        m4.metric('Último PR', ultimo_pr)

        # --- Gráficas Gimnasio ---
        if show_gym and not gym.empty:
            claves = ['Press de pecho', 'Sentadilla', 'Peso muerto']
            datos_clave = gym[gym['Ejercicio'].isin(claves)]
            if not datos_clave.empty:
                max_chart = (
                    alt.Chart(datos_clave)
                    .mark_line(point=True)
                    .encode(x='Fecha:T', y='Peso_kg', color='Ejercicio', tooltip=['Fecha', 'Peso_kg'])
                    .interactive()
                )
                st.altair_chart(max_chart, use_container_width=True)

            join = gym.merge(grupo_muscular_df[['Ejercicio', 'Grupo_Muscular']], on='Ejercicio', how='left')
            join['Semana'] = join['Fecha'].dt.to_period('W').astype(str)
            grupo_vol = join.groupby(['Semana', 'Grupo_Muscular'])['Volumen'].sum().reset_index()
            stack = alt.Chart(grupo_vol).mark_bar().encode(x='Semana', y='Volumen', color='Grupo_Muscular')
            st.altair_chart(stack, use_container_width=True)

        # --- Gráficas Running ---
        if show_run and not run.empty:
            line_dist = (
                alt.Chart(run)
                .mark_line(point=True)
                .encode(x='Fecha:T', y='Distancia', tooltip=['Fecha', 'Distancia'])
                .interactive()
            )
            st.altair_chart(line_dist, use_container_width=True)

            run = run[run['Distancia'] > 0]
            if not run.empty:
                run['ritmo'] = run['Tiempo'] / run['Distancia']
                area_pace = (
                    alt.Chart(run)
                    .mark_area(opacity=0.3)
                    .encode(x='Fecha:T', y='ritmo', tooltip=['Fecha', 'ritmo'])
                    .interactive()
                )
                st.altair_chart(area_pace, use_container_width=True)

        # --- Últimas sesiones ---
        st.subheader('Últimas sesiones')
        ultimas = datos_sel.sort_values('Fecha', ascending=False).head(10)
        st.dataframe(ultimas[['Dia', 'Ejercicio', 'Peso', 'Distancia', 'Tipo']])


with tabs[2]:
    st.header('📚 Catálogo de Ejercicios')
    st.dataframe(grupo_muscular_df)
    with st.form('add_exercise'):
        grupo = st.text_input('Grupo Muscular')
        ejercicio = st.text_input('Ejercicio')
        tipo_ej = st.selectbox('Tipo', ['Gimnasio', 'Carrera'])
        submitted = st.form_submit_button('Agregar')
        if submitted and grupo and ejercicio:
            existe = not grupo_muscular_df[
                (grupo_muscular_df['Grupo_Muscular'] == grupo) &
                (grupo_muscular_df['Ejercicio'] == ejercicio)
            ].empty
            if existe:
                st.warning('El ejercicio ya existe')
            else:
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

with tabs[3]:
    st.header('🔄 Sincronización')
    csv_data = progreso_df.to_csv(index=False).encode('utf-8')
    st.download_button('Descargar historial', csv_data, 'progreso.csv', 'text/csv')
    archivo = st.file_uploader('Importar CSV', type='csv')
    if archivo is not None:
        try:
            nuevos = pd.read_csv(archivo)
            progreso_df = pd.concat([progreso_df, nuevos], ignore_index=True)
            save_df(progreso_df, PROGRESO_CSV)
            st.success('Datos importados')
        except Exception as e:
            st.error(f'Error al importar: {e}')


