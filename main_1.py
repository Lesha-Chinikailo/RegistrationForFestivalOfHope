import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


# --- НАСТРОЙКА ПОДКЛЮЧЕНИЯ ---
def connect_to_sheet():
    # Путь к вашему файлу ключей JSON
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
        client = gspread.authorize(creds)
        # Убедитесь, что название таблицы совпадает с вашей в Google Drive
        sheet = client.open("База_Участников_Май").sheet1
        return sheet
    except Exception as e:
        st.error(f"Ошибка подключения: {e}")
        return None


# Настройка страницы для мобильных устройств
st.set_page_config(page_title="Май 16-17", layout="centered")

# Кастомный дизайн кнопок
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #28a745; color: white; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #f0f2f6; 
        border-radius: 10px 10px 0px 0px; 
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

sheet = connect_to_sheet()

if sheet:
    st.title("📱 Управление списком")

    # Создаем три вкладки: Добавление, Просмотр, Экспорт
    tab1, tab2, tab3 = st.tabs(["➕ Добавить", "📋 Список", "📤 Экспорт"])

    # --- ВКЛАДКА 1: ДОБАВЛЕНИЕ ---
    with tab1:
        st.subheader("Новый участник")
        with st.form("add_user", clear_on_submit=True):
            f = st.text_input("Фамилия")
            i = st.text_input("Имя")
            o = st.text_input("Отчество")
            phone = st.text_input("Номер телефона")
            day = st.radio("Дата:", ["16 мая", "17 мая"], horizontal=True)

            submitted = st.form_submit_button("СОХРАНИТЬ")

            if submitted:
                if f and i and phone:
                    sheet.append_row([f, i, o, phone, day])
                    st.success(f"✅ {f} {i} успешно добавлен!")
                else:
                    st.error("Заполните ФИО и телефон!")

    # --- ВКЛАДКА 2: ПРОСМОТР И СОРТИРОВКА ---
    with tab2:
        st.subheader("Все записи")
        raw_data = sheet.get_all_records()
        if raw_data:
            df = pd.DataFrame(raw_data)

            # Сортировка (удобно для больших списков)
            sort_col = st.selectbox("Сортировать по:", df.columns)
            df = df.sort_values(by=sort_col)

            st.dataframe(df, use_container_width=True)

            if st.button("🔄 Обновить список"):
                st.rerun()
        else:
            st.info("Таблица пуста")

    # --- ВКЛАДКА 3: ЭКСПОРТ ДЛЯ ГРУППЫ ---
    with tab3:
        st.subheader("Подготовка списка для группы")
        raw_data = sheet.get_all_records()

        if raw_data:
            df = pd.DataFrame(raw_data)

            # Выбор того, что экспортируем
            export_mode = st.radio(
                "Что копируем?",
                ["Все дни", "Только 16 мая", "Только 17 мая"],
                horizontal=True
            )

            # Фильтрация
            if export_mode == "Только 16 мая":
                filtered_df = df[df['Дата визита'] == "16 мая"]
                header_text = "*Список на 16 мая:*\n"
            elif export_mode == "Только 17 мая":
                filtered_df = df[df['Дата визита'] == "17 мая"]
                header_text = "*Список на 17 мая:*\n"
            else:
                filtered_df = df
                header_text = "*Полный список (16-17 мая):*\n"

            # Формирование текста
            export_text = header_text
            for idx, row in enumerate(filtered_df.values, 1):
                # row[0]-Фамилия, row[1]-Имя, row[2]-Отчество, row[3]-Телефон, row[4]-Дата
                export_text += f"{idx}. {row[0]} {row[1]} — {row[3]} ({row[4]})\n"

            # Поле с текстом, которое легко скопировать
            st.text_area("Скопируйте текст ниже:", value=export_text, height=300)
            st.info("👆 Нажмите на поле, выделите всё и скопируйте для отправки в Telegram/WhatsApp.")

        else:
            st.warning("Нет данных для экспорта.")

else:
    st.error("Не удалось подключиться к Google Таблице. Проверьте файл keys.json")