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
    elif version == "2":
        return search_v2()
    else:
        return search()

@irsystem.route('getRelatedTeas/', methods=['GET'])
def getRelatedTeas():
    tea_id = request.args.get('tea_id')
    print tea_id
    related_tea_ids = query_tea_with_same_label(int(tea_id), 5)
    print related_tea_ids
    res = Tea.query.filter(Tea.id.in_(related_tea_ids)).order_by(ordering_sql(related_tea_ids)).all()
    return jsonify([r.to_json() for r in res])

def search():
    q_flavor_raw = request.args.get('flavor')
    f_teaType = request.args.get('notTeaTypes', "")
    f_caffeine = request.args.get('notCaffeines', "")
    page = request.args.get(get_page_parameter(), type=int, default=1)

    pagination = None

    # Formatted search query
    q_flavor = ""
    # List of teas
    results = []
    # Filters
    tea_types, caffeines = [], []

    if q_flavor_raw:
        q_flavor = ", ".join([flavor.title().strip() for flavor in q_flavor_raw.split(",")])

        flavor_OR_query = " OR ".join(["teas.flavors LIKE '%" + flavor.title().strip() + "%'" for flavor in q_flavor_raw.split(",")])
        raw_teas_OR = Tea.query.filter(flavor_OR_query).order_by(Tea.ratingValue.desc())

        if raw_teas_OR.count() > 0:   
            
            q_flavor_title = [flavor.title().strip() for flavor in q_flavor_raw.split(",")]
            tea_ids_matched = []
            for num_match in reversed(range(1, len(q_flavor_title)+1)):
                tea_ids = []
                for tea in raw_teas_OR.all():
                    flavor_matches = sum([1 for flavor in tea.flavors.split(",") if flavor.strip() in q_flavor_title])
                    if num_match == flavor_matches:
                        tea_ids.append(tea.id)
                tea_ids_matched.append(tea_ids)

            if HITS_RANK:
                hits_ranked_tea_id = []
                for tea_ids in tea_ids_matched:
                    hits_ranked_teas = hits_rank(tea_ids)
                    hits_ranked_tea_id.extend(hits_ranked_teas)
                raw_teas = Tea.query.filter(Tea.id.in_(hits_ranked_tea_id)).order_by(ordering_sql(hits_ranked_tea_id))

            else:
                ranked_tea_id = []
                for tea_ids in tea_ids_matched:
                    ranked_tea_id.extend(tea_ids)
                raw_teas = Tea.query.filter(Tea.id.in_(ranked_tea_id)).order_by(ordering_sql(ranked_tea_id))
        else:
            raw_teas = raw_teas_OR

        # Filters 
        tea_types = [tea.teaType for tea in raw_teas.all()] if raw_teas.all() else []
        tea_types = sorted(list(set(tea_types)))
        tea_types = [(teaType, teaType in f_teaType.split(",")) for teaType in tea_types]

        caffeines = [tea.caffeine for tea in raw_teas.all()] if raw_teas.all() else []
        caffeines = sorted(list(set(caffeines)))
        caffeines = [(caffeine, caffeine in f_caffeine.split(",")) for caffeine in caffeines]

        if f_teaType:
            raw_teas = raw_teas.filter(~Tea.teaType.in_(f_teaType.split(",")))
        if f_caffeine:
            raw_teas = raw_teas.filter(~Tea.caffeine.in_(f_caffeine.split(",")))

        total = raw_teas.count()
        teas = raw_teas.offset((page-1)*10).limit(10)

        results = []
        for tea in teas:
            matched_flavors = ""
            marked_flavors = ""
            for flavor in tea.flavors.split(','):
                if flavor.strip() in q_flavor_title:
                    matched_flavors += "<span class=\"marked\">" + flavor.strip() + "</span> "
                else:
                    marked_flavors += flavor + ", "
            tea.marked_flavors = matched_flavors + marked_flavors[:-2]
            results.append(tea)

            
        pagination = Pagination(page=page, total=total, per_page=10, 
                                bs_version=4, record_name="teas")

    return render_template('search.html', name=project_name, netid=net_id, 
                            query=q_flavor, teas=results, 
                            pagination=pagination, page=(page-1)*10, 
                            multi_query=len(q_flavor.split(','))>1,
                            version=request.args.get('version'),
                            tea_types=tea_types, caffeines=caffeines,
                            f_teaType=f_teaType, f_caffeine=f_caffeine)

def search_v2():
    q_flavor_raw = request.args.get('flavor')
    f_teaType = request.args.get('notTeaTypes', "")
    f_caffeine = request.args.get('notCaffeines', "")
    page = request.args.get(get_page_parameter(), type=int, default=1)

    pagination = None

    if not q_flavor_raw:
        q_flavor = ""
        teas = []
        output_message = ""
        tea_types = []
        caffeines = []
    else:
        q_flavor = ", ".join([flavor.title().strip() for flavor in q_flavor_raw.split(",")])

        flavors_AND_query = " AND ".join(["teas.flavors LIKE '%" + flavor.title().strip() + "%'" for flavor in q_flavor_raw.split(",")])
        raw_teas_AND = Tea.query.filter(flavors_AND_query).order_by(Tea.ratingValue.desc())

        flavor_OR_query = " OR ".join(["teas.flavors LIKE '%" + flavor.title().strip() + "%'" for flavor in q_flavor_raw.split(",")])
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

        # Filters 
        tea_types = [tea.teaType for tea in raw_teas.all()] if raw_teas.all() else []
        tea_types = sorted(list(set(tea_types)))
        tea_types = [(teaType, teaType in f_teaType.split(",")) for teaType in tea_types]

        caffeines = [tea.caffeine for tea in raw_teas.all()] if raw_teas.all() else []
        caffeines = sorted(list(set(caffeines)))
        caffeines = [(caffeine, caffeine in f_caffeine.split(",")) for caffeine in caffeines]

        if f_teaType:
            raw_teas = raw_teas.filter(~Tea.teaType.in_(f_teaType.split(",")))
        if f_caffeine:
            raw_teas = raw_teas.filter(~Tea.caffeine.in_(f_caffeine.split(",")))

        total = raw_teas.count()
        teas = raw_teas.offset((page-1)*10).limit(10)
            
        pagination = Pagination(page=page, total=total, per_page=10, 
                                bs_version=4, record_name="teas")

    return render_template('search_v2.html', name=project_name, netid=net_id, 
                            query=q_flavor, teas=teas, 
                            pagination=pagination,
                            version=request.args.get('version'),
                            tea_types=tea_types, caffeines=caffeines,
                            f_teaType=f_teaType, f_caffeine=f_caffeine)

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

def query_tea_with_same_label(q_id, top_n):
    '''
    This function takes a query of tea Id 
    and return a list of (id, recommendation_score) pairs sorted by 
    recommendation scores
    
    params:
    q_id: integer, the id of the tea which you want to find teas similar with
    top_n: integer, return top n results
    
    return:
    list: a list of (id, recommendation_score) pairs which has the same label as q_id 
            and sorted by their recommendation score
    '''
    import pandas as pd
    id_label_df = pd.read_csv(os.path.join(APP_ROOT, "data/clusters.csv") )

    q_label = int(id_label_df.label[id_label_df.id == q_id])
    tmp_df = id_label_df[['id','recommendation']][id_label_df.label == q_label].\
        sort_values('recommendation', ascending = False)

    # return list(zip(tmp_df['id'].values[:top_n], tmp_df['recommendation'].values[:top_n]))
    return list(tmp_df['id'].values[:top_n])

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
