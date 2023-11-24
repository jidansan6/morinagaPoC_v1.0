# 20231122 初期作成 v1.0
import streamlit as st
import pandas as pd
from PIL import Image
import smtplib
from email.mime.text import MIMEText

# google drive読み込み用
import gspread
from google.oauth2.service_account import Credentials

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
if "selected_user_info" not in st.session_state:
    st.session_state["selected_user_info"] = {}
if "purchase_clicked" not in st.session_state:
    st.session_state["purchase_clicked"] = False
if "selected_product" not in st.session_state:
    st.session_state["selected_product"] = None
if "selected_user_id" not in st.session_state:
    st.session_state["selected_user_id"] = None
if "selected_plan" not in st.session_state:
    st.session_state["selected_plan"] = None
if "selected_user_id" not in st.session_state:
    st.session_state["selected_user_id"] = None


#######################################################################
# 関数や事前ファイル読み込み
#######################################################################
# CSVファイルの読み込み
df = pd.read_csv("products_v1.0.csv")


def read_DB():
    # 決まり文句
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # ダウンロードしたjsonファイル名をクレデンシャル変数に設定。
    credentials = Credentials.from_service_account_file(
        "morinaga-pjt-2f117589ec39.json", scopes=scope
    )
    # OAuth2の資格情報を使用してGoogle APIにログイン。
    gc = gspread.authorize(credentials)
    # スプレッドシートIDを変数に格納する。
    SPREADSHEET_KEY = os.environ.get("SPREADSHEET_KEY")
    # スプレッドシート（ブック）を開く
    workbook = gc.open_by_key(SPREADSHEET_KEY)
    worksheet = workbook.worksheet("userdb_v1.0")
    # df = pd.DataFrame(worksheet.get_all_values())
    # スプレッドシートをDataFrameに取り込む
    df_user = pd.DataFrame(
        worksheet.get_all_values()[1:], columns=worksheet.get_all_values()[0]
    )
    return df_user, worksheet


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
            body = f"商品が購入されました。\n■購入者: {st.session_state['selected_user_info']['user_name']}\n■購入商品情報: {st.session_state['selected_product']['name']}\n■ユーザーのメッセージ:\n{user_input}\n■お届け先:\n〒{st.session_state['selected_user_info']['postcode']}\n{st.session_state['selected_user_info']['address']}\n■電話番号: {st.session_state['selected_user_info']['tel']}\n■契約プラン：{st.session_state['selected_user_info']['plan']}"

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


# 選択されたプランをスプレッドシートへ記述
def plan_select(selected_plan):
    cell = worksheet.find(st.session_state["selected_user_id"])
    plan_col = worksheet.row_values(1).index("plan") + 1
    new_plan_value = selected_plan
    worksheet.update_cell(cell.row, plan_col, new_plan_value)


# プランの削除
def plan_delete():
    cell = worksheet.find(st.session_state["selected_user_id"])
    plan_col = worksheet.row_values(1).index("plan") + 1
    new_plan_value = ""
    worksheet.update_cell(cell.row, plan_col, new_plan_value)


# プランの確認
def plan_check():
    if st.session_state["selected_user_id"]:
        st.session_state["selected_user_id"] = user_id
        selected_user_info = df_user[df_user["user_id"] == user_id].iloc[0].to_dict()
        st.session_state["selected_user_info"] = selected_user_info
        # 選択されたユーザーIDに対応するプランを取得
        selected_plan = df_user[df_user["user_id"] == user_id]["plan"].iloc[0]
        # 条件分岐
        if df_user[df_user["user_id"] == user_id]["plan"].values[0] == "":
            # planを選んでいなかった場合
            if df_user[df_user["user_id"] == user_id]["address"].values[0] != "":
                st.write("プランに登録されていません。まずはプランを選びましょう！")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.image("image/simple.png", use_column_width=True)
                    st.markdown(
                        "**シンプルプラン**<br><span style='color:#e50914'><strong>3,000円/月（税込）</strong></span>",
                        unsafe_allow_html=True,
                    )
                    # プラン選択後の処理
                    if st.button("このプランにする！", key="simple"):
                        plan_select("シンプルプラン")
                        st.success("プランを更新しました。リロードしてログインしてください。")
                with col2:
                    st.image("image/standard.png", use_column_width=True)
                    st.markdown(
                        "**スタンダードプラン**<br><span style='color:#e50914'><strong>6,000円/月（税込）</strong></span>",
                        unsafe_allow_html=True,
                    )
                    # プラン選択後の処理
                    if st.button("このプランにする！", key="standard"):
                        plan_select("スタンダードプラン")
                        st.success("プランを更新しました。リロードしてログインしてください。")
                with col3:
                    st.image("image/premium.png", use_column_width=True)
                    st.markdown(
                        "**プレミアムプラン**<br><span style='color:#e50914'><strong>9,000円/月（税込）</strong></span>",
                        unsafe_allow_html=True,
                    )
                    # プラン選択後の処理
                    if st.button("このプランにする！", "premium"):
                        plan_select("プレミアムプラン")
                        st.success("プランを更新しました。リロードしてログインしてください。")
        # プラン選択済みの場合
        else:
            st.write(f"ユーザーID： {user_id} さんのプランは【　{selected_plan}　】です。")
            st.write("ページ選択から「商品一覧」へ進み、プレゼントを選んでください。")
            st.session_state["login_clicked"] = False
            st.markdown(
                '<hr style="border:1px solid #5a5957; margin-top: 15px; margin-bottom: 25px" />',
                unsafe_allow_html=True,
            )
            if st.button("プランを選びなおす！"):
                plan_delete()
                st.success("登録済みのプランを削除しました。リロードしてプランを選びなおしてください。")


#######################################################################
# streamlit事前設定
#######################################################################
st.set_page_config(
    page_title="β版プレゼントサイト",
    menu_items={
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

# セレクトボックスのページリストを作成
pagelist = ["ログイン", "商品一覧"]

# サイドバーのセレクトボックスを配置
selector = st.sidebar.selectbox("ページ選択", pagelist)
if selector == "ログイン":
    st.write("事前に通知したIDを選択し、プランを選んでください。プランは後からでも変えられます。")
    st.markdown(
        '<hr style="border:1px solid #5a5957; margin-top: 15px; margin-bottom: 25px" />',
        unsafe_allow_html=True,
    )
    # db読み込み
    df_user, worksheet = read_DB()
    # ユーザーIDを選択するためのセレクトボックス
    user_id = st.selectbox(
        "ユーザーIDを選択してください",
        df_user["user_id"].unique(),
        key="user_id_select",
        index=0,
    )
    st.session_state["selected_user_id"] = user_id
    plan_check()


######################################################################################################################
# 商品一覧ページ
elif selector == "商品一覧":
    if st.session_state["selected_user_info"]["nickname"]:
        st.write(
            "ようこそ！"
            + st.session_state["selected_user_info"]["nickname"]
            + "さん！（名前が違う場合はログインしなおしてください。）"
        )
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
