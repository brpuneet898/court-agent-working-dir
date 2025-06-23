from flask import Flask, render_template
from utils.graph_module import fetch_documents, compute_similarity_and_visualize_plotly

app = Flask(__name__)

@app.route('/')
def index():
    df = fetch_documents()
    graph_html = compute_similarity_and_visualize_plotly(df, field="Monetary Penalty Imposed", threshold=0.3)
    return render_template('index.html', graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
