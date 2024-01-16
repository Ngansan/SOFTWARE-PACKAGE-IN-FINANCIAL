import requests
from bs4 import BeautifulSoup
import plotly.graph_objs as go
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import glob
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from plotly.subplots import make_subplots
from scipy.interpolate import make_interp_spline, BSpline


# Cài đặt headers để mô phỏng một trình duyệt web
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Hàm để lấy thông tin từ URL
def get_website_content(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return "Website không phản hồi hoặc có lỗi xảy ra."
    except requests.RequestException as e:
        return str(e)

# Hàm để phân tích cú pháp nội dung và lấy thông tin cần thiết
def extract_information(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Đối với trang này, bạn cần tìm selector chính xác để lấy nội dung
    content = soup.find('div', class_='row dn-chi-tiet')  # Thay đổi này theo nội dung thực tế bạn muốn lấy
    return content.text if content else "Không tìm thấy thông tin."

def show_home():
    html_content = get_website_content(
        'https://vnr500.com.vn/Thong-tin-doanh-nghiep/CONG-TY-CP-BIBICA--Chart--204-2017.html')
    content_to_display = extract_information(html_content)
    st.write(content_to_display)

def show_financials():
    folder_path = r'D:\Software Package'
    desired_files = ["2018-Vietnam.xlsx", "2019-Vietnam.xlsx", "2020-Vietnam.xlsx", "2021-Vietnam.xlsx",
                     "2022-Vietnam.xlsx"]

    # Tạo DataFrame chứa dữ liệu từ 5 file Excel
    dfs = []  # List để lưu trữ DataFrame của mỗi file
    for file_name in desired_files:
        # Đường dẫn đầy đủ của file
        file_path = f"{folder_path}\\{file_name}"

        # Đọc dữ liệu từ file Excel
        df = pd.read_excel(file_path)

        # Lấy năm từ tên file
        year = file_name.split('-')[0]

        # Xóa cụm từ khỏi tên cột
        df.columns = df.columns.str.replace(f'\nHợp nhất\nQuý: Hàng năm\nNăm: {year}\nĐơn vị: Triệu VND', '')

        # Xóa các cột cụ thể
        columns_to_drop = [
            f'Quý\nHợp nhất\nQuý: Hàng năm\nNăm: {year}\n',
            f'Trạng thái kiểm toán\nHợp nhất\nQuý: Hàng năm\nNăm: {year}\n'
        ]

        # Thay đổi tên các cột thành "Năm"
        columns_to_rename = [f'Năm\nHợp nhất\nQuý: Hàng năm\nNăm: {year}\n' for year in range(2018, 2023)] + ['Năm']

        # Xóa các cột không cần thiết
        df = df.drop(columns=columns_to_drop, errors='ignore')

        # Thay đổi tên các cột
        df.rename(columns=dict(zip(columns_to_rename, [f'Năm' for _ in range(2018, 2023)] + ['Năm'])), inplace=True)
        # Tìm và thay thế '(TT)' trong tên các cột
        df.columns = df.columns.str.replace(r'\(TT\)', '', regex=True)

        # Thêm DataFrame vào danh sách
        dfs.append(df)

    # Tạo DataFrame chứa dữ liệu từ 5 file Excel
        combined_df = pd.concat(dfs, ignore_index=True)
    # Tìm các dòng trong cột 'Mã' có giá trị là 'BBC'
    df = combined_df[combined_df['Mã'] == 'BBC']

    # Chuyển đổi cột 'Năm' thành kiểu dữ liệu số nguyên
    combined_df['Năm'] = pd.to_numeric(combined_df['Năm'], errors='coerce').astype('Int64')

    # Đường dẫn đầy đủ đến file Excel
    file_path = r'D:\Software Package\SSI_BBC_Financial_Ratio_20182023.xlsx'

    # Đọc file Excel và lưu vào DataFrame
    df_ssi = pd.read_excel(file_path)

    # Lấy dữ liệu từ cột 'Năm', 'Doanh thu Toàn ngành', 'Tăng trưởng doanh thu Toàn ngành (%)'
    columns_of_interest = ['Năm', 'Doanh thu Toàn ngành', 'Tăng trưởng doanh thu ngành(%)']
    dt_df = df_ssi[columns_of_interest]

    tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs(["Cơ cấu tài sản & nguồn vốn", "Tăng trưởng", "Sinh lời",
                                "Thanh khoản", "Đòn bẩy tài chính", "Dòng tiền", "Định giá"])

    with tab1:
        st.header("Biểu đồ Tổng cộng tài sản BBC từ năm 2018 đến 2022")
        ################### Biểu đồ Tổng cộng tài sản BBC từ năm 2018 đến năm 2022 #############
        # Chọn các cột cần thiết từ DataFrame gốc
        df_tong_tai_san = df[['Năm', 'CĐKT. TỔNG CỘNG TÀI SẢN']]

        # Đảm bảo kiểu dữ liệu của cột 'Năm' là số nguyên
        df_tong_tai_san['Năm'] = pd.to_numeric(df_tong_tai_san['Năm'], errors='coerce').astype('Int64')
        # Tạo biểu đồ sử dụng Plotly Express
        fig = px.line(df_tong_tai_san, x='Năm', y='CĐKT. TỔNG CỘNG TÀI SẢN',
                      markers=True,
                      labels={'CĐKT. TỔNG CỘNG TÀI SẢN': 'Tổng cộng tài sản (ĐVT: Triệu tỷ đồng)'},
                      )
        fig.update_xaxes(showline=True, linewidth=2, linecolor="black")
        fig.update_yaxes(
            showline=True,
            linewidth=2,
            linecolor="black",
            gridwidth=1,
            gridcolor="blue",
        )
        # Thêm text trên từng điểm dữ liệu
        for index, row in df_tong_tai_san.iterrows():
            fig.add_annotation(x=row['Năm'], y=row['CĐKT. TỔNG CỘNG TÀI SẢN'],
                               text=f"{row['CĐKT. TỔNG CỘNG TÀI SẢN'] / 1e12:.2f} triệu tỷ đồng",
                               showarrow=True,
                               arrowhead=1,
                               ax=0,
                               ay=-40)
        # Hiển thị biểu đồ
        st.plotly_chart(fig)

        ########### Biểu đồ thể hiện tỷ lệ thành phần Tổng tài sản từ 2018 đến 2022 ###########
        st.header("Biểu đồ tỷ lệ thành phần Tổng tài sản từ 2018 đến 2022")
        cols = ['Năm', 'CĐKT. Tiền và tương đương tiền ', 'CĐKT. Đầu tư tài chính ngắn hạn',
                'CĐKT. Các khoản phải thu ngắn hạn', 'CĐKT. Hàng tồn kho, ròng',
                'CĐKT. Tài sản ngắn hạn khác', 'CĐKT. Phải thu dài hạn', 'CĐKT. Tài sản cố định',
                'CĐKT. Giá trị ròng tài sản đầu tư', 'CĐKT. Tài sản dở dang dài hạn',
                'CĐKT. Tài sản dài hạn khác']
        df_tai_san = df[cols]

        # Màu của từng cột
        colors = ['#711DB0', '#C21292', '#FFA732', '#D3D04F', 'brown', '#ED5AB3', 'green', '#1B4242', '#65B741',
                  '#9ADE7B']

        # Vẽ biểu đồ cột
        fig, ax = plt.subplots(figsize=(12, 8))
        bottom = None

        def func_percent(x, pos):
            return f"{x * 100:.1f}%"

        formatter = FuncFormatter(func_percent)

        for i, col in enumerate(df_tai_san.columns[1:]):
            values = df_tai_san[col] / df_tai_san.iloc[:, 1:].sum(axis=1)
            rects = ax.bar(df_tai_san['Năm'], values, label=col, color=colors[i], bottom=bottom)

            # Thêm tooltip
            labels = [f'{val * 100:.1f}%' if val != 0 else '' for val in values]
            ax.bar_label(rects, labels=labels, color='white', fontsize=12, fmt="%s", fontweight='bold',
                         label_type='center', padding=3)

            if bottom is None:
                bottom = values
            else:
                bottom += values

        ax.yaxis.set_major_formatter(formatter)
        plt.xlabel('Năm')

        # Lưu lại chú thích và đảo ngược thứ tự nó
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(reversed(handles), reversed(labels), loc='upper left', bbox_to_anchor=(1, 1), title='Chú thích',
                  title_fontsize='14', fontsize='12')

        # Hiển thị biểu đồ sử dụng Streamlit
        st.pyplot(fig)

        ###################### Biểu đồ thể hiện tỷ lệ thành phần Tổng nguồn vốn từ 2018 đến 2022 #################
        st.header("Biểu đồ thể hiện tỷ lệ thành phần Tổng nguồn vốn từ 2018 đến 2022")
        ## Biểu đồ thể hiện tỷ lệ thành phần Tổng nguồn vốn từ 2018 đến 2022
        cols = ['Năm', 'CĐKT. Nợ ngắn hạn', 'CĐKT. Nợ dài hạn', 'CĐKT. VỐN CHỦ SỞ HỮU']

        df_no_von = df[cols]

        # Màu của từng cột
        colors = ['#65B741', '#D71313', '#FFCD4B']

        # Vẽ biểu đồ cột
        fig, ax = plt.subplots(figsize=(12, 8))
        bottom = None

        def func_percent(x, pos):
            return f"{x * 100:.1f}%"

        formatter = FuncFormatter(func_percent)

        for i, col in enumerate(df_no_von.columns[1:]):
            values = df_no_von[col] / df_no_von.iloc[:, 1:].sum(axis=1)
            rects = ax.bar(df_no_von['Năm'], values, label=col, color=colors[i], bottom=bottom)

            # Thêm tooltip
            labels = [f'{val * 100:.1f}%' if val != 0 else '' for val in values]
            ax.bar_label(rects, labels=labels, color='white', fontsize=12, fmt="%s", fontweight='bold',
                         label_type='center', padding=3)

            if bottom is None:
                bottom = values
            else:
                bottom += values

        ax.yaxis.set_major_formatter(formatter)
        plt.xlabel('Năm')

        # Lưu lại chú thích và đảo ngược thứ tự nó
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(reversed(handles), reversed(labels), loc='upper left', bbox_to_anchor=(1, 1), title='Chú thích',
                  title_fontsize='14', fontsize='12')
        #show chart
        st.pyplot(fig)

    with tab2:
        st.header("Biểu đồ Tăng trưởng doanh thu của Bibica từ 2018 đến 2022")
        ############# Biểu đồ Tăng trưởng doanh thu Bibica từ 2018 đến 2022 #############################
        # Chọn cột 'Năm' và 'KQKD. Doanh thu thuần\n'
        df_doanh_thu = df[['Năm', 'KQKD. Doanh thu thuần']]

        # Chuyển đổi cột 'Năm' sang kiểu số nguyên
        df_doanh_thu.loc[:, 'Năm'] = df_doanh_thu['Năm'].astype(int)

        # Thêm Doanh thu thuần năm 2017
        doanh_thu_2017 = 1289892987833  # Giá trị Doanh thu thuần năm 2017
        df_doanh_thu.loc[df_doanh_thu['Năm'] == 2017, 'KQKD. Doanh thu thuần'] = doanh_thu_2017

        # Tính tốc độ tăng trưởng của từng năm so với năm trước
        df_doanh_thu.loc[:, 'Tốc độ tăng trưởng doanh thu thuần(%)'] = df_doanh_thu[
                                                                           'KQKD. Doanh thu thuần'].pct_change() * 100

        # Tính tốc độ tăng trưởng của năm 2018 so với năm 2017
        doanh_thu_2018 = df_doanh_thu.loc[df_doanh_thu['Năm'] == 2018, 'KQKD. Doanh thu thuần'].values[0]
        tang_truong_2018 = (doanh_thu_2018 - doanh_thu_2017) / doanh_thu_2017 * 100
        df_doanh_thu.loc[df_doanh_thu['Năm'] == 2018, 'Tốc độ tăng trưởng doanh thu thuần(%)'] = tang_truong_2018

        # Vẽ biểu đồ cột và đường tăng trưởng
        fig, ax1 = plt.subplots(figsize=(10, 6))

        color = '#337CCF'
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('Doanh thu thuần (Triệu tỷ đồng)', color=color)
        bars = ax1.bar(df_doanh_thu['Năm'], df_doanh_thu['KQKD. Doanh thu thuần'] / 1e12, color=color,
                       label='Doanh thu thuần')
        ax1.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị trên từng cột
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2f}', ha='center', va='bottom')

        # Tạo một trục thứ hai để vẽ đường tăng trưởng
        ax2 = ax1.twinx()
        color = 'tab:red'
        line = ax2.plot(df_doanh_thu['Năm'], df_doanh_thu['Tốc độ tăng trưởng doanh thu thuần(%)'], color=color,
                        marker='o', label='Tăng trưởng (%)')
        ax2.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị tăng trưởng trực tiếp trên từng điểm
        for index, row in df_doanh_thu.iterrows():
            ax2.annotate(f'{row["Tốc độ tăng trưởng doanh thu thuần(%)"]:.2f}%',
                         (row['Năm'], row['Tốc độ tăng trưởng doanh thu thuần(%)'] + 1.5),
                         textcoords="offset points", xytext=(0, 5), ha='center', color='red')

        fig.legend(loc='upper left', bbox_to_anchor=(0.95, 0.9), title='Chú thích', title_fontsize='12', fontsize='10')
        # show chart
        st.pyplot(fig)

        #########################################################################################################

        ######### Biểu đồ Tăng trưởng doanh thu Toàn ngành từ 2018 đến 2022 #####################

        # Chuyển cột 'Năm' sang kiểu số nguyên
        st.header("Biểu đồ Tăng trưởng doanh thu Toàn ngành từ 2018 đến 2022")
        dt_df['Năm'] = dt_df['Năm'].astype(int)

        # Hiển thị biểu đồ trong ứng dụng
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Biểu đồ cột cho doanh thu
        color = '#337CCF'
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('Doanh thu Toàn ngành (Triệu tỷ đồng)', color=color)
        bars = ax1.bar(dt_df['Năm'], dt_df['Doanh thu Toàn ngành'] / 1e12, color=color, label='Doanh thu Toàn ngành')
        ax1.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị và chú thích trực tiếp trên từng cột
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2f}', ha='center', va='bottom', color='black')

        # Biểu đồ đường cho tốc độ tăng trưởng (nhân 100)
        ax2 = ax1.twinx()
        color = 'tab:red'
        line = ax2.plot(dt_df['Năm'], dt_df['Tăng trưởng doanh thu ngành(%)'] * 100, color=color, marker='o',
                        label='Tăng trưởng (%)')
        ax2.set_ylabel('Tốc độ tăng trưởng (%)', color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị tăng trưởng trực tiếp trên từng điểm
        for index, row in dt_df.iterrows():
            ax2.annotate(f'{row["Tăng trưởng doanh thu ngành(%)"] * 100:.2f}%',
                         (row['Năm'], row['Tăng trưởng doanh thu ngành(%)'] * 100),
                         textcoords="offset points", xytext=(0, 5), ha='center', color='red')

        # Hiển thị biểu đồ trong ứng dụng Streamlit
        st.pyplot(fig)
        #######################################################################################

        ################ Biểu đồ Tăng trưởng Lợi nhuận sau thuế của Bibica từ 2018 đến 2022 #######################
        st.header("Biểu đồ Tăng trưởng LNST chưa phân phối của Bibica từ 2018 đến 2022")
        # Chọn cột 'Năm' và 'CĐKT. LNST chưa phân phối kỳ này'
        df_lnst = df[['Năm', 'CĐKT. LNST chưa phân phối kỳ này']]

        # Tính tốc độ tăng trưởng của từng năm so với năm trước
        df_lnst.loc[:, 'Tốc độ tăng trưởng LNST(%)'] = (df_lnst['CĐKT. LNST chưa phân phối kỳ này'] - df_lnst[
            'CĐKT. LNST chưa phân phối kỳ này'].shift(1)) / df_lnst['CĐKT. LNST chưa phân phối kỳ này'].shift(1) * 100

        # Tính tốc độ tăng trưởng của năm 2018 so với năm 2017
        lnst_2017 = 81908194816  # Giá trị LNST chưa phân phối năm 2017
        lnst_2018 = df_lnst.loc[df_lnst['Năm'] == 2018, 'CĐKT. LNST chưa phân phối kỳ này'].values[0]
        tang_truong_2018 = (lnst_2018 - lnst_2017) / lnst_2017 * 100
        df_lnst.loc[df_lnst['Năm'] == 2018, 'Tốc độ tăng trưởng LNST(%)'] = tang_truong_2018

        # Vẽ biểu đồ cột và đường tăng trưởng
        fig, ax1 = plt.subplots(figsize=(10, 6))

        color = '#337CCF'
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('LNST chưa phân phối (ĐVT: Tỷ đồng)', color=color)
        bars = ax1.bar(df_lnst['Năm'], df_lnst['CĐKT. LNST chưa phân phối kỳ này'] / 1e9, color=color,
                       label='LNST chưa phân phối')
        ax1.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị trên từng cột
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2f}', ha='center', va='bottom')

        # Tạo một trục thứ hai để vẽ đường tăng trưởng
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Tốc độ tăng trưởng LNST(%)', color=color)
        line = ax2.plot(df_lnst['Năm'], df_lnst['Tốc độ tăng trưởng LNST(%)'], color=color, marker='o',
                        label='Tăng trưởng (%)')
        ax2.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị tăng trưởng trực tiếp trên từng điểm
        for index, row in df_lnst.iterrows():
            ax2.annotate(f'{row["Tốc độ tăng trưởng LNST(%)"]:.2f}%',
                         (row['Năm'], row['Tốc độ tăng trưởng LNST(%)'] + 4),
                         textcoords="offset points", xytext=(0, 5), ha='center', color='red')

        # Tạo chú thích tổng hợp
        fig.legend(loc='upper left', bbox_to_anchor=(0.95, 0.85), title='Chú thích', title_fontsize='8', fontsize='10')

        ##### show chart
        st.pyplot(fig)
        ###########################################################################################################

        ################### Biểu đồ Tăng trưởng Lợi nhuận sau thuế toàn ngành của Bibica từ 2018 đến 2022 ##########
        st.header("Biểu đồ Tăng trưởng lợi nhuận sau thuế Toàn ngành từ 2018 đến 2022")
        # Chuyển cột 'Năm' sang kiểu số nguyên
        df_ssi['Năm'] = df_ssi['Năm'].astype(int)

        # Vẽ biểu đồ
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Biểu đồ cột cho doanh thu
        color = '#337CCF'
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('Lợi nhuận sau thuế Toàn ngành (Triệu tỷ đồng)', color=color)
        bars = ax1.bar(df_ssi['Năm'], df_ssi['Lợi nhuận sau thuế Toàn ngành'] / 1e12, color=color,
                       label='Doanh thu Toàn ngành')
        ax1.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị và chú thích trực tiếp trên từng cột
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2f}', ha='center', va='bottom', color='black')

        # Biểu đồ đường cho tốc độ tăng trưởng (nhân 100)
        ax2 = ax1.twinx()
        color = 'tab:red'
        line = ax2.plot(df_ssi['Năm'], df_ssi['Tăng trưởng lợi nhuận ngành (%)'] * 100, color=color, marker='o',
                        label='Tăng trưởng (%)')
        ax2.set_ylabel('Tốc độ tăng trưởng (%)', color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        # Thêm giá trị tăng trưởng trực tiếp trên từng điểm
        for index, row in df_ssi.iterrows():
            ax2.annotate(f'{row["Tăng trưởng lợi nhuận ngành (%)"] * 100:.2f}%',
                         (row['Năm'], row['Tăng trưởng lợi nhuận ngành (%)'] * 100),
                         textcoords="offset points", xytext=(5, -16), va='bottom', ha='center', color='red')

        plt.title('Biểu đồ Tăng trưởng lợi nhuận sau thuế Toàn ngành từ 2018 đến 2022')
        ##### show chart
        st.pyplot(fig)
        #######################################################################################################

    with tab3:

        ################## Biểu đồ các chỉ số tăng trưởng của Bibica từ năm 2018 đến 2022 #####################
        st.header("Biểu đồ Biên lợi nhuận của BBC từ 2018 đến 2022")
        # Chuyển cột 'Năm' sang kiểu số nguyên
        df_ssi['Năm'] = df_ssi['Năm'].astype(int)
        # Tính biên lợi nhuận gộp, ròng và hoạt động
        df['Biên_Lợi_Nhuận_Gộp'] = (df['KQKD. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ'] / df[
            'KQKD. Doanh thu thuần']) * 100
        df['Biên_Lợi_Nhuận_Ròng'] = (df['KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp'] / df[
            'KQKD. Doanh thu thuần']) * 100
        df['Biên_Lợi_Nhuận_Hoạt_Động'] = (df['KQKD. Tổng lợi nhuận kế toán trước thuế'] / df[
            'KQKD. Doanh thu thuần']) * 100

        # Vẽ biểu đồ
        fig, ax = plt.subplots(figsize=(10, 6))

        # Vẽ đường cho từng biên lợi nhuận
        ax.plot(df['Năm'].astype(int), df['Biên_Lợi_Nhuận_Gộp'], marker='o', linestyle='-', label='Biên lợi nhuận gộp')
        ax.plot(df['Năm'].astype(int), df['Biên_Lợi_Nhuận_Ròng'], marker='o', linestyle='-',
                label='Biên lợi nhuận ròng')
        ax.plot(df['Năm'].astype(int), df['Biên_Lợi_Nhuận_Hoạt_Động'], marker='o', linestyle='-',
                label='Biên lợi nhuận hoạt động')

        # Hiển thị giá trị trực tiếp trên từng điểm của mỗi năm
        for year, gop, rong, hoat_dong in zip(df['Năm'], df['Biên_Lợi_Nhuận_Gộp'], df['Biên_Lợi_Nhuận_Ròng'],
                                              df['Biên_Lợi_Nhuận_Hoạt_Động']):
            ax.text(year, gop, f'{gop:.2f}%', ha='center', va='bottom', color='black')
            ax.text(year, rong, f'{rong:.2f}%', ha='center', va='bottom', color='black')
            ax.text(year, hoat_dong, f'{hoat_dong:.2f}%', ha='center', va='bottom', color='black')

        ax.set_xlabel('Năm')
        ax.set_ylabel('Biên lợi nhuận (%)')
        ax.grid(True)
        ax.legend()

        # Chỉ định điểm chính trên trục X (hiển thị 5 năm)
        plt.xticks(df['Năm'].astype(int).iloc[::1])

        #### show chart
        st.pyplot(fig)
        ###########################################################################################################

        ##################  Biểu đồ Hiệu quả sử dụng vốn từ 2018 đến 2022  ##################
        st.header("Biểu đồ Hiệu quả sử dụng vốn từ 2018 đến 2022")
        # Chuyển cột 'Năm' sang kiểu số nguyên
        df_ssi['Năm'] = df_ssi['Năm'].astype(int)
        selected_years = df['Năm'].unique()[:5]
        ax.set_xticks(selected_years)

        # Tính toán các tỷ lệ ROE, ROIC, và Lãi cơ bản trên cổ phiếu
        df['ROE(%)'] = (df['KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp'] / df['CĐKT. VỐN CHỦ SỞ HỮU']) * 100

        df['ROIC(%)'] = (df['KQKD. Cổ đông của Công ty mẹ']) * 100 / (
                df['CĐKT. VỐN CHỦ SỞ HỮU'] + df['CĐKT. Vay và nợ thuê tài chính ngắn hạn'] + df[
            'CĐKT. Vay và nợ thuê tài chính dài hạn'] - df['CĐKT. Tiền và tương đương tiền '])

        df['ROA(%)'] = (df['KQKD. Lợi nhuận sau thuế thu nhập doanh nghiệp'] / df['CĐKT. TỔNG CỘNG TÀI SẢN']) * 100

        # Vẽ biểu đồ
        fig, ax = plt.subplots(figsize=(10, 6))
        # Vẽ đường cho Lãi cơ bản trên cổ phiếu (%)
        color = 'tab:red'
        ax.set_xlabel('Năm')
        ax.set_ylabel('Tỷ lệ (%)', color=color)
        ax.tick_params(axis='y', labelcolor=color)

        ax.plot(df['Năm'].astype(int), df['ROA(%)'], marker='o', linestyle='-', color=color, label='ROA(%)')
        ax.plot(df['Năm'].astype(int), df['ROE(%)'], marker='o', linestyle='-', color='tab:blue', label='ROE (%)')
        ax.plot(df['Năm'].astype(int), df['ROIC(%)'], marker='o', linestyle='-', color='tab:green', label='ROIC (%)')

        # Hiển thị giá trị trực tiếp trên điểm của mỗi năm
        for year, lcb, roe, roic in zip(df['Năm'], df['ROA(%)'], df['ROE(%)'], df['ROIC(%)']):
            ax.text(year, lcb, f'{lcb:.2f}', ha='center', va='bottom', color='black')
            ax.text(year, roe, f'{roe:.2f}', ha='center', va='bottom', color='black')
            ax.text(year, roic, f'{roic:.2f}', ha='center', va='bottom', color='black')

        # Thay đổi hướng hiển thị chú thích
        ax.legend(loc='upper right', bbox_to_anchor=(1, 1))

        # Chỉ hiển thị 5 năm trên trục x
        ax.set_xticks(selected_years)

        plt.xlabel('Năm', fontsize=10)
        plt.ylabel('Tỷ lệ (%)', color=color, fontsize=10)

        #### show chart
        st.pyplot(fig)
        ###########################################################################################
    with tab4:
        ################## Hiệu quả hoạt động  ################################
        st.header("Nhóm chỉ số Hiệu quả hoạt động của BIBICA từ 2018 đến 2022")
        # Tính và lưu các chỉ số vòng quay vào cột mới
        df['Turnover_Ratio_Inventory'] = df['KQKD. Doanh thu bán hàng và cung cấp dịch vụ'] / df[
            'CĐKT. Hàng tồn kho, ròng']
        df['Turnover_Ratio_Fixed_Assets'] = df['KQKD. Doanh thu bán hàng và cung cấp dịch vụ'] / df[
            'CĐKT. Tài sản cố định']
        df['Turnover_Ratio_Total_Assets'] = df['KQKD. Doanh thu bán hàng và cung cấp dịch vụ'] / df[
            'CĐKT. TỔNG CỘNG TÀI SẢN']

        # Tính và lưu chỉ số Kỳ thu tiền bình quân
        df['Average_Collection_Period'] = (df['CĐKT. Các khoản phải thu ngắn hạn'] + df['CĐKT. Phải thu dài hạn']) / (
                    df['KQKD. Doanh thu bán hàng và cung cấp dịch vụ'] / 365)

        # Vẽ biểu đồ
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Vẽ cột cho từng chỉ số vòng quay với màu sắc tùy chỉnh
        ax1.bar(df['Năm'] - 0.2, df['Turnover_Ratio_Inventory'], width=0.2, label='Vòng quay Hàng tồn kho',
                color='#337CCF')
        ax1.bar(df['Năm'], df['Turnover_Ratio_Fixed_Assets'], width=0.2, label='Vòng quay Tài sản cố định',
                color='#65B741')
        ax1.bar(df['Năm'] + 0.2, df['Turnover_Ratio_Total_Assets'], width=0.2, label='Vòng quay Tổng tài sản',
                color='#F875AA')

        # Vẽ đường cho chỉ số Kỳ thu tiền bình quân với màu sắc tùy chỉnh
        ax2 = ax1.twinx()
        ax2.plot(df['Năm'], df['Average_Collection_Period'] + 5, marker='o', linestyle='-', color='red',
                 label='Kỳ thu tiền bình quân (ngày)')

        # Chú thích chung
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()

        # Thêm chú thích riêng cho Kỳ thu tiền bình quân vào đầu danh sách
        lines.insert(0, lines2[0])
        labels.insert(0, labels2[0])

        # Đặt vị trí chú thích
        ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(0.0, 1.15), ncol=4)

        # Hiển thị giá trị trực tiếp trên điểm của mỗi năm
        for year, inv_ratio, fixed_assets_ratio, total_assets_ratio, avg_coll_period in zip(
                df['Năm'], df['Turnover_Ratio_Inventory'], df['Turnover_Ratio_Fixed_Assets'],
                df['Turnover_Ratio_Total_Assets'], df['Average_Collection_Period']
        ):
            ax1.text(year - 0.2, inv_ratio, f'{inv_ratio:.2f}', ha='center', va='bottom', color='black')
            ax1.text(year, fixed_assets_ratio, f'{fixed_assets_ratio:.2f}', ha='center', va='bottom', color='black')
            ax1.text(year + 0.2, total_assets_ratio, f'{total_assets_ratio:.2f}', ha='center', va='bottom',
                     color='black')
            ax2.text(year, avg_coll_period + 0.9, f'{avg_coll_period:.2f}', ha='center', va='bottom', color='red')

        # Cấu hình trục X và chú thích
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('Chỉ số Vòng quay')
        ax2.set_ylabel('Kỳ thu tiền bình quân (ngày)', color='red')
        ax2.tick_params(axis='y', colors='red')  # Thiết lập màu cho số trên trục y bên phải

        #############################################################################################
        st.pyplot(fig)

        ################# Biểu đồ so sánh giữa Chỉ số thanh khoản trung bình ngành #############
        # Thực phẩm của các doanh nghiệp nổi bậc niêm yết trên sàn Chứng khoán và BBC #############
        st.header("So sánh Chỉ số thanh khoản của BIBICA và Thực phẩm của BBC từ 2018 đến 2022")
        # Lọc dữ liệu chỉ cho ngành Thực phẩm
        df_food = combined_df[combined_df['Ngành ICB - cấp 4'] == 'Thực phẩm']

        # Nhóm theo năm và tính tổng cho mỗi nhóm
        sum_by_year = df_food.groupby('Năm').agg({
            'CĐKT. TÀI SẢN NGẮN HẠN': 'sum',
            'CĐKT. Hàng tồn kho, ròng': 'sum',
            'CĐKT. Nợ ngắn hạn': 'sum',
            'CĐKT. Tiền và tương đương tiền ': 'sum'
        })

        # Áp dụng công thức cho từng chỉ số
        sum_by_year['Quick_Ratio'] = (sum_by_year['CĐKT. TÀI SẢN NGẮN HẠN'] - sum_by_year['CĐKT. Hàng tồn kho, ròng']) / \
                                     sum_by_year['CĐKT. Nợ ngắn hạn']
        sum_by_year['Current_Ratio'] = sum_by_year['CĐKT. TÀI SẢN NGẮN HẠN'] / sum_by_year['CĐKT. Nợ ngắn hạn']
        sum_by_year['Cash_Ratio'] = sum_by_year['CĐKT. Tiền và tương đương tiền '] / sum_by_year['CĐKT. Nợ ngắn hạn']

        print(
            f'Chỉ số thanh toán nhanh, thanh toán hiện hành và thanh toán bằng tiền mặt của ngành Thực phẩm theo năm:\n{sum_by_year[["Quick_Ratio", "Current_Ratio", "Cash_Ratio"]]}')
        fig, ax = plt.subplots(figsize=(12, 8))
        # Tính và lưu các chỉ số thanh khoản vào cột mới
        df['Quick_Ratio'] = (df['CĐKT. TÀI SẢN NGẮN HẠN'] - df['CĐKT. Hàng tồn kho, ròng']) / df['CĐKT. Nợ ngắn hạn']
        df['Current_Ratio'] = df['CĐKT. TÀI SẢN NGẮN HẠN'] / df['CĐKT. Nợ ngắn hạn']
        df['Cash_Ratio'] = df['CĐKT. Tiền và tương đương tiền '] / df['CĐKT. Nợ ngắn hạn']

        # Vẽ đường cho BIBICA
        ax.plot(df['Năm'].astype(int), df['Quick_Ratio'], marker='o', linestyle='-', color='blue',
                label='BIBICA - Tỷ số thanh toán nhanh')
        ax.plot(df['Năm'].astype(int), df['Current_Ratio'], marker='o', linestyle='-', color='green',
                label='BIBICA - Tỷ số thanh toán hiện hành')
        ax.plot(df['Năm'].astype(int), df['Cash_Ratio'], marker='o', linestyle='-', color='red',
                label='BIBICA - Tỷ số thanh toán bằng tiền mặt')

        # Vẽ đường cho ngành Thực phẩm của BBC
        ax.plot(sum_by_year.index, sum_by_year['Quick_Ratio'], marker='s', linestyle='-', color='blue',
                label='Thực phẩm - Tỷ số thanh toán nhanh', alpha=0.5)
        ax.plot(sum_by_year.index, sum_by_year['Current_Ratio'], marker='s', linestyle='-', color='green',
                label='Thực phẩm - Tỷ số thanh toán hiện hành', alpha=0.5)
        ax.plot(sum_by_year.index, sum_by_year['Cash_Ratio'], marker='s', linestyle='-', color='red',
                label='Thực phẩm - Tỷ số thanh toán bằng tiền mặt', alpha=0.5)

        # Hiển thị giá trị trực tiếp trên điểm của mỗi năm cho BIBICA
        for year, qr, cr, cratio in zip(df['Năm'], df['Quick_Ratio'], df['Current_Ratio'], df['Cash_Ratio']):
            ax.text(year, qr, f'{qr:.2f}', ha='center', va='bottom', color='black')
            ax.text(year, cr, f'{cr:.2f}', ha='center', va='bottom', color='black')
            ax.text(year, cratio, f'{cratio:.2f}', ha='center', va='bottom', color='black')

        # Hiển thị giá trị trực tiếp trên điểm của mỗi năm cho ngành Thực phẩm của BBC
        for year, qr, cr, cratio in zip(sum_by_year.index, sum_by_year['Quick_Ratio'], sum_by_year['Current_Ratio'],
                                        sum_by_year['Cash_Ratio']):
            ax.text(year, qr, f'{qr:.2f}', ha='center', va='top', color='black')
            ax.text(year, cr, f'{cr:.2f}', ha='center', va='top', color='black')
            ax.text(year, cratio, f'{cratio:.2f}', ha='center', va='top', color='black')

        # Chú thích
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        ax.set_xlabel('Năm')
        ax.set_ylabel('Chỉ số thanh khoản')
        ax.grid(True)

        # Chỉ định điểm chính trên trục X (hiển thị tất cả các năm)
        plt.xticks(df['Năm'].astype(int))

        ## show chart
        st.pyplot(fig)
        #######################################################################
    with tab5:
        st.header("Tỷ lệ nợ vay và Hệ số thanh toán lãi vay từ 2018 đến 2022")
        # Tính tỷ lệ nợ vay và tỷ số thanh toán lãi vay
        df['Debt_to_Equity_Ratio'] = df['CĐKT. NỢ PHẢI TRẢ'] / df['CĐKT. TỔNG CỘNG NGUỒN VỐN'] * 100
        df['TIE_Ratio'] = (df['KQKD. Tổng lợi nhuận kế toán trước thuế'] - df['KQKD. Trong đó: Chi phí lãi vay']) / (
            -df['KQKD. Trong đó: Chi phí lãi vay'])

        # Vẽ biểu đồ
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Vẽ đường cho tỷ lệ nợ vay (trục y bên trái)
        color = 'tab:red'
        ax1.set_xlabel('Năm')
        ax1.set_ylabel('Tỷ lệ nợ vay (%)', color=color)
        ax1.plot(df['Năm'].astype(int), df['Debt_to_Equity_Ratio'], marker='o', linestyle='-', color=color,
                 label='Tỷ lệ nợ vay')
        ax1.tick_params(axis='y', labelcolor=color)

        # Tạo trục y phụ
        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('Hệ số thanh toán lãi vay', color=color)
        ax2.plot(df['Năm'].astype(int), df['TIE_Ratio'], marker='o', linestyle='-', color=color,
                 label='Hệ số thanh toán lãi vay')
        ax2.tick_params(axis='y', labelcolor=color)

        # Hiển thị giá trị trực tiếp trên điểm của mỗi năm
        for year, debt_ratio, tie_ratio in zip(df['Năm'], df['Debt_to_Equity_Ratio'], df['TIE_Ratio']):
            ax1.text(year, debt_ratio, f'{debt_ratio:.2f}', ha='center', va='bottom', color='black')
            ax2.text(year, tie_ratio, f'{tie_ratio:.2f}', ha='center', va='bottom', color='black')

        # Đặt chú thích cho biểu đồ
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper left', bbox_to_anchor=(0, 0.95))

        # Chỉ định điểm chính trên trục X (hiển thị 5 năm)
        plt.xticks(df['Năm'].astype(int).iloc[::1][-5:])

        # Hiển thị biểu đồ
        st.pyplot(fig)
    with tab6:
        st.header("Biểu đồ Dòng tiền từ năm 2018 đến 2022")
        # Chọn các cột quan trọng
        df_dong_tien = df[['Năm',
                           'LCTT. Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh ',
                           'LCTT. Lưu chuyển tiền tệ ròng từ hoạt động đầu tư ',
                           'LCTT. Lưu chuyển tiền tệ từ hoạt động tài chính ',
                           'LCTT. Tiền và tương đương tiền cuối kỳ ']]
        df_dong_tien.iloc[:, 1:] = df_dong_tien.iloc[:, 1:] / 1e9
        # Chuyển cột 'Năm' sang kiểu số nguyên
        df_dong_tien['Năm'] = df_dong_tien['Năm'].astype(int)

        # Vẽ biểu đồ cột
        fig, ax = plt.subplots(figsize=(12, 8))
        bar_width = 0.2
        bar_positions = range(len(df_dong_tien['Năm']))

        # Vẽ từng cột cho mỗi loại dòng tiền
        for i, col in enumerate(df_dong_tien.columns[1:-1]):
            ax.bar([pos + i * bar_width for pos in bar_positions], df_dong_tien[col], width=bar_width, label=col,
                   alpha=0.7)

        # Vẽ đường cho cột cuối cùng và điểm hiển thị giá trị
        line = ax.plot([pos + i * bar_width for i, pos in enumerate(bar_positions)],
                       df_dong_tien.iloc[:, -1], marker='o', linestyle='-', color='red',
                       label='LCTT. Tiền và tương đương tiền cuối kỳ')
        # Hiển thị giá trị trực tiếp trên từng cột (trừ cột cuối cùng)
        for i, col in enumerate(df_dong_tien.columns[1:-1]):
            for pos, value in zip([pos + i * bar_width for pos in bar_positions], df_dong_tien[col]):
                ax.text(pos, value, f'{value:.2f}', ha='center', va='bottom', color='black')

        # Hiển thị giá trị trực tiếp trên đường
        for pos, value, year in zip([pos + i * bar_width for i, pos in enumerate(bar_positions)],
                                    df_dong_tien.iloc[:, -1], df_dong_tien['Năm']):
            ax.annotate(f'{value:.2f}', xy=(pos, value), xytext=(pos, value), ha='center', va='bottom', color='red',
                        arrowprops=dict(facecolor='red', arrowstyle='wedge,tail_width=0.7', lw=0.5))

        ax.set_xlabel('Năm')
        ax.set_ylabel('Dòng tiền (ĐVT: Tỷ đồng)')
        ax.set_xticks([pos + (len(df_dong_tien.columns) - 2) * bar_width / 2 for pos in bar_positions])
        ax.set_xticklabels(df_dong_tien['Năm'])
        ax.axhline(0, color='black', linewidth=2, linestyle='--')

        # Điều chỉnh vị trí và kích thước của bảng chú thích
        ax.legend(bbox_to_anchor=(0.7, 1.0))
        # show chart
        st.pyplot(fig)
    with tab7:
        st.header("So sánh tỉ số giá trị thị trường của BBC và ngành")
        ##################  So sánh tỉ số giá trị thị trường của BBC và ngành  ####################################
        fig = plt.subplots(figsize=(10, 6))
        # Convert 'Năm' column to integer
        df_ssi['Năm'] = df_ssi['Năm'].astype(int)

        # Extracting the relevant columns for BBC and the industry
        years = df_ssi['Năm']
        columns_of_interest = ['P/E BBC', 'P/E Toàn ngành',
                               'P/B BBC', 'P/B Toàn ngành',
                               'P/S BBC', 'P/S Toàn ngành']

        # Now let's recreate the figure with the specified adjustments
        fig = go.Figure()

        # Adding traces for BBC and the entire industry for each ratio
        for i in range(0, len(columns_of_interest), 2):
            bbc_column = columns_of_interest[i]
            industry_column = columns_of_interest[i + 1]

            # Determine line color based on the column name
            if 'P/E' in bbc_column:
                line_color_bbc = '#DC0000'  # Màu cho P/E BBC
                line_color_industry = '#F55353'  # Màu cho P/E Toàn ngành
            elif 'P/S' in bbc_column:
                line_color_bbc = '#2D31FA'  # Màu cho P/S BBC
                line_color_industry = '#2192FF'  # Màu cho P/S Toàn ngành
            else:
                line_color_bbc = '#FFBF00'  # Màu cho P/B BBC
                line_color_industry = '#FFEA20'  # Màu cho P/B Toàn ngành

            # Adding trace with markers for each year, and setting line color accordingly
            fig.add_trace(go.Scatter(x=df_ssi['Năm'], y=df_ssi[bbc_column], mode='lines+markers',
                                     name=bbc_column, hoverinfo='x+y', hovertemplate='%{y}',
                                     line=dict(color=line_color_bbc, width=3)))

            # Adding trace with markers for each year, and setting line color accordingly
            fig.add_trace(go.Scatter(x=df_ssi['Năm'], y=df_ssi[industry_column], mode='lines+markers',
                                     name=industry_column, hoverinfo='x+y', hovertemplate='%{y}',
                                     line=dict(color=line_color_industry, width=3)))

        # Updating layout for a clear view
        fig.update_layout(xaxis=dict(title='Year', tickmode='array', tickvals=df_ssi['Năm']),
                          yaxis_title='Value',
                          margin=dict(l=0, r=0, t=30, b=0),
                          hovermode='x')
        # Showing the figure
        st.plotly_chart(fig)
        ###########################################################################################

