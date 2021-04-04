import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib as mpl
from celluloid import Camera
import streamlit.components.v1 as components

with st.echo(code_location='below'):
    st.title("Бессмысленные и беспощадные")
    """
    Выборы в США: 1976 - 2020
    """

    """
    Немого общей статистики - голоса за демократов и республиканцев:
    """
    st.set_option('deprecation.showPyplotGlobalUse', False)
    data = pd.read_csv("1976-2020-president.csv")
    data = data.drop(['state_fips', 'state_cen', 'state_ic', 'office', 'writein', 'version', 'notes'], axis='columns')
    data['percentage'] = data["candidatevotes"] / data["totalvotes"]
    geo_states = gpd.read_file("https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_1_states_provinces.zip")
    geo_states = geo_states[geo_states["iso_a2"] == "US"]
    geo_states['name'] = geo_states['name'].apply(lambda x: x.upper())
    geo_states = geo_states[['name', 'geometry']]
    geo_states["rp"] = geo_states['geometry'].representative_point()
    #geo_states['ctr'] = geo_states['geometry'].to_crs({'init': 'epsg:3395'}).centroid
    df = geo_states.merge(data, how="right", left_on="name", right_on="state")
    df['area'] = df['geometry'].to_crs({'init': 'epsg:3395'}).map(lambda
                                                                      p: p.area / 10 ** 6)  # (copy from https://gis.stackexchange.com/questions/218450/getting-polygon-areas-using-geopandas)

    fig=plt.figure(figsize=(7, 7))
    camera = Camera(fig)
    for year in df["year"].unique():
        sample_1 = df[(df["year"] == year) & (df["candidatevotes"] > 100000)]
        a = sample_1.groupby("party_detailed")["candidatevotes"].sum().reindex(
        index=['DEMOCRAT', 'REPUBLICAN', "LIBERTARIAN"])
        a.plot.bar(color=['blue', 'red', 'black'])
        plt.xticks(rotation=30, horizontalalignment="center")
        plt.title("Votes for Democrat and Republican Candidates in {}".format(year), fontweight='bold', pad=25)
        plt.xlabel("Party", fontsize=8)
        plt.ylabel("Number of votes for a candidate from the party", fontsize=8)
        camera.snap()
    animation = camera.animate(interval=200, repeat=True, repeat_delay=400)
    components.html(animation.to_jshtml(), height=1000)


    dict_col = {'DEMOCRAT': ["Blues", "демократ!"], 'REPUBLICAN': ["Reds", "республиканец!"]}

    selected_year= st.selectbox("Выберите год", df['year'].unique())

    a = int(selected_year)
    sample_zero = df[(df["year"] == a)]
    win = sample_zero.groupby("party_simplified")["candidatevotes"].sum().idxmax()
    if a==2000:
        prez = 'GORE, AL'
        st.write(f"В {selected_year!r} году больше всего голосов получил(а) "+ dict_col[win][1]+
             " (хотя президентом стал {}.)".format(prez)+ " Но все же посмотрим, как зовоеывал штаты кандидат, получивший большинство голосов:")
    elif a==2016:
        prez = 'TRUMP, DONALD J.'
        st.write(f"В {selected_year!r} году больше всего голосов получил(а) " + dict_col[win][1] +
                 " (хотя президентом стал {})".format(prez) + ". Но все же посмотрим, как зовоеывал штаты кандидат, получивший большинство голосов:")
    else:
        st.write(f"В {selected_year!r} году победил "+ dict_col[win][1]+ " Вот как он завоевывал штаты:")

    b=win
    sample = df[(df["year"] == a) & (df["party_simplified"] == b)]
    sample.plot(column='percentage', norm=mpl.colors.Normalize(vmin=0, vmax=1), figsize=(25, 15), legend=True, cmap=dict_col[win][0],
                  legend_kwds={'label': "Share of votes"})
    plt.xlim(-130, -65)
    plt.ylim(20, 55)
    title = 'Elections {}: {} - {} candidate'.format(a, df[(df["year"] == a) & (df["party_simplified"] == b)][
            'candidate'].unique()[0], b.lower())
    mpl.pyplot.title(title, fontsize=30, fontweight='bold', loc='center', pad=10)
    for x, y, label in zip(sample['rp'].x - 1.5, sample['rp'].y, sample["state"]):
        if label != 'ALASKA' and label != 'HAWAII' and (sample[sample['state'] == label]['area'] > 40000).to_list()[0]:
            if label == "MISSISSIPPI" or label == 'VERMONT':
                plt.text(x, y + 0.7, label, fontsize=8, color='black', alpha=1, weight="bold")
            elif label == "IDAHO":
                plt.text(x + 1, y - 1, label, fontsize=8, color='black', alpha=1, weight="bold")
            else:
                plt.text(x, y, label, fontsize=8, color='black', alpha=1, weight="bold")
    st.pyplot()


    #selected_regions = st.multiselect("Выберите регионы", data['region_name'].unique())




