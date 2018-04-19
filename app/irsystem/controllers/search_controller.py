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
    version = request.args.get('version')
    if version == "1":
        return search_v1()
    else:
        return search_v2()

def search_v2():
    raw_query = request.args.get('flavor')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = None

    if not raw_query:
        q_flavor = ""
        teas = []
        output_message = ""
    else:
        q_flavor = ", ".join([flavor.title().strip() for flavor in raw_query.split(",")])

        flavors_AND_query = " AND ".join(["teas.flavors LIKE '%" + flavor.title().strip() + "%'" for flavor in raw_query.split(",")])
        raw_teas_AND = Tea.query.filter(flavors_AND_query).order_by(Tea.ratingValue.desc())

        flavor_OR_query = " OR ".join(["teas.flavors LIKE '%" + flavor.title().strip() + "%'" for flavor in raw_query.split(",")])
        raw_teas_OR = Tea.query.filter(flavor_OR_query).order_by(Tea.ratingValue.desc())

        if (raw_teas_AND.count() + raw_teas_OR.count()) > 0:            
            if HITS_RANK:
                print "Found {} teas".format(raw_teas_AND.count() + raw_teas_OR.count())
                hits_ranked_AND = hits_rank([tea.id for tea in raw_teas_AND.all()])
                hits_ranked_OR = hits_rank([tea.id for tea in raw_teas_OR.all()])
                hits_ranked_tea_id = hits_ranked_AND + [tea_id for tea_id in hits_ranked_OR if tea_id not in hits_ranked_AND]

                print "Found {} teas after HITS algo".format(len(hits_ranked_tea_id))
                raw_teas = Tea.query.filter(Tea.id.in_(hits_ranked_tea_id)).order_by(ordering_sql(hits_ranked_tea_id))
            else:
                ranked_AND = [tea.id for tea in raw_teas_AND.all()]
                ranked_OR = [tea.id for tea in raw_teas_OR.all()]
                ranked_tea_id = ranked_AND + [tea_id for tea_id in ranked_OR if tea_id not in ranked_AND]

                raw_teas = Tea.query.filter(Tea.id.in_(ranked_tea_id)).order_by(ordering_sql(ranked_tea_id))
        else:
            raw_teas = raw_teas_AND
        
        total = raw_teas.count()
        teas = raw_teas.offset((page-1)*10).limit(10)

        pagination = Pagination(page=page, total=total, per_page=10, 
                                bs_version=4, record_name="teas")

    return render_template('search.html', name=project_name, netid=net_id, 
                            query=q_flavor, teas=teas, 
                            pagination=pagination,
                            version=request.args.get('version'))

def search_v1():
    raw_query = request.args.get('flavor')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = None
    if not raw_query:
        q_flavor = ""
        teas = []
        output_message = ""
    else:
        q_flavor = ", ".join([flavor.title().strip() for flavor in raw_query.split(",")])
        flavor_query = " OR ".join(["teas.flavors LIKE '%" + flavor.title().strip() + "%'" for flavor in raw_query.split(",")])
        raw_teas = Tea.query.filter(flavor_query).order_by(Tea.ratingValue.desc())
        if HITS_RANK and raw_teas.count() > 0:
            # print "Found {} teas".format(raw_teas.count())
            hits_ranked_tea_id = hits_rank([tea.id for tea in raw_teas.all()])
            # print "Found {} teas after HITS algo".format(len(hits_ranked_tea_id))
            if hits_ranked_tea_id:
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

    return render_template('search_v1.html', name=project_name, netid=net_id, 
                            query=q_flavor, teas=teas, 
                            pagination=pagination,
                            version=request.args.get('version'))

def hits_rank(matchFlavors):

    if not matchFlavors: return []

    import pandas as pd
    reviews = pd.read_csv(os.path.join(APP_ROOT, "data/reviews_top_10k.csv") )
    results = reviews[reviews.id.isin(matchFlavors)]

    import networkx as nx
    G = nx.from_pandas_edgelist(results, 'author_url', 'id', create_using=nx.DiGraph())
    h, a = nx.hits(G, max_iter=10000)
    top_teas = {teaid: a[teaid] for teaid in results.id.unique()}
    return sorted(top_teas, key=top_teas.get, reverse=True)

def ordering_sql(ranked_list):
    # Src: https://stackoverflow.com/questions/29326297/sqlalchemy-filter-by-field-in-list-but-keep-original-order
    from sqlalchemy.sql.expression import case
    ordering = case(
        {id: index for index, id in enumerate(ranked_list)},
        value=Tea.id
    )
    return ordering
