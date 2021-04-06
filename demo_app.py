import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib as mpl
from celluloid import Camera

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

    vbr = []
    hhh = []
    for i in range(9):
        vbr.append("{}0M".format(i))
        hhh.append(i * 10 ** 7)

    fig, ax = plt.subplots(figsize=(6, 6))
    camera = Camera(fig)
    for year1 in df["year"].unique():
        sample_1 = df[(df["year"] == year1) & (df["candidatevotes"] > 100000)]
        a = sample_1.groupby("party_detailed")["candidatevotes"].sum().reindex(
        index=['DEMOCRAT', 'REPUBLICAN', "LIBERTARIAN"])
        a.plot.bar(color=['mediumblue', 'red', 'black'])
        plt.xticks(rotation=0, horizontalalignment="center")
        ax.text(0.15, 1.03, "Votes for three parties in {}".format(year1), transform=ax.transAxes, fontsize=14, fontweight='bold')
        plt.xlabel("", fontsize=12)
        plt.ylabel("NUMBER OF VOTES", fontsize=12)
        plt.yticks(hhh, vbr)
        camera.snap()
    animation = camera.animate(interval=600, repeat=True, repeat_delay=400)
    st.components.v1.html(animation.to_jshtml(), height=700, scrolling=True)

    """""
    """
    
    #Теперь наше естественное желание - понять, как каждый штат менял предпочтения за эти годы. Посмотрим!
    
    """

    simply = df[(df['party_simplified'] == 'DEMOCRAT') | (df['party_simplified'] == 'REPUBLICAN')]
    simply1 = simply.drop(df.columns.difference(['name', 'year', 'percentage', 'party_simplified']), 1).copy()
    dem = simply1[simply1['party_simplified'] == 'DEMOCRAT'].copy()
    rep = simply1[simply1['party_simplified'] == 'REPUBLICAN'].copy()
    df['wh'] = df['name'] + df['year'].astype(str)
    dem['wh'] = dem['name'] + dem['year'].astype(str)
    rep['wh'] = rep['name'] + rep['year'].astype(str)
    margins = dem.merge(rep, left_on='wh', right_on='wh').copy()
    margins['marg'] = -margins["percentage_x"] + margins["percentage_y"]
    margins2 = margins.drop(margins.columns.difference(['wh', 'marg']), 1)
    df = df.merge(margins2, left_on='wh', right_on='wh')
    margins = margins.drop(margins.columns.difference(['wh', 'marg', "name_x", "year_x"]), 1)
    margins = margins.pivot_table(index='name_x', columns='year_x', values='marg')

    fig = plt.figure(figsize=(20, 15))
    sns.heatmap(margins, vmin=-0.25, vmax=0.25, center=0, cmap='coolwarm', yticklabels=True, linewidths=1.7)
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('State', fontsize=12, fontweight='bold')
    plt.title('% margin (%Republican - %Democrat) for each state', fontsize=16, fontweight='bold', pad=20)

    st.pyplot()

    dict_col = {'DEMOCRAT': ["Blues", "демократ!"], 'REPUBLICAN': ["Reds", "республиканец!"]}
    """
    #___
    """
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




selected_regions = st.multiselect("Выберите регионы", data['region_name'].unique())


"""

