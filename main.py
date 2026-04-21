import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import os
import re

# --- НАСТРОЙКА ПОДКЛЮЧЕНИЯ К SUPABASE ---
# На Railway используем переменные окружения, а не .env файл
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def connect_to_supabase():
    """Подключение к Supabase"""
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.error("❌ Настройте SUPABASE_URL и SUPABASE_KEY в переменных окружения Railway!")
            st.info("""
            **Как настроить:**
            1. В панели Railway откройте ваш проект
            2. Перейдите во вкладку **Variables**
            3. Добавьте переменные:
               - `SUPABASE_URL` = ваш URL из Supabase
               - `SUPABASE_KEY` = ваш anon/public ключ
            4. Нажмите **Deploy**
            """)
            return None
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        st.error(f"Ошибка подключения к Supabase: {e}")
        return None


def get_all_participants(supabase):
    """Получение всех участников"""
    try:
        response = supabase.table("participants").select("*").order("id", desc=False).execute()
        return response.data
    except Exception as e:
        st.error(f"Ошибка получения данных: {e}")
        return []


def add_participant(supabase, last_name, first_name, middle_name, phone, visit_date):
    """Добавление нового участника"""
    try:
        # Очищаем телефон от нецифровых символов
        clean_phone = re.sub(r'\D', '', phone)
        data = {
            "last_name": last_name if last_name else "",
            "first_name": first_name if first_name else "",
            "middle_name": middle_name if middle_name else "",
            "phone": clean_phone,
            "visit_date": visit_date
        }
        response = supabase.table("participants").insert(data).execute()
        return True, response.data
    except Exception as e:
        return False, str(e)


def update_participant(supabase, participant_id, last_name, first_name, middle_name, phone, visit_date):
    """Обновление данных участника"""
    try:
        clean_phone = re.sub(r'\D', '', phone)
        data = {
            "last_name": last_name if last_name else "",
            "first_name": first_name if first_name else "",
            "middle_name": middle_name if middle_name else "",
            "phone": clean_phone,
            "visit_date": visit_date
        }
        response = supabase.table("participants").update(data).eq("id", participant_id).execute()
        return True, response.data
    except Exception as e:
        return False, str(e)


def delete_participant(supabase, participant_id):
    """Удаление участника"""
    try:
        response = supabase.table("participants").delete().eq("id", participant_id).execute()
        return True
    except Exception as e:
        return False


