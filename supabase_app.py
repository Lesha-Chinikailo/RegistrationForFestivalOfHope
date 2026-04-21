import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# --- НАСТРОЙКА ПОДКЛЮЧЕНИЯ К SUPABASE ---
# Данные для подключения (нужно будет заменить на свои)
# Получить их можно в настройках проекта Supabase: Settings -> API
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def connect_to_supabase():
    """Подключение к Supabase"""
    try:
        if not SUPABASE_URL or "ваш_проект" in SUPABASE_URL:
            st.error("❌ Настройте SUPABASE_URL и SUPABASE_KEY в коде!")
            return None
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        st.error(f"Ошибка подключения к Supabase: {e}")
        return None


def get_all_participants(supabase):
    """Получение всех участников"""
    try:
        response = supabase.table("participants").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Ошибка получения данных: {e}")
        return []


def add_participant(supabase, last_name, first_name, middle_name, phone, visit_date):
    """Добавление нового участника"""
    try:
        data = {
            "last_name": last_name if last_name else "",
            "first_name": first_name if first_name else "",
            "middle_name": middle_name if middle_name else "",
            "phone": phone,
            "visit_date": visit_date
        }
        response = supabase.table("participants").insert(data).execute()
        return True, response.data
    except Exception as e:
        return False, str(e)


def delete_participant(supabase, participant_id):
    """Удаление участника (опционально)"""
    try:
        response = supabase.table("participants").delete().eq("id", participant_id).execute()
        return True
    except Exception as e:
        return False


# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Фестиваль Надежды - Май 16-17", layout="centered", page_icon="🎪")

