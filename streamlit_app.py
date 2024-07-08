import datetime
import random
import mysql.connector

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="サポート・チケット", page_icon="🎫")
st.title("🎫 サポート・チケット")
st.write(
    """
    サポート チケット ワークフローの実装。ユーザーはチケットを作成、編集できます。 
    既存のチケットを確認し、統計を表示します。
    """
)

# DBへ接続
conn = mysql.connector.connect(
    user='smairuser',
    password='smairuser',
    host='www.ryhintl.com',
    database='smair',
    port=36000
)

# DBの接続確認
if not conn.is_connected():
    raise Exception("MySQLサーバへの接続に失敗しました")

cur = conn.cursor(dictionary=True)  # 取得結果を辞書型で扱う設定
#cur = conn.cursor()

query__for_fetching = """
SELECT Task_ID as ID,Task_Subject as Issue,Task_Status as Status,Task_Priority as Priority,Task_Start_Date as Date_Submitted FROM todo_tasks ORDER BY task_ID limit 20;
"""

cur.execute(query__for_fetching)

for fetched_line in cur.fetchall():
    #id = fetched_line['Task_ID']
    #name = fetched_line['Task_Subject']
    #st.write(f'{id}: {name}')

fl = cur.fetchall()
st.write(fl)

#issue_descriptions1 = []
#for row in cur:
    #st.write(row)
    #issue_descriptions1.append(row["Task_Subject"])

#st.write(issue_descriptions1)

#for fetched_line in cur.fetchall():
    #id = fetched_line['Task_ID']
    #name = fetched_line['Task_Subject']
    #st.write(f'{id}: {name}')

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

    # Make up some fake issue descriptions.
    issue_descriptions = [
        "オフィスのネットワーク接続の問題",
        "ソフトウェアアプリケーションが起動時にクラッシュする",
        "プリンターが印刷コマンドに応答しない",
        "電子メールサーバーのダウンタイム",
        "データのバックアップ失敗",
        "ログイン認証の問題",
        "ウェブサイトのパフォーマンスの低下",
        "セキュリティ上の脆弱性が特定されました",
        "サーバールームのハードウェア故障",
        "従業員が共有ファイルにアクセスできない",
        "データベース接続の失敗",
        "モバイルアプリケーションがデータを同期していない",
        "VoIP 電話システムの問題",
        "リモート従業員の VPN 接続の問題",
        "システムアップデートにより互換性の問題が発生する",
        "ファイルサーバーのストレージ容量が不足しています",
        "侵入検知システムのアラート",
        "在庫管理システムのエラー",
        "顧客データが CRM に読み込まれない",
        "コラボレーションツールが通知を送信しない",
    ]

    # Generate the dataframe with 100 rows/tickets.
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across
    # page runs). This ensures our data is persisted when the app updates.
    st.session_state.df = df

#st.write(issue_descriptions)
# Show a section to add a new ticket.
st.header("チケット追加")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("イッシュを説明")
    priority = st.selectbox("優先度", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("提出")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("チケットが提出されました。")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing tickets in a table.
st.header("既存チケット")
st.write(f"チケット数: `{len(st.session_state.df)}`")

st.info(
    "セルをダブルクリックすると、チケットを編集できます。",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

# Show some metrics and charts about the ticket.
st.header("統計")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="オープンチケット数", value=num_open_tickets, delta=10)
col2.metric(label="レスポンスタイム（時間）", value=5.2, delta=-1.5)
col3.metric(label="平均時間", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### 月別チケット・ステータス")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### 優先度")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
