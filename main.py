# 20231122 初期作成 v1.0
import streamlit as st
import pandas as pd
from PIL import Image
import smtplib
from email.mime.text import MIMEText

# env読み込み用
import os
from os.path import join, dirname
from dotenv import load_dotenv

# 環境変数envファイルからの取得用
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# 環境変数取得
from_email = os.environ.get("from_email")
to_email = os.environ.get("to_email")
from_password = os.environ.get("from_password")

# セッション状態の初期化
if "purchase_clicked" not in st.session_state:
    st.session_state["purchase_clicked"] = False
if "selected_product" not in st.session_state:
    st.session_state["selected_product"] = None

#######################################################################
# 関数や事前ファイル読み込み
#######################################################################
# CSVファイルの読み込み
df = pd.read_csv("products_v1.0.csv")


# 商品データを表示する関数
def display_products(category_name):
    cols = st.columns(3)
    # 指定されたカテゴリーのデータをフィルタリング
    df_selected = df[df["カテゴリー"] == category_name]
    # 商品名、URL、値段、番号、詳細ページURLの配列を取得
    names = df_selected["商品名"].tolist()
    urls = df_selected["URL"].tolist()
    prices = df_selected["値段"].tolist()
    detail_urls = df_selected["詳細ページURL"].tolist()  # 詳細ページのURL

    for i in range(len(names)):
        with cols[i % 3]:
            st.image(urls[i], use_column_width=True)
            # 詳細ページURLが存在する場合のみリンクを表示
            if detail_urls[i] and detail_urls[i] != "None":
                # 商品名をハイパーリンクとして表示
                st.markdown(
                    f"**{i+1}.{names[i]}**<br><span style='color:#e50914'><strong>{prices[i]}　　</strong></span>\
                    <a href='{detail_urls[i]}' style='color:white; font-size:0.8rem;' target='_blank'>商品イメージ</a>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"**{i+1}.{names[i]}**<br><span style='color:#e50914'><strong>{prices[i]}</strong></span>",
                    unsafe_allow_html=True,
                )
            # ボタンが押された際の購入処理
            if st.button(f"{i+1}を選択"):
                # 購入ボタンが押されたら、状態を更新
                st.session_state["purchase_clicked"] = True
                st.session_state["selected_product"] = {
                    "name": names[i],
                    "price": prices[i],
                    "url": urls[i],
                }


# 購入処理
def display_purchase_section():
    if st.session_state["purchase_clicked"]:
        # 水平線（仕切り線）を挿入
        st.markdown(
            '<hr style="border:1px solid #5a5957; margin-top: 40px; margin-bottom: 25px" />',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<h3 style="text-align:center;">🎉 メッセージを記入してください 🎉</h3>',
            unsafe_allow_html=True,
        )
        st.write(
            f"選択されている商品:　 {st.session_state['selected_product']['name']} / {st.session_state['selected_product']['price']}"
        )
        # メッセージ記入
        user_input = st.text_area("送りたいメッセージ（最大250文字）", max_chars=250)
        # 購入確定
        if st.button("購入確定！"):
            # 購入ボタンが押されたら、メールを送信
            # メール内容
            subject = "購入確定通知"
            body = f"商品情報: {st.session_state['selected_product']['name']}\nユーザーのメッセージ: {user_input}"

            # メール送信
            send_email(subject, body, to_email)
            st.success("購入を確定しました。商品のお届けまで今しばらくお待ちください。")


# メール送信関数
def send_email(subject, body, to_email):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, from_password)
    server.send_message(msg)
    server.quit()


#######################################################################
# streamlit事前設定
#######################################################################
st.set_page_config(
    page_title="β版プレゼントサイト",
    menu_items={
        "Get Help": "mailto:a-komukai-ah@morinaga.co.jp",
        "Report a bug": "mailto:jidansan6.serv@gmail.com",
        "About": """
        # β版プレゼントサイト
        このアプリはβ版であり、内容は予告なく変更する場合がございます。2023ⓒ森永製菓㈱ 小向
        """,
    },
)

# 画面上部のpadding設定
padding_top = 2
# カスタムCSSを定義
st.markdown(
    f"""
    <style>
    .appview-container .main .block-container{{
        padding-top: {padding_top}rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)
# カスタムCSSをページに埋め込む
st.markdown(
    """
    <style>
    /* テキストエリアのフォントサイズを小さくする */
    .stTextArea textarea {
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

#######################################################################
# streamlit本ページ
#######################################################################
# Title
st.title("β版プレゼントサイト")
st.write("商品を選択後、画面下部へ進みメッセージを記入してから購入を確定してください。")
st.markdown(
    '<hr style="border:1px solid #5a5957; margin-top: 15px; margin-bottom: 25px" />',
    unsafe_allow_html=True,
)

# カテゴリー選択
category = st.selectbox(label="カテゴリーを選んでください。", options=["お花", "リラクゼーション", "お菓子"])

if category:
    display_products(category)

# 購入セクションの表示
display_purchase_section()
