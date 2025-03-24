from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import numpy as np
from simplification.cutil import simplify_coords
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon


def process_polygons(polygons):
    # Создаем Shapely полигоны
    shapely_polygons = []
    for poly in polygons:
        if len(poly) < 3:
            continue
        try:
            p = Polygon(poly)
            if not p.is_valid:
                p = p.buffer(0)
            if p.is_valid and not p.is_empty:
                shapely_polygons.append(p)
        except:
            continue

    if not shapely_polygons:
        return []

    # Объединение пересекающихся полигонов
    union = unary_union(shapely_polygons)

    # Разделение MultiPolygon
    merged_polygons = []
    if isinstance(union, MultiPolygon):
        merged_polygons = list(union.geoms)
    else:
        merged_polygons = [union]

    # Удаление вложенных полигонов
    filtered_polygons = []
    for i, a in enumerate(merged_polygons):
        is_inside = False
        for j, b in enumerate(merged_polygons):
            if i != j and b.area > a.area:
                intersection = a.intersection(b)
                if intersection.area / a.area > 0.9:
                    is_inside = True
                    break
        if not is_inside:
            filtered_polygons.append(a)

    # Упрощение полигонов
    simplified_polygons = []
    for poly in filtered_polygons:
        coords = np.array(poly.exterior.coords)
        if len(coords) > 10:
            tolerance = 1.5
            simple_coords = simplify_coords(coords, tolerance)
            while len(simple_coords) > 10 and tolerance < 10:
                tolerance += 1.0
                simple_coords = simplify_coords(coords, tolerance)
            if len(simple_coords) > 10:
                step = max(1, len(simple_coords) // 10)
                simple_coords = simple_coords[::step][:10]
            if len(simple_coords) >= 3:
                if (simple_coords[0] != simple_coords[-1]).any():
                    simple_coords = np.vstack([simple_coords, simple_coords[0]])
                simplified = Polygon(simple_coords)
                if not simplified.is_valid:
                    simplified = simplified.buffer(0)
                if simplified.is_valid:
                    simplified_polygons.append(simplified)
        else:
            simplified_polygons.append(poly)

    # Преобразование обратно в кортежи
    result = []
    for sp in simplified_polygons:
        if sp.is_empty or not sp.is_valid:
            continue
        coords = list(sp.exterior.coords)
        if len(coords) > 10:
            coords = coords[:10]
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        if len(coords) >= 3:
            coords = [tuple(map(int, coord)) for coord in coords[:-1]]
            result.append(coords)

    return result


def plot_polygons(polygons_list, title, color='blue'):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.set_title(title)

    for i, poly in enumerate(polygons_list):
        closed_poly = poly + [poly[0]]
        mpl_poly = MplPolygon(
            closed_poly,
            closed=True,
            edgecolor=color,
            facecolor=color,  # Исправлено здесь
            alpha=0.3,  # Добавлен отдельный параметр прозрачности
            linewidth=2,
            linestyle='--' if 'Before' in title else '-'
        )
        ax.add_patch(mpl_poly)

    ax.autoscale_view()
    plt.grid(True)
    plt.xlabel('X')
    plt.ylabel('Y')


# Пример данных
input_polygons = [
    [(234, 365), (218, 379), (213, 460), (215, 769), (242, 776), (435, 772), (437, 546), (397, 411), (376, 383),
     (335, 365)],
    [(394, 464), (304, 648), (242, 674), (227, 600), (225, 837), (274, 928), (503, 943), (516, 791), (625, 687)]
]


#plot_polygons(input_polygons, 'Before Processing', 'red')


#processed = process_polygons(input_polygons)


#plot_polygons(processed, 'After Processing', 'green')


#plt.show()