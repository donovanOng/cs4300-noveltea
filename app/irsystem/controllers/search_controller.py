from . import * 
from app.irsystem.models.tea import Tea
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "noveltea"
members_name = "Benjamin Stevens, Bowen Gao, Joshua Lee:, Sasha Badov, Yong Lin Ong"
net_id = "bls235, bg453, jhl298, sb965, yo228"

@irsystem.route('/', methods=['GET'])
def search():
	q_flavor = request.args.get('flavor')
	if not q_flavor:
		data = []
		output_message = ''
	else:
		data = Tea.query.filter(Tea.flavors.like("%" + q_flavor.title() + "%")).limit(10).all()
		print data[0]
	return render_template('search.html', name=project_name, netid=net_id, query=q_flavor, data=data)



