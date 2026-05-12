# 札幌人口マップ

## 1. 概要

以下の２つの公開データを使用して、札幌市内の町名・条丁目単位で人口を確認したり、ある年度間の差分を比較できます。

* [e-stat 境界データ](https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2020&serveyId=A002005212020&prefCode=01&coordsys=1&format=shape&datum=2000)
* [札幌市 町名・条丁目別世帯数及び男女別人口](https://www.city.sapporo.jp/toukei/jinko/juuki/juuki.html#jou-choume-5)

## 2. 使い方

1. python 3.10をインストール
2. パイソンパッケージをインストール `pip install -r requirement.txt`
3. アプリの起動 `streamlit run sapporo_population_map.py`

## 3. デモ(streamlit community cloud)

* [app](https://sapporopopulationmap-xpw5k5sfavu5ruunjta39s.streamlit.app/)
