from . import * 
# from app.irsystem.models.matrix import Matrix
# from app.irsystem.models.redisconn import RedisConn as RedisConn 
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "HotTea"
net_id = "Benjamin Stevens: bls235, Bowen Gao: bg453, Joshua Lee: jhl298, Sasha Badov: sb965, Yong Lin Ong: yo228"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



