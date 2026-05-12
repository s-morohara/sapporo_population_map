import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np

import os
import glob

import unicodedata
import re

def convert_kanji_to_int(string) -> str:
    """漢数字を半角数字に変換する

    Args:
        string (str): 住所の文字列

    Returns:
        result (str): 変換後の文字列
    """
    result = string.translate(str.maketrans("零〇一壱二弐三参四五六七八九拾", "00112233456789十", ""))
    convert_table = {"十": "0", "百": "00", "千": "000", "万": "0000", "億": "00000000", "兆": "000000000000", "京": "0000000000000000"}
    unit_list = "|".join(convert_table.keys())
    while re.search(unit_list, result):
        for unit in convert_table.keys():
            zeros = convert_table[unit]
            for numbers in re.findall(f"(\d+){unit}(\d+)", result):
                result = result.replace(numbers[0] + unit + numbers[1], numbers[0] + zeros[len(numbers[1]):len(zeros)] + numbers[1])
            for number in re.findall(f"(\d+){unit}", result):
                result = result.replace(number + unit, number + zeros)
            for number in re.findall(f"{unit}(\d+)", result):
                result = result.replace(unit + number, "1" + zeros[len(number):len(zeros)] + number)
            result = result.replace(unit, "1" + zeros)
    return result

def change_name(string) -> str:
    """八軒と二十四軒をもとに戻す

    Args:
        string (str): 住所の文字列

    Returns:
        string (str): 変換後の文字列
    """
    if "8軒" in string:
        return string.replace("8軒", "八軒")
    elif "24軒" in string:
        return string.replace("24軒", "二十四軒")
    else:
        return string

def remove_banch(string) -> str:
    """住所の文字列から(番地)を削除する

    Args:
        string (str): 住所の文字列

    Returns:
        string (str): 変換後の文字列
    """
    return string.replace("(番地)", "")

def remove_comma(string) -> str:
    """住所の文字列からカンマを削除する

    Args:
        string (str): 住所の文字列

    Returns:
        string (str): 変換後の文字列
    """
    return string.replace(",", "")

def remove_space(string) -> str:
    """住所の文字列から空白を削除する

    Args:
        string (str): 住所の文字列

    Returns:
        string (str): 変換後の文字列
    """
    return string.replace(" ", "")

def remove_irregal(string) -> str:
    """不規則な値を0に変換する

    Args:
        string (str): 住所の文字列

    Returns:
        string (str): 変換後の文字列
    """
    if "-" == string or "x" == string or "−" == string:
        return "0"
    else:
        return string

def load_city_data(city_data_path) -> pd.DataFrame:
    """都道府県データの読み込み

    Args:
        city_data_path (str): 町名・条丁目別世帯数及び男女別人口データのファイルパス

    Returns:
        df (pd.DataFrame): 読み込んだデータ
    """
    df = pd.read_csv(city_data_path, encoding="shift_jis")

    # 地名の正規化
    df["地名"] = df["地名"].map(lambda x: unicodedata.normalize('NFKC', x))
    df["地名"] = df["地名"].map(remove_banch)
    df["地名"] = df["地名"].map(change_name)
    df["地名"] = df["地名"].map(remove_space)

    # 町名・条丁目別世帯数及び男女別人口の数値列の正規化
    df_columns = df.columns[1:].tolist()
    for column in df_columns:
        df[column] = df[column].map(remove_comma)
        df[column] = df[column].map(remove_irregal)

        df[column] = df[column].astype(np.int64)
        # pacentile99 = df[column].quantile(0.99)
        # df[column] = df[column].map(lambda x: pacentile99 if int(x) > pacentile99 else x)

    return df

###################################################
# データ前処理
###################################################

# サブフォルダ内のshpファイル(地図データ)のパスを取得
shapefiles = glob.glob(os.path.join("map_data", "**", "*.shp"))
shapefiles.sort()
# shpファイルの読み込み
print(f"Loading shapefile: {shapefiles}")
gdfs = [gpd.read_file(f) for f in shapefiles]
# 読み込んだGeoDataFrameを結合して1つのGeoDataFrameにする
gdf_combined = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
gdf_combined["S_NAME"] = gdf_combined["S_NAME"].map(convert_kanji_to_int)
gdf_combined["S_NAME"] = gdf_combined["S_NAME"].map(lambda x: unicodedata.normalize('NFKC', x))
gdf_combined["S_NAME"] = gdf_combined["S_NAME"].map(change_name)

# 町名・条丁目別世帯数及び男女別人口データのパスを取得
city_data_list = glob.glob(os.path.join("city_data", "*.csv"))
city_data_list.sort()

###################################################
# streamlit事前設定
###################################################

# セレクトボックス用の年ラベルを作成
year_label = {}
for city_path in city_data_list:
    year_name = os.path.basename(city_path).split(".")[0]
    year_label[year_name] = city_path
# セレクトボックス用の統計量ラベルを設定
df_columns = pd.read_csv(city_data_list[-1], encoding="shift_jis").columns[1:].tolist()

# ページ設定
st.set_page_config(
    page_title="札幌人口マップ(町名・条丁目別)",
    layout="wide",
)

###################################################
# サイドバー設定とデータの読み込み
###################################################

# サイドバー設定
with st.sidebar:
    year_option = st.selectbox(
        "確認したい年",
        list(year_label.keys()),
        index=len(year_label)-1,
    )

    compare_option = st.selectbox(
        "比較したい年(任意)",
        list(year_label.keys()),
        index=None,
    )

    stat_option = st.selectbox(
        "統計量",
        df_columns,
    )

# 町名・条丁目別世帯数及び男女別人口のデータを読み込む
df = load_city_data(year_label[year_option])
# 比較用の町名・条丁目別世帯数及び男女別人口のデータを読み込む
if compare_option is not None:
    df_compare = load_city_data(year_label[compare_option])

    diff = df.set_index('地名') - df_compare.set_index('地名')
    df = diff.fillna(0).reset_index()

    for column in df_columns:
        # pacentile1 = df[column].quantile(0.01)
        # df[column] = df[column].map(lambda x: pacentile1 if int(x) < pacentile1 else x)
        pass

    color_continuous_scale="Jet"
else:
    color_continuous_scale="Viridis"

###################################################
# マップの表示
###################################################

# GeoDataFrameと町名・条丁目別世帯数及び男女別人口のDataFrameを地名をキーにして結合する
new_gdf =pd.merge(gdf_combined, df, left_on="S_NAME", right_on="地名", how="left")
for column in df_columns:
    new_gdf[column] = new_gdf[column].fillna(0)

# plotyを使用して地図を描写する
fig = px.choropleth_mapbox(
    new_gdf,
    geojson=new_gdf.geometry,
    locations=new_gdf.index,
    color=stat_option,
    color_continuous_scale=color_continuous_scale,
    hover_data=["S_NAME"],
    mapbox_style="carto-positron",
    center={"lat": new_gdf.geometry.centroid.y.mean(), "lon": new_gdf.geometry.centroid.x.mean()},
    zoom=12,
    opacity=0.5
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Streamlitで表示する
st.plotly_chart(fig, width=2000, height=1000)

"""
データ元
* [e-stat 境界データ](https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2020&serveyId=A002005212020&prefCode=01&coordsys=1&format=shape&datum=2000)
* [札幌市 町名・条丁目別世帯数及び男女別人口](https://www.city.sapporo.jp/toukei/jinko/juuki/juuki.html#jou-choume-5)
"""