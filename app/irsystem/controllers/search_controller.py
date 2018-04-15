from . import * 
from app.irsystem.models.tea import Tea
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from flask_paginate import Pagination, get_page_parameter
from settings import *

project_name = "noveltea"
members_name = "Benjamin Stevens, Bowen Gao, Joshua Lee:, Sasha Badov, Yong Lin Ong"
net_id = "bls235, bg453, jhl298, sb965, yo228"

HITS_RANK = True

@irsystem.route('/', methods=['GET'])
def search():
    q_flavor = request.args.get('flavor')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = None
    if not q_flavor:
        teas = []
        output_message = ''
    else:
        q_flavor = "%".join([flavor.title() for flavor in q_flavor.split(",")])
        raw_teas = Tea.query.filter(Tea.flavors.like("%" + q_flavor + "%")).order_by(Tea.ratingValue.desc())
        if HITS_RANK and raw_teas.count() > 0:
            hits_ranked_tea_id = hits_rank([tea.id for tea in raw_teas.all()])
            # https://stackoverflow.com/questions/29326297/sqlalchemy-filter-by-field-in-list-but-keep-original-order
            from sqlalchemy.sql.expression import case
            ordering = case(
                {id: index for index, id in enumerate(hits_ranked_tea_id)},
                value=Tea.id
            )
            raw_teas = Tea.query.filter(Tea.id.in_(hits_ranked_tea_id)).order_by(ordering)
        total = raw_teas.count()
        teas = raw_teas.offset((page-1)*10).limit(10)

        pagination = Pagination(page=page, total=total, per_page=10, 
                                bs_version=4, record_name="teas")

        q_flavor = q_flavor.replace("%", ", ")

    return render_template('search.html', name=project_name, netid=net_id, 
                            query=q_flavor, teas=teas, 
                            pagination=pagination)


def hits_rank(matchFlavors):
    import pandas as pd
    reviews = pd.read_csv(os.path.join(APP_ROOT, "data/reviews_top_10k.csv") )
    results = reviews[reviews.id.isin(matchFlavors)]

    import networkx as nx
    G = nx.from_pandas_edgelist(results, 'author_url', 'id', create_using=nx.DiGraph())
    h, a = nx.hits(G, max_iter=10000)
    top_teas = {teaid: a[teaid] for teaid in results.id.unique()}
    return sorted(top_teas, key=top_teas.get, reverse=True)