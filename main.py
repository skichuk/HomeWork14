import json
import sqlite3
from flask import Flask


app = Flask(__name__)


def get_data_by_sql(sql):
    with sqlite3.connect('./netflix.db') as connection:
        connection.row_factory = sqlite3.Row

        result = connection.execute(sql).fetchall()

    return result


# Возвращаем первую строку базы
@app.get("/")
def get_first():
    result = {}
    for item in get_data_by_sql(sql=f'''
                    SELECT *
                    FROM netflix
                    LIMIT 1
                    '''):
        result = dict(item)

    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


# Поиск по названию
@app.get("/movie/<title>")
def get_title(title):
    result = {}
    for item in get_data_by_sql(sql=f'''
                    SELECT title, country, release_year, listed_in, description
                    FROM netflix
                    WHERE title = '{title}'
                    ORDER BY release_year DESC
                    LIMIT 1
                    '''):
        result = dict(item)
    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


# Поиск в диапазоне годов релиза
@app.get("/movie/<int:year1>/to/<int:year2>")
def get_year_to_year(year1, year2):
    if year1 > year2:
        year1, year2 = year2, year1
    result = []
    for item in get_data_by_sql(sql=f'''
                    SELECT *
                    FROM netflix
                    WHERE release_year BETWEEN {year1} AND {year2}
                    LIMIT 100
                    '''):
        result.append(dict(item))
    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


# Поиск по рейтингу
@app.get("/rating/<rating>")
def get_rating(rating):
    rating_dict = {
        'children': ('G', 'G'),
        'family': ('G', 'PG', 'PG-13'),
        'adult': ('R', 'NC-17'),
    }
    result = []
    for item in get_data_by_sql(sql=f'''
                    SELECT *
                    FROM netflix
                    WHERE rating IN {rating_dict.get(rating, ('G', 'G'))}
                    '''):
        result.append(dict(item))
    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


# Поиск по жанру
@app.get("/genre/<genre>")
def get_genre(genre):
    result = []
    for item in get_data_by_sql(sql=f'''
                    SELECT title, description
                    FROM netflix
                    WHERE listed_in LIKE '%{str(genre).title()}%'
                    '''):
        result.append(dict(item))
    return app.response_class(
        json.dumps(result, ensure_ascii=False, indent=4),
        mimetype="application/json",
        status=200
    )


# Поиск "частых" напарников к двум актерам
def get_by_two_casts(name1='Rose McIver', name2='Ben Lamb'):
    sql = f'''
        SELECT netflix.cast
        FROM netflix
        WHERE netflix.cast LIKE '%{name1}%' AND netflix.cast LIKE '%{name2}%'
        '''

    names_dict = {}

    for item in get_data_by_sql(sql):
        result = dict(item)

        names = set(result.get("cast").split(', ')) - set([name1, name2])

        for name in names:
            names_dict[name.strip()] = names_dict.get(name.strip(), 0) + 1

    print(names_dict)
    for key, value in names_dict.items():
        if value >= 2:
            print(key)

# Вывод названия и описания по типу, году и жанру
def get_title_with_description(types='Movie', year=2019, genre='Dramas'):
    sql = f'''
            SELECT title, description
            FROM netflix
            WHERE type LIKE '{types.title()}' AND release_year LIKE '{year}' AND listed_in LIKE '%{genre.title()}%'
            '''

    result = []

    for item in get_data_by_sql(sql):
        result.append(dict(item))

    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
