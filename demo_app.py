import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib as mpl
from celluloid import Camera
import altair as alt
from vega_datasets import data


from matplotlib.animation import ArtistAnimation
with st.echo(code_location='below'):
    st.title("STOP THE COUNT! (c)")
    """
    Выборы в США: 1976 - 2020. Пожалуйста, подождите пока страница полностью загрузится (не больше 2 минут).
    """
    """
    Использованные библиотеки (помимо matplotlib): график 1 (анимация) - celluloid, графики 2,4,5 -  seaborn, график 3 - geopandas, остальные графики (интерактивность) - altair.
    """

    """
    Немного общей статистики - голоса за демократов и республиканцев в течение 44 лет:
    """
    st.set_option('deprecation.showPyplotGlobalUse', False)

    filea = "1976-2020-president.csv"
    fileb = "ne_50m_admin_1_states_provinces.shp"

    datain = pd.read_csv(filea)
    datain = datain.drop(['state_fips', 'state_cen', 'state_ic', 'office', 'writein', 'version', 'notes'], axis='columns')
    datain['percentage'] = datain["candidatevotes"] / datain["totalvotes"]
    geo_states = gpd.read_file(fileb)
    geo_states = geo_states[geo_states["iso_a2"] == "US"]
    geo_states['name'] = geo_states['name'].apply(lambda x: x.upper())
    geo_states = geo_states[['name', 'geometry']]
    geo_states["rp"] = geo_states['geometry'].representative_point()
    df = geo_states.merge(datain, how="right", left_on="name", right_on="state")
    df['area'] = df['geometry'].to_crs({'init': 'epsg:3395'}).map(lambda p: p.area / 10 ** 6) # (this line - from https://gis.stackexchange.com/questions/218450/getting-polygon-areas-using-geopandas)
    df['wh'] = df['name'] + df['year'].astype(str)
    all_years=list(df["year"].unique())

    vbr = []
    hhh = []
    for i in range(9):
        vbr.append("{}0M".format(i))
        hhh.append(i * 10 ** 7)
    fig, ax = plt.subplots(figsize=(5, 3))
    camera = Camera(fig)
    for year1 in all_years:
        sample_1 = df[(df["year"] == year1) & (df["candidatevotes"] > 100000)]
        a = sample_1.groupby("party_detailed")["candidatevotes"].sum().reindex(
        index=['DEMOCRAT', 'REPUBLICAN', "LIBERTARIAN"])
        a.plot.bar(color=['#3d50bd', 'darkred', 'black'])
        plt.xticks(rotation=0, horizontalalignment="center", fontsize=8)
        ax.text(0.19, 1.03, "Votes for three parties in {}".format(year1), transform=ax.transAxes, fontsize=10, fontweight='bold')
        plt.xlabel("", fontsize=8)
        plt.ylabel("NUMBER OF VOTES", fontsize=8)
        plt.yticks(hhh, vbr, fontsize=8)
        camera.snap()
    animation = camera.animate(interval=400, repeat=True, repeat_delay=400)
    st.components.v1.html(animation.to_jshtml(), height=400, scrolling=True)


    """
    
    Теперь наше естественное желание - понять, как каждый штат менял предпочтения за эти годы. Посмотрим!
    Hint: чтобы не ждать слишком долго, продолжайте выбирать штаты, даже когда экран стал серым. 
    
    """


    simply = df[(df['party_simplified'] == 'DEMOCRAT') | (df['party_simplified'] == 'REPUBLICAN')]
    simply1 = simply.drop(df.columns.difference(['name', 'year', 'percentage', 'party_simplified']), 1).copy()
    dem = simply1[simply1['party_simplified'] == 'DEMOCRAT'].copy()
    rep = simply1[simply1['party_simplified'] == 'REPUBLICAN'].copy()
    dem['wh'] = dem['name'] + dem['year'].astype(str)
    rep['wh'] = rep['name'] + rep['year'].astype(str)
    margins = dem.merge(rep, left_on='wh', right_on='wh').copy()
    margins['marg'] = -margins["percentage_x"] + margins["percentage_y"]
    margins2 = margins.drop(margins.columns.difference(['wh', 'marg']), 1)
    margins = margins.drop(margins.columns.difference(['wh', 'marg', "name_x", "year_x"]), 1)
    margins_main = margins.pivot_table(index='name_x', columns='year_x', values='marg')

    df = df.merge(margins2, left_on='wh', right_on='wh')
    selected_states=st.multiselect("Выберите названия штатов (как минимум 4):", list(df['name'].unique()))#, default=lt)
    selected_states=list(selected_states)
    if len(selected_states)>3:
        k=margins_main.loc[selected_states]
        fig = plt.figure(figsize=(15, 0.5 * len(selected_states)))
        sns.heatmap(k, vmin=-0.3, vmax=0.3, center=0, cmap='coolwarm', yticklabels=True, linewidths=3)
        plt.xlabel('Year', fontsize=14, fontweight='bold')
        plt.ylabel('State', fontsize=14, fontweight='bold')
        plt.title('% margin (%Republican - %Democrat) for each state', fontsize=16, fontweight='bold', pad=20)
        st.pyplot()
    else:
        st.write('Пока Вы выбрали меньше 4 штатов!')


    dict_col = {'DEMOCRAT': ["Blues", "демократ!"], 'REPUBLICAN': ["Reds", "республиканец!"]}
    """

    Теперь можно увидеть общую картину по каждым выборам: 

    """
    selected_year= st.selectbox("Выберите год", df['year'].unique())
    a = int(selected_year)
    sample_zero = df[(df["year"] == a)]
    dem_cand = str(sample_zero[sample_zero['party_detailed'] == 'DEMOCRAT']['candidate'].unique()[0])
    rep_cand = str(sample_zero[sample_zero['party_detailed'] == 'REPUBLICAN']['candidate'].unique()[0])
    st.write("В {} году участвовали политики {} от республиканцев и {} от демократов.".format(a, rep_cand, dem_cand))
    win = sample_zero.groupby("party_simplified")["candidatevotes"].sum().idxmax()
    if a==2000:
        prez = 'GORE, AL'
        st.write(f"В {selected_year!r} году больше всего голосов получил(а) "+ dict_col[win][1]+
             " (хотя президентом стал {}.)".format(prez)+" А вот как голосовали штаты (на графике - разница между результатами республиканца и демократа в процентных пунтках):")
    elif a==2016:
        prez = 'TRUMP, DONALD J.'
        st.write(f"В {selected_year!r} году больше всего голосов получил(а) " + dict_col[win][1] +
                 " (хотя президентом стал {}).".format(prez) +" А вот как голосовали штаты (на графике - разница между результатами республиканца и демократа в процентных пунтках):")
    else:
        st.write(f"Победил "+ dict_col[win][1]+ " А вот как голосовали штаты (на графике - разница между результатами республиканца и демократа в процентных пунтках):")

    """
     
     
    """
    sample5 = df[(df["year"] == a) & (df["party_simplified"] == "DEMOCRAT")]
    sample5.plot(column='marg', vmin=-0.3, vmax=0.3, figsize=(25, 15), legend=True, cmap='coolwarm')
    plt.xlim(-130, -65)
    plt.ylim(20, 55)
    title = 'Elections {}: state-level margin'.format(a)
    mpl.pyplot.title(title, fontsize=20, fontweight='bold', loc='center', pad=10)
    for x, y, label in zip(sample5['rp'].x - 1.5, sample5['rp'].y, sample5["state"]):
        if label != 'ALASKA' and label != 'HAWAII' and (sample5[sample5['state'] == label]['area'] > 40000).to_list()[
            0]:
            if label == "MISSISSIPPI" or label == 'VERMONT':
                plt.text(x, y + 0.7, label, fontsize=8, color='black', alpha=1, weight="bold")
            elif label == "IDAHO":
                plt.text(x + 1, y - 1, label, fontsize=8, color='black', alpha=1, weight="bold")
            else:
                plt.text(x, y, label, fontsize=8, color='black', alpha=1, weight="bold")
    plt.text(-56, 35, "Share of votes", fontsize=14, color='black', weight="bold", rotation='vertical')
    st.pyplot()

    """
    
    А это график с количеством выборщиков у каждого штата. Если президентом стал не тот кандидат, который набрал большинство голосов, то все дело в этом (на кружок можно навести курсор и увидеть название штата и количество выборщиков):

    """
    college = pd.read_csv("Electoral_College.csv")
    college = college[college['Year'] >= 1976]
    college['Votes'] = college['Votes'].astype(int)
    votes = college.copy()
    college['State'] = college['State'].apply(lambda x: x.upper())
    college['wh'] = college['State'] + college['Year'].astype(str)
    college["Votes"] = college["Votes"].apply(lambda x: int(x))
    df = df.merge(college, left_on='wh', right_on='wh')

    votes = votes[votes['Year'] == a]
    votes['electors'] = votes['Votes']

    longlat = pd.read_csv("longlat.csv")
    longlat.drop(['country_code', 'latitude', 'longitude', 'country'], 1)
    votes = votes.merge(longlat, left_on='State', right_on='usa_state')
    states = alt.topo_feature(data.us_10m.url, 'states')

    background = alt.Chart(states).mark_geoshape(
        fill='grey',
        stroke='white').properties(width=650,height=400).project('albersUsa')

    points = alt.Chart(votes).mark_circle().encode(
        latitude='usa_state_latitude',
        longitude='usa_state_longitude',
        size=alt.Size('Votes', title='Number of Electors', scale=alt.Scale(range=[100, 2000])),
        color=alt.value('darkred'),
        tooltip=['usa_state', 'electors']).properties(title='United States Electoral College {}'.format(a))

    st.altair_chart(alt.layer(background, points))

    st.subheader("Трамп!")
    """
    
    Теперь посмотрим на 2020 год.
    Действительно ли за Трампа голосуют скорее те регионы, в которых преобладают белые и мужчины? Похоже на то, вот регрессии:
    
    """

    table = pd.read_csv("county_statistics.csv")
    table['trump-marg-%'] = table["percentage20_Donald_Trump"] - table["percentage16_Donald_Trump"]
    table['trump-marg-n'] = (table["votes20_Donald_Trump"] - table["votes16_Donald_Trump"]) / (
    table["votes16_Donald_Trump"])
    table['White'] = table['White'] / 100
    table['Men%']=table['Men']/table['TotalPop']


    sns.regplot(x="White", y="percentage20_Donald_Trump", data=table, color='darkred', logistic=True, truncate=False,
                scatter_kws={"s": 20})
    plt.xlabel('% of whites in population', fontsize=28)
    plt.ylabel("% votes for Trump",fontsize=28)
    plt.title('Trump-2020 on white race (county-level)', fontweight='bold',fontsize=30)
    plt.tick_params(labelsize=20)
    st.pyplot()

    sns.regplot(x="Men%", y="percentage20_Donald_Trump", data=table[(table["Men%"]>0.4)&(table["Men%"]<0.6)], color='darkred', logistic=True, truncate=False,
                scatter_kws={"s": 20})
    plt.xlabel('% of men in population', fontsize=28)
    plt.ylabel("% votes for Trump", fontsize=28)
    plt.title('Trump-2020 on male gender (county-level)', fontweight='bold', fontsize=30)
    plt.tick_params(labelsize=20)
    st.pyplot()

    """
    
    Теперь ключевой параметр, который мы будем исследовать - разницу между процентными результатами Трампа.
    Здесь вы можете выбрать штат и посмотреть распределения количества округов в этом штате в зависимости от динамики предпочтений (ЧТО?! ДА!):
    
    """

    table['share of votes for Trump in 2016'] = table['percentage16_Donald_Trump']
    table['share of votes for Trump in 2020'] = table['percentage20_Donald_Trump']
    react = alt.Chart(table).mark_rect().encode(
        alt.X('share of votes for Trump in 2016', bin=True, axis=alt.Axis(format='%', title="Trump's result in 2016")),
        alt.Y('share of votes for Trump in 2020', bin=True, axis=alt.Axis(format='%', title="Trump's result in 2020")),
        alt.Color("trump-marg-%", scale=alt.Scale(scheme='redblue', reverse=True),
                  legend=alt.Legend(title='Margin',  orient="left"))).properties(width=600)

    line = pd.DataFrame({'x': [0, 1], 'y': [0, 1], })
    line_plot = alt.Chart(line).mark_line(color='darkred').encode(x='x', y='y')

    pts = alt.selection(type="single", encodings=['x'])

    circ = react.mark_point().encode(alt.ColorValue('grey'), alt.Size('count()', legend=alt.Legend(
        title='Number of counties in selection'))).transform_filter(pts)

    bar = alt.Chart(table).mark_bar().encode(x='state', y='count()',
                                             color=alt.condition(pts, alt.ColorValue("darkred"), alt.ColorValue("grey"))
                                             ).properties(width=700, height=200).add_selection(pts)

    st.altair_chart(alt.vconcat(react + line_plot + circ, bar).resolve_legend(color="independent", size="independent"))

    """
    Может все дело в ковиде? На следующих графиках стоит поиграться с прямоугольной выборкой (кейсы ковида - данные накануне выборов):
   
    """

    table['%Covid in Population'] = table['cases'] / table['TotalPop']
    table['Democrats: % shift'] = table["percentage20_Joe_Biden"] - table['percentage16_Hillary_Clinton']
    table['Republicans: % shift']=table['trump-marg-%']
    table_45 = table[(table['Republicans: % shift'] > -0.1) & (table['Republicans: % shift'] < 0.1)]
    table_45 = table_45[(table_45['Democrats: % shift'] > -0.1) & (table_45['Democrats: % shift'] < 0.1)]
    table_45 = table_45[(table_45['%Covid in Population'] < 0.13)]
    table_45['Income per capita']=table['IncomePerCap']
    table_45.loc[table_45['percentage20_Joe_Biden'] > table_45['percentage20_Donald_Trump'], 'winner'] = 'DEMOCRAT'
    table_45.loc[table_45['percentage20_Joe_Biden'] < table_45['percentage20_Donald_Trump'], 'winner'] = 'REPUBLICAN'
    drug = alt.selection_interval()
    brush = alt.selection_interval()
    chart1 = alt.Chart(table_45).mark_point().encode(
        y='Republicans: % shift',
        color=alt.condition(drug, alt.Color('winner:N',
                                             scale=alt.Scale(domain=['DEMOCRAT', 'REPUBLICAN'],
                                                             range=['blue', 'darkred'])),
                            alt.value('lightgray'))).properties(width=250, height=250).add_selection(drug)
    hui = chart1.encode(x='Democrats: % shift') | chart1.encode(x='%Covid in Population') & chart1.encode(x='Income per capita')
    st.altair_chart(hui)

    """
    
    Видимо, ковид вообще не сыграл никакой роли. А еще (судя по всему) не Трамп терял голоса, а Байден активнее мобилизовывал демократический электорат. 
    
    """


    st.title("ну, спасибо им большое за их борьбу..")
