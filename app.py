import streamlit as st
import pandas as pd

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Фестиваль Надежды - Май 16-17", layout="wide", page_icon="🎪")

# Кастомный дизайн
st.markdown("""
    <style>
    .stButton>button { 
        border-radius: 8px; 
        height: 2.5em; 
        font-weight: bold; 
    }
    .stButton>button:hover {
        background-color: #218838;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
    }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #f0f2f6; 
        border-radius: 10px 10px 0px 0px; 
        padding: 10px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #28a745;
        color: white;
    }
    .stAlert {
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .copy-button {
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎪 Фестиваль Надежды")
st.caption("16-17 мая 2026 | Регистрация участников")

# --- ЗАГРУЗКА ФАЙЛА ---
st.sidebar.header("📂 Загрузка данных")
uploaded_file = st.sidebar.file_uploader(
    "Загрузите Excel файл с участниками",
    type=['xlsx', 'xls'],
    help="Файл должен содержать колонки: ФИО, номер телефона, дата (16 или 17)"
)

if uploaded_file is not None:
    try:
        # Читаем Excel файл
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Определяем названия колонок (поиск похожих названий)
        fio_col = None
        phone_col = None
        date_col = None

        for col in df.columns:
            col_lower = str(col).lower()
            if 'фио' in col_lower or 'ф и о' in col_lower or 'ф.и.о' in col_lower or 'фио' in col_lower:
                fio_col = col
            elif 'телефон' in col_lower or 'номер' in col_lower or 'phone' in col_lower or 'телефону' in col_lower:
                phone_col = col
            elif 'дата' in col_lower or 'date' in col_lower:
                date_col = col

        # Если не нашли по ключевым словам, берем по позициям (2-й, 3-й и 5-й столбцы)
        if fio_col is None and len(df.columns) > 1:
            fio_col = df.columns[1]  # Второй столбец (индекс 1)
        if phone_col is None and len(df.columns) > 2:
            phone_col = df.columns[2]  # Третий столбец (индекс 2)
        if date_col is None and len(df.columns) > 4:
            date_col = df.columns[4]  # Пятый столбец (индекс 4)

        if fio_col and phone_col and date_col:
            # Переименовываем колонки для удобства
            df_clean = pd.DataFrame()
            df_clean['ФИО'] = df[fio_col].astype(str).str.strip()
            df_clean['Телефон'] = df[phone_col].astype(str).str.strip()
            df_clean['Дата'] = df[date_col].astype(str).str.strip()

            # Удаляем строки, где нет ФИО или телефона
            df_clean = df_clean[(df_clean['ФИО'] != 'nan') & (df_clean['ФИО'] != '')]
            df_clean = df_clean[(df_clean['Телефон'] != 'nan') & (df_clean['Телефон'] != '')]


            # Обработка дат
            def process_date(date_val):
                if date_val in ['16', '16 мая', '16 мая', '16.0']:
                    return '16 мая'
                elif date_val in ['17', '17 мая', '17 мая', '17.0']:
                    return '17 мая'
                elif date_val == 'nan' or date_val == '' or date_val == 'None' or date_val == '0':
                    return 'Не указано'
                else:
                    return 'Другое'


            df_clean['Дата_норм'] = df_clean['Дата'].apply(process_date)

            # --- СТАТИСТИКА ---
            total_count = len(df_clean)
            count_16 = len(df_clean[df_clean['Дата_норм'] == '16 мая'])
            count_17 = len(df_clean[df_clean['Дата_норм'] == '17 мая'])
            count_other = len(df_clean[df_clean['Дата_норм'] == 'Не указано']) + len(
                df_clean[df_clean['Дата_норм'] == 'Другое'])

            # Отображаем статистику
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Всего участников", total_count)
            with col2:
                st.metric("📅 16 мая", count_16)
            with col3:
                st.metric("📅 17 мая", count_17)
            with col4:
                st.metric("❓ Без даты / Другое", count_other)

            # --- ВКЛАДКИ ДЛЯ СПИСКОВ ---
            tab1, tab2, tab3 = st.tabs(["📅 Список на 16 мая", "📅 Список на 17 мая", "📋 Остальные участники"])


            # Функция для создания текста списка
            def create_list_text(dataframe, title):
                text = f"🎪 *{title}*\n" + "━" * 30 + "\n\n"
                for idx, row in dataframe.iterrows():
                    name = row['ФИО']
                    # Убираем "nan" если вдруг появилось
                    if name.lower() == 'nan' or not name:
                        continue
                    text += f"{idx + 1}. {name}\n"
                text += "\n" + "━" * 30 + "\n"
                text += f"📊 *Итого: {len(dataframe)} участников*"
                return text


            # Вкладка 1 - 16 мая
            with tab1:
                st.subheader("🎯 Участники на 16 мая")

                df_16 = df_clean[df_clean['Дата_норм'] == '16 мая'].copy()
                df_16 = df_16.reset_index(drop=True)

                if not df_16.empty:
                    # Отображаем таблицу
                    st.dataframe(df_16[['ФИО', 'Телефон']], use_container_width=True)

                    # Создаем текст списка
                    list_text = create_list_text(df_16, "СПИСОК УЧАСТНИКОВ НА 16 МАЯ")

                    # Используем text_area для копирования
                    st.text_area(
                        "📋 Скопируйте список (Ctrl+A, Ctrl+C):",
                        value=list_text,
                        height=300,
                        key="copy_16",
                        help="Выделите весь текст и скопируйте"
                    )

                    st.info(f"✅ Всего на 16 мая: **{len(df_16)} участников**")
                else:
                    st.info("📭 Нет участников на 16 мая")

            # Вкладка 2 - 17 мая
            with tab2:
                st.subheader("🎯 Участники на 17 мая")

                df_17 = df_clean[df_clean['Дата_норм'] == '17 мая'].copy()
                df_17 = df_17.reset_index(drop=True)

                if not df_17.empty:
                    # Отображаем таблицу
                    st.dataframe(df_17[['ФИО', 'Телефон']], use_container_width=True)

                    # Создаем текст списка
                    list_text = create_list_text(df_17, "СПИСОК УЧАСТНИКОВ НА 17 МАЯ")

                    st.text_area(
                        "📋 Скопируйте список (Ctrl+A, Ctrl+C):",
                        value=list_text,
                        height=300,
                        key="copy_17",
                        help="Выделите весь текст и скопируйте"
                    )

                    st.info(f"✅ Всего на 17 мая: **{len(df_17)} участников**")
                else:
                    st.info("📭 Нет участников на 17 мая")

            # Вкладка 3 - Остальные (без даты или другое)
            with tab3:
                st.subheader("❓ Участники без указанной даты или с другими датами")

                df_other = df_clean[df_clean['Дата_норм'].isin(['Не указано', 'Другое'])].copy()
                df_other = df_other.reset_index(drop=True)

                if not df_other.empty:
                    # Показываем какие даты были в оригинале
                    st.caption("ℹ️ Здесь отображаются участники, у которых в колонке 'дата' не указано '16' или '17'")

                    # Отображаем таблицу с оригинальной датой
                    df_other_display = df_other[['ФИО', 'Телефон', 'Дата']].copy()
                    st.dataframe(df_other_display, use_container_width=True)

                    # Список только с ФИО
                    list_text = create_list_text(df_other, "УЧАСТНИКИ БЕЗ УКАЗАННОЙ ДАТЫ")

                    st.text_area(
                        "📋 Скопируйте список (Ctrl+A, Ctrl+C):",
                        value=list_text,
                        height=300,
                        key="copy_other",
                        help="Выделите весь текст и скопируйте"
                    )

                    st.info(f"✅ Всего без даты: **{len(df_other)} участников**")
                else:
                    st.info("📭 Нет участников без указанной даты")

            # --- ДОПОЛНИТЕЛЬНО: ПОЛНАЯ ТАБЛИЦА ---
            with st.expander("📊 Показать полную таблицу всех участников"):
                st.dataframe(df_clean[['ФИО', 'Телефон', 'Дата_норм', 'Дата']], use_container_width=True)

                # Экспорт в CSV
                csv = df_clean[['ФИО', 'Телефон', 'Дата_норм']].to_csv(index=False)
                st.download_button(
                    label="📥 Скачать полный список в CSV",
                    data=csv,
                    file_name="festival_participants.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        else:
            st.error(f"❌ Не удалось определить колонки в файле.")
            st.info(f"**Доступные колонки:** {list(df.columns)}")
            st.info("""
            **Ожидаемая структура файла:**
            - Колонка с ФИО (должна содержать слова "ФИО", "Ф.И.О" или быть второй по счету)
            - Колонка с телефоном (должна содержать слова "телефон", "номер" или быть третьей по счету)
            - Колонка с датой (должна содержать слова "дата" или быть пятой по счету)

            **Пример:** если ваш файл имеет колонки как на фото:
            - 1-й столбец: № (пропускаем)
            - 2-й столбец: ФИО (используем)
            - 3-й столбец: номер телефона (используем)
            - 4-й столбец: в группе (пропускаем)
            - 5-й столбец: дата (используем)
            - 6-й столбец: кто пригласил (пропускаем)
            """)

    except Exception as e:
        st.error(f"❌ Ошибка при чтении файла: {e}")
        st.info("Убедитесь, что файл имеет формат Excel (.xlsx или .xls) и не поврежден")

else:
    # Если файл не загружен
    st.info("👈 **Начните с загрузки Excel файла** в боковой панели")

    st.markdown("""
    ### 📋 Требования к файлу:

    1. **Формат**: Excel (.xlsx или .xls)
    2. **Структура** (как на вашем фото):
       - Столбец с ФИО (можно назвать "ФИО", "Ф.И.О" и т.д.)
       - Столбец с номером телефона (можно назвать "телефон", "номер телефона")
       - Столбец с датой (значения: "16" или "17")

    ### 📱 Как использовать:

    1. **Загрузите файл** через боковую панель
    2. **Просмотрите списки** по дням в отдельных вкладках
    3. **Скопируйте список** только с ФИО для отправки в Telegram/WhatsApp
    4. **Статистика** покажет общее количество и разбивку по дням

    ### ⚠️ Важно:
    - Файл загружается только для чтения, изменения не сохраняются
    - Если в колонке "дата" пусто или другое значение - такие участники попадают в отдельный список
    """)

    # Пример файла
    st.markdown("---")
    st.markdown("### 📝 Пример структуры файла:")
    example_df = pd.DataFrame({
        '№': [1, 2, 3],
        'ФИО': ['Иванов Иван Иванович', 'Петрова Анна Сергеевна', 'Сидоров Петр Николаевич'],
        'номер телефона': ['+375291234567', '+375293334455', '+375297778899'],
        'в группе': ['+', '', '+'],
        'дата': ['16', '17', ''],
        'кто пригласил': ['Анна', '', 'Мария']
    })
    st.dataframe(example_df, use_container_width=True)