from flask import Flask ,render_template, request,jsonify
from flask_cors import CORS,cross_origin
import agents

app= Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = app.make_default_options_response()
    
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,access-control-allow-origin')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response
    
@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/query-agent/', methods = ['POST'])
def query_agent():
    data = request.get_json()
    user_query = data.get('user_query')

    try:
        json_data = agents.search_jobs(user_query)
        if not json_data['success']:
            return jsonify(json_data), 400
        
        return jsonify(json_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/query-agent-excel/', methods = ['POST'])
def query_agent_excel():
    data = request.get_json()
    user_query = data.get('user_query')

    try:
        url_obj = agents.search_jobs(user_query, isExcel = True)
        if not url_obj['success']:
            return jsonify(url_obj), 400
        
        return jsonify({
            "data": url_obj['url']
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/call-agent/', methods = ['POST'])
def call_agent():
    data = request.get_json()
    ip_addr = str(request.remote_addr)

    # sample_html_text = """
    #     <head>
    #         <title>Sample HTML</title>
    #     </head>
    #     <body>
    #         <h1>Hello, World!</h1>
    #         <p>This is a sample HTML response.</p>
    #     </body>
    # """

    # return jsonify({"success": True, "data": sample_html_text}), 200
    try:
        response_ans = agents.callAgent(data['user_query'], ip_addr)
        return jsonify({
            "success": True,
            "data": response_ans
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug = True, port = 5000, host = '0.0.0.0')