# Кастомный дизайн
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #28a745; 
        color: white; 
        font-weight: bold; 
        font-size: 16px;
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
    </style>
    """, unsafe_allow_html=True)

# Подключаемся к Supabase
supabase = connect_to_supabase()

if supabase:
    st.title("🎪 Фестиваль Надежды")
    st.caption("16-17 мая 2026 | Регистрация участников")

    # Создаем три вкладки
    tab1, tab2, tab3 = st.tabs(["➕ Добавить участника", "📋 Список участников", "📤 Экспорт для группы"])

    # --- ВКЛАДКА 1: ДОБАВЛЕНИЕ ---
    with tab1:
        st.subheader("📝 Регистрация нового участника")

        st.info("ℹ️ Для регистрации достаточно указать номер телефона. Остальные поля — по желанию.")

        with st.form("add_user", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                f = st.text_input("Фамилия (необязательно)", placeholder="Иванов")
            with col2:
                i = st.text_input("Имя (необязательно)", placeholder="Иван")

            o = st.text_input("Отчество (необязательно)", placeholder="Иванович")
            phone = st.text_input("Номер телефона *", placeholder="+7 (999) 123-45-67")

            day = st.radio("Выберите дату участия:", ["16 мая", "17 мая"], horizontal=True)

            st.caption("* — обязательные поля (только телефон)")

            submitted = st.form_submit_button("✅ СОХРАНИТЬ", use_container_width=True)

            if submitted:
                if phone:  # Только телефон обязателен
                    success, result = add_participant(supabase, f, i, o, phone, day)
                    if success:
                        if f and i:
                            st.success(f"✅ {f} {i} успешно добавлен(а) в список!")
                        else:
                            st.success(f"✅ Участник с номером {phone} успешно добавлен(а) в список!")
                        st.balloons()
                    else:
                        st.error(f"❌ Ошибка при добавлении: {result}")
                else:
                    st.error("❌ Пожалуйста, укажите номер телефона (это обязательное поле)")

    # --- ВКЛАДКА 2: ПРОСМОТР ---
    with tab2:
        st.subheader("📋 Все зарегистрированные участники")

        # Кнопка обновления
        col_refresh, col_stats = st.columns([1, 3])
        with col_refresh:
            refresh = st.button("🔄 Обновить", use_container_width=True)
            if refresh:
                st.rerun()

        # Получаем данные
        participants = get_all_participants(supabase)

        if participants:
            # Создаем DataFrame для отображения
            df = pd.DataFrame(participants)

            # Переименовываем колонки для красивого отображения
            df_display = df.rename(columns={
                'last_name': 'Фамилия',
                'first_name': 'Имя',
                'middle_name': 'Отчество',
                'phone': 'Телефон',
                'visit_date': 'Дата визита',
                'created_at': 'Дата регистрации'
            })

            # Заменяем пустые значения на прочерк
            df_display['Фамилия'] = df_display['Фамилия'].replace('', '—')
            df_display['Имя'] = df_display['Имя'].replace('', '—')
            df_display['Отчество'] = df_display['Отчество'].replace('', '—')

            # Выбираем колонки для отображения
            display_columns = ['Фамилия', 'Имя', 'Отчество', 'Телефон', 'Дата визита']
            df_display = df_display[display_columns]

            # Статистика
            with col_stats:
                total_16 = len(df[df['visit_date'] == '16 мая'])
                total_17 = len(df[df['visit_date'] == '17 мая'])
                st.info(f"📊 Всего: **{len(participants)}** | 16 мая: **{total_16}** | 17 мая: **{total_17}**")

            # Сортировка
            sort_by = st.selectbox("Сортировать по:", ["Фамилия", "Имя", "Дата визита", "Телефон"])
            df_display = df_display.sort_values(by=sort_by)

            # Отображение таблицы
            st.dataframe(df_display, use_container_width=True, height=400)

        else:
            st.info("📭 Пока нет зарегистрированных участников. Добавьте первого участника во вкладке 'Добавить'.")

    # --- ВКЛАДКА 3: ЭКСПОРТ ---
    with tab3:
        st.subheader("📤 Подготовка списка для отправки в Telegram/WhatsApp")

        participants = get_all_participants(supabase)

        if participants:
            df = pd.DataFrame(participants)

            # Выбор даты для экспорта
            export_mode = st.radio(
                "Что копируем?",
                ["📅 Все дни", "📆 Только 16 мая", "📆 Только 17 мая"],
                horizontal=True,
                index=0
            )

            # Фильтрация
            if export_mode == "📆 Только 16 мая":
                filtered_df = df[df['visit_date'] == "16 мая"]
                header_text = "🎪 *СПИСОК УЧАСТНИКОВ НА 16 МАЯ:*\n"
                header_text += "━" * 30 + "\n\n"
            elif export_mode == "📆 Только 17 мая":
                filtered_df = df[df['visit_date'] == "17 мая"]
                header_text = "🎪 *СПИСОК УЧАСТНИКОВ НА 17 МАЯ:*\n"
                header_text += "━" * 30 + "\n\n"
            else:
                filtered_df = df
                header_text = "🎪 *ПОЛНЫЙ СПИСОК УЧАСТНИКОВ (16-17 мая):*\n"
                header_text += "━" * 30 + "\n\n"

            # Формирование текста
            if not filtered_df.empty:
                export_text = header_text

                # Группировка по датам если выбран "Все дни"
                if export_mode == "📅 Все дни":
                    for date in ["16 мая", "17 мая"]:
                        date_df = filtered_df[filtered_df['visit_date'] == date]
                        if not date_df.empty:
                            export_text += f"\n📌 *{date}*\n"
                            export_text += "─" * 20 + "\n"
                            for idx, row in date_df.iterrows():
                                # Формируем имя, если есть
                                if row['last_name'] or row['first_name']:
                                    name = f"{row['last_name']} {row['first_name']}".strip()
                                    if row['middle_name']:
                                        name += f" {row['middle_name']}"
                                else:
                                    name = "Участник"
                                export_text += f"{idx + 1}. {name} — {row['phone']}\n"
                            export_text += "\n"
                else:
                    # Для одного дня
                    for idx, row in filtered_df.iterrows():
                        # Формируем имя, если есть
                        if row['last_name'] or row['first_name']:
                            name = f"{row['last_name']} {row['first_name']}".strip()
                            if row['middle_name']:
                                name += f" {row['middle_name']}"
                        else:
                            name = "Участник"
                        export_text += f"{idx + 1}. {name} — {row['phone']}\n"

                # Добавляем статистику
                export_text += "\n" + "━" * 30 + "\n"
                export_text += f"📊 *Итого: {len(filtered_df)} участников*"

                # Поле для копирования
                st.text_area(
                    "📋 Скопируйте текст ниже (нажмите Ctrl+A, затем Ctrl+C):",
                    value=export_text,
                    height=400,
                    help="Выделите весь текст и скопируйте для отправки в мессенджер"
                )

                # Кнопка для копирования (подсказка)
                st.info("💡 **Совет:** Нажмите на поле выше, затем Ctrl+A (выделить всё) и Ctrl+C (скопировать)")

                # Дополнительная кнопка для экспорта в CSV
                csv = filtered_df[['last_name', 'first_name', 'middle_name', 'phone', 'visit_date']].to_csv(index=False)
                st.download_button(
                    label="📥 Скачать как CSV файл",
                    data=csv,
                    file_name=f"participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning(f"⚠️ Нет участников для выбранной даты ({export_mode})")
        else:
            st.warning("📭 Нет данных для экспорта. Добавьте участников во вкладке 'Добавить'.")

else:
    st.error("""
        ❌ **Не удалось подключиться к Supabase**

        **Проверьте настройки:**
        1. Зарегистрируйтесь на [supabase.com](https://supabase.com) (бесплатно, через GitHub)
        2. Создайте новый проект
        3. В разделе Settings -> API скопируйте:
           - Project URL (supabase_url)
           - anon/public key (supabase_key)
        4. Вставьте эти значения в переменные SUPABASE_URL и SUPABASE_KEY в коде
        5. Создайте таблицу через SQL Editor:

        ```sql
        CREATE TABLE participants (
            id SERIAL PRIMARY KEY,
            last_name TEXT,
            first_name TEXT,
            middle_name TEXT,
            phone TEXT NOT NULL,
            visit_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
""")