############


def show_tech():
    #################### BBC Stock Price and Volum #################################
    fig = plt.subplots(figsize=(10, 6))
    # Đường dẫn tới thư mục chứa các file Excel
    file_path = r'D:\Software Package\Price-Vol VN 2015-2023.xlsx'
    df_pv = pd.read_excel(file_path)

    # Tạo dummy data để minh họa, bạn cần thay thế bằng dữ liệu thật từ file của bạn
    dates = pd.date_range(start="2015-01-01", periods=100, freq="B")  # Business days
    close_prices = np.random.uniform(low=100, high=200, size=len(dates))
    volumes = np.random.randint(low=1000, high=10000, size=len(dates))

    # Tạo DataFrame
    bbc_data = pd.DataFrame({'Date': dates, 'Close': close_prices, 'Volume': volumes})

    # Tạo subplot với 2 trục y khác nhau
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        subplot_titles=('BBC Stock Price and Volume',), specs=[[{"secondary_y": True}]])

    # Thêm dữ liệu giá cổ phiếu (Price)
    fig.add_trace(
        go.Scatter(x=bbc_data['Date'], y=bbc_data['Close'], name="Price", mode='lines'),
        secondary_y=False,
    )

    # Thêm dữ liệu khối lượng giao dịch (Volume)
    fig.add_trace(
        go.Bar(x=bbc_data['Date'], y=bbc_data['Volume'], name="Volume", marker_color='rgb(150, 200, 250)', opacity=0.6),
        secondary_y=True,
    )

    # Định nghĩa label cho trục x và trục y
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Price", secondary_y=False)
    fig.update_yaxes(title_text="Volume", secondary_y=True)

    # Cập nhật layout để tối ưu hóa không gian biểu đồ
    fig.update_layout(
        autosize=True,
        width=800,
        height=600,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="LightSteelBlue",
    )

    # Hiển thị biểu đồ
    st.plotly_chart(fig)
    ###############################################################################################



# Thanh sidebar cho điều hướng

menu_items = {
    "Trang Chủ": show_home,
    "Phân tích tài chính": show_financials,
    "Phân tích kỹ thuật" : show_tech,
}

# Tạo radio buttons trên sidebar cho điều hướng
selected_btn = st.sidebar.radio("Điều hướng", list(menu_items.keys()))
# chart = st.sidebar.button("Biểu đồ", list(menu_items.keys()))


# Hiển thị trang dựa trên lựa chọn
menu_items[selected_btn]()

# with sidebar:
#
# st.sidebar.markdown('''
#     <div>
#         Streamlit :baloon:
#     </div>
# ''')
