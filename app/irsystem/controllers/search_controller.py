from . import * 
from app.irsystem.models.tea import Tea
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from flask_paginate import Pagination, get_page_parameter

project_name = "noveltea"
members_name = "Benjamin Stevens, Bowen Gao, Joshua Lee:, Sasha Badov, Yong Lin Ong"
net_id = "bls235, bg453, jhl298, sb965, yo228"

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
		raw_teas = Tea.query.filter(Tea.flavors.like("%" + q_flavor + "%"))
		total = raw_teas.count()
		teas = raw_teas.offset((page-1)*10).limit(10)
		pagination = Pagination(page=page, total=total, per_page=10, bs_version=4, record_name="teas")
		q_flavor = q_flavor.replace("%", ", ")

	return render_template('search.html', name=project_name, netid=net_id, query=q_flavor, teas=teas, pagination=pagination)



