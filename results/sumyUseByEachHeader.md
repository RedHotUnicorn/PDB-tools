# Intro
**Граф** — это форма визуализации, позволяющая показывать и анализировать отношения между сущностями.
## Установка networkx
Чтобы установить этот пакет, используйте команду pip: !pip install networkx
## Терминология
Прежде чем начать отрисовку графа, полезно знать некоторые основы.
## Создание графа
Если захочется создать ориентированный, используйте класс nx.DiGraph(directed=True), который возвращает объект networkx.classes.digraph.DiGraph.
## Добавим узлы
Фрагмент кода ниже добавляет три узла без ребер: G.add_node("Singapore") G.add_node("San Francisco") G.add_node("Tokyo") print(G) # Graph with 3 nodes and 0 edges Помимо функции add_node() для добавления индивидуальных узлов, чтобы добавить множество узлов, можно воспользоваться функцией add_nodes_from(): G.add_nodes_from(["Riga", "Copenhagen"]) print(G) # Graph with 5 nodes and 0 edges Сейчас у графа 5 узлов.
## Добавим ребра
Теперь, когда узлы определены, определим ребра, чтобы соединить их: G.add_edge("Singapore","San Francisco") G.add_edge("San Francisco","Tokyo") G.add_edges_from( [ ("Riga","Copenhagen"), ("Copenhagen","Singapore"), ("Singapore","Tokyo"), ("Riga","San Francisco"), ("San Francisco","Singapore"), ] ) print(G) # Graph with 5 nodes and 6 edges Как и узлы, ребра можно добавлять по одному, при помощи add_edge(), или группами — при помощи add_edges_from() со списком кортежей, представляющих каждый узел.
## Рисуем граф
Я покажу основы отображения сетевых графов при помощи пакета networkx.
## Отображение меток
Эти функции позволяют настраивать внешний вид отдельных узлов, меток и ребер.
## Применение макетов
Помните, что функция draw() каждый раз использует разные макеты?
## Разметка ребер
Фрагмент кода ниже размечает два ребра трех узлов: pos = nx.circular_layout(G) nx.draw(G, pos, with_labels = True) nx.draw_networkx_edge_labels( G, pos, edge_labels={ ("Singapore","Tokyo"): '2 flights daily', ("San Francisco","Singapore"): '5 flights daily', }, font_color='red' )
## Ориентированный граф
Ориентированный граф позволяет увидеть, какие рейсы идут из одного города в другой.
## Настройка узлов
По умолчанию узлы имеют синий цвет и довольно маленький размер.
## Очерчивание узлов
Следующий фрагмент кода задает размер рисунка 10 на 10 дюймов (ширина и высота), а затем функцией set_edgecolor() рисует контур каждого узла: pos = nx.circular_layout(G) options = { 'node_color': 'yellow', 'node_size': 8500, 'width': 1, 'arrowstyle': '-|>', 'arrowsize': 18, } nx.draw(G, pos, with_labels = True, arrows=True, **options) ax = plt.gca() ax.collections[0].set_edgecolor("#000000") Теперь каждый узел обведен черным: Если не установить размер рисунка, граф будет выглядеть так:
## Раскрашивание узлов
Чтобы раскрасить каждый узел разными цветами, можно определить цветовую палитру, такую как в bokeh, и установить значение ключу словаря node_color, затем передав его в draw(): from networkx import * import matplotlib.pyplot as plt from bokeh.palettes import Spectral plt.figure(figsize=(8, 8)) pos = nx.circular_layout(G) options = { 'node_color': Spectral[5], # first 5 colors from the Spectral palette 'node_size': 8500, 'width': 1, 'arrowstyle': '-|>', 'arrowsize': 18, } nx.draw(G, pos=pos, with_labels = True, arrows=True, **options) ax = plt.gca() ax.collections[0].set_edgecolor("#000000") И теперь узлы графа раскрашены разными цветами: Если захочется указать свой цвет, установите его вручную: options = { 'node_color': ['yellow','magenta','lightblue','lightgreen','pink'], 'node_size': 8500, 'width': 1, 'arrowstyle': '-|>', 'arrowsize': 18, } Вот и все на сегодня.