def format_phone_display(phone):
    """Форматирование телефона для отображения"""
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 12 and digits.startswith('375'):
        return f"+{digits[:3]} ({digits[3:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:12]}"
    elif len(digits) == 11 and digits.startswith('375'):
        return f"+{digits[:3]} ({digits[3:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:11]}"
    return phone


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
    div[data-testid="stExpander"] details {
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

# Подключаемся к Supabase
supabase = connect_to_supabase()

if supabase:
    st.title("🎪 Фестиваль Надежды")
    st.caption("16-17 мая 2026 | Регистрация участников")

    # Создаем вкладки
    tab1, tab2, tab3, tab4 = st.tabs(
        ["➕ Добавить участника", "📋 Список участников", "✏️ Редактировать", "📤 Экспорт для группы"])

    # --- ВКЛАДКА 1: ДОБАВЛЕНИЕ ---
    with tab1:
        st.subheader("📝 Регистрация нового участника")

        st.info("ℹ️ Для регистрации достаточно указать номер телефона. Остальные поля — по желанию.")
        st.caption("📱 Примеры: 80291234567, 291234567, +375291234567")

        with st.form("add_user", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                f = st.text_input("Фамилия (необязательно)", placeholder="Иванов")
            with col2:
                i = st.text_input("Имя (необязательно)", placeholder="Иван")

            o = st.text_input("Отчество (необязательно)", placeholder="Иванович")
            phone = st.text_input("Номер телефона *", placeholder="+375 (29) 123-45-67")

            day = st.radio("Выберите дату участия:", ["16 мая", "17 мая"], horizontal=True)

            st.caption("* — обязательные поля (только телефон)")

            submitted = st.form_submit_button("✅ СОХРАНИТЬ", use_container_width=True)

            if submitted:
                if phone:
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

        col_refresh, col_stats = st.columns([1, 3])
        with col_refresh:
            refresh = st.button("🔄 Обновить список", use_container_width=True)
            if refresh:
                st.rerun()

        participants = get_all_participants(supabase)

        if participants:
            df = pd.DataFrame(participants)

            with col_stats:
                total_16 = len(df[df['visit_date'] == '16 мая'])
                total_17 = len(df[df['visit_date'] == '17 мая'])
                st.info(f"📊 Всего: **{len(participants)}** | 16 мая: **{total_16}** | 17 мая: **{total_17}**")

            df_display = df.copy()
            df_display['last_name'] = df_display['last_name'].replace('', '—')
            df_display['first_name'] = df_display['first_name'].replace('', '—')
            df_display['middle_name'] = df_display['middle_name'].replace('', '—')
            df_display['phone_display'] = df_display['phone'].apply(format_phone_display)

            df_display = df_display.rename(columns={
                'id': 'ID',
                'last_name': 'Фамилия',
                'first_name': 'Имя',
                'middle_name': 'Отчество',
                'phone_display': 'Телефон',
                'visit_date': 'Дата',
                'created_at': 'Зарегистрирован'
            })

            display_columns = ['ID', 'Фамилия', 'Имя', 'Отчество', 'Телефон', 'Дата']
            df_display = df_display[display_columns]

            sort_by = st.selectbox("Сортировать по:", ['ID', 'Фамилия', 'Имя', 'Дата', 'Телефон'])
            df_display = df_display.sort_values(by=sort_by)

            st.dataframe(df_display, use_container_width=True, height=500)
        else:
            st.info("📭 Пока нет зарегистрированных участников. Добавьте первого участника во вкладке 'Добавить'.")

    # --- ВКЛАДКА 3: РЕДАКТИРОВАНИЕ ---
    with tab3:
        st.subheader("✏️ Редактирование и удаление участников")

        participants = get_all_participants(supabase)

        if participants:
            participant_options = {}
            for p in participants:
                name = f"{p['last_name']} {p['first_name']}".strip()
                if not name:
                    name = f"Участник {format_phone_display(p['phone'])}"
                participant_options[f"{name} (ID: {p['id']})"] = p

            selected_key = st.selectbox(
                "Выберите участника для редактирования:",
                list(participant_options.keys())
            )

            selected = participant_options[selected_key]

            with st.form("edit_participant", clear_on_submit=False):
                st.markdown(f"**Редактирование участника ID: {selected['id']}**")

                col1, col2 = st.columns(2)
                with col1:
                    edit_last_name = st.text_input("Фамилия", value=selected.get('last_name', ''))
                with col2:
                    edit_first_name = st.text_input("Имя", value=selected.get('first_name', ''))

                edit_middle_name = st.text_input("Отчество", value=selected.get('middle_name', ''))
                edit_phone = st.text_input("Номер телефона *", value=format_phone_display(selected.get('phone', '')))
                edit_date = st.radio("Дата участия:", ["16 мая", "17 мая"],
                                     index=0 if selected.get('visit_date') == "16 мая" else 1)

                col_save, col_delete = st.columns(2)

                with col_save:
                    save_button = st.form_submit_button("💾 СОХРАНИТЬ ИЗМЕНЕНИЯ", use_container_width=True)

                with col_delete:
                    delete_button = st.form_submit_button("🗑️ УДАЛИТЬ УЧАСТНИКА", use_container_width=True)

                if save_button:
                    if edit_phone:
                        success, result = update_participant(
                            supabase, selected['id'], edit_last_name, edit_first_name,
                            edit_middle_name, edit_phone, edit_date
                        )
                        if success:
                            st.success(f"✅ Данные участника успешно обновлены!")
                            st.rerun()
                        else:
                            st.error(f"❌ Ошибка при обновлении: {result}")
                    else:
                        st.error("❌ Номер телефона обязателен!")

                if delete_button:
                    st.warning("⚠️ Вы уверены? Это действие нельзя отменить!")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ ДА, УДАЛИТЬ"):
                            success = delete_participant(supabase, selected['id'])
                            if success:
                                st.success(f"✅ Участник удален!")
                                st.rerun()
                            else:
                                st.error("❌ Ошибка при удалении")
                    with col_cancel:
                        if st.button("❌ НЕТ, ОТМЕНА"):
                            st.info("Удаление отменено")
        else:
            st.info("📭 Нет участников для редактирования")

    # --- ВКЛАДКА 4: ЭКСПОРТ ---
    with tab4:
        st.subheader("📤 Подготовка списка для отправки в Telegram/WhatsApp")

        participants = get_all_participants(supabase)

        if participants:
            df = pd.DataFrame(participants)
            df['phone_formatted'] = df['phone'].apply(format_phone_display)

            export_mode = st.radio(
                "Что копируем?",
                ["📅 Все дни", "📆 Только 16 мая", "📆 Только 17 мая"],
                horizontal=True,
                index=0
            )

            if export_mode == "📆 Только 16 мая":
                filtered_df = df[df['visit_date'] == "16 мая"]
                header_text = "🎪 *СПИСОК УЧАСТНИКОВ НА 16 МАЯ:*\n━" * 30 + "\n\n"
            elif export_mode == "📆 Только 17 мая":
                filtered_df = df[df['visit_date'] == "17 мая"]
                header_text = "🎪 *СПИСОК УЧАСТНИКОВ НА 17 МАЯ:*\n━" * 30 + "\n\n"
            else:
                filtered_df = df
                header_text = "🎪 *ПОЛНЫЙ СПИСОК УЧАСТНИКОВ (16-17 мая):*\n━" * 30 + "\n\n"

            if not filtered_df.empty:
                export_text = header_text

                if export_mode == "📅 Все дни":
                    for date in ["16 мая", "17 мая"]:
                        date_df = filtered_df[filtered_df['visit_date'] == date]
                        if not date_df.empty:
                            export_text += f"\n📌 *{date}*\n" + "─" * 20 + "\n"
                            for idx, row in date_df.iterrows():
                                name = f"{row['last_name']} {row['first_name']}".strip()
                                if not name:
                                    name = "Участник"
                                if row['middle_name']:
                                    name += f" {row['middle_name']}"
                                export_text += f"{idx + 1}. {name} — {row['phone_formatted']}\n"
                            export_text += "\n"
                else:
                    for idx, row in filtered_df.iterrows():
                        name = f"{row['last_name']} {row['first_name']}".strip()
                        if not name:
                            name = "Участник"
                        if row['middle_name']:
                            name += f" {row['middle_name']}"
                        export_text += f"{idx + 1}. {name} — {row['phone_formatted']}\n"

                export_text += "\n" + "━" * 30 + "\n"
                export_text += f"📊 *Итого: {len(filtered_df)} участников*"

                st.text_area(
                    "📋 Скопируйте текст ниже (нажмите Ctrl+A, затем Ctrl+C):",
                    value=export_text,
                    height=400,
                    help="Выделите весь текст и скопируйте для отправки в мессенджер"
                )

                st.info("💡 **Совет:** Нажмите на поле выше, затем Ctrl+A (выделить всё) и Ctrl+C (скопировать)")

                csv = filtered_df[['last_name', 'first_name', 'middle_name', 'phone', 'visit_date']].to_csv(index=False)
                st.download_button(
                    label="📥 Скачать как CSV файл",
                    data=csv,
                    file_name=f"participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning(f"⚠️ Нет участников для выбранной даты")
        else:
            st.warning("📭 Нет данных для экспорта. Добавьте участников во вкладке 'Добавить'.")

else:
    st.error("""
        ❌ **Не удалось подключиться к Supabase**

        **Проверьте настройки в Railway:**
        1. Перейдите в ваш проект на Railway
        2. Откройте вкладку **Variables**
        3. Добавьте переменные окружения:
           - `SUPABASE_URL` = ваш URL из Supabase
           - `SUPABASE_KEY` = ваш anon/public ключ
        4. Нажмите **Deploy**

        **Не забудьте создать таблицу в Supabase:**
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

        ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
        CREATE POLICY "Allow all" ON participants FOR ALL USING (true);
""")