from flask import Flask, render_template, request, send_file, after_this_request
import os
from utils.graph_module import fetch_documents, compute_similarity_and_visualize_plotly

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    df = fetch_documents()

    # Default values
    selected_field = "Monetary Penalty Imposed"
    threshold = 0.3

    if request.method == 'POST':
        selected_field = request.form.get('field')
        threshold = float(request.form.get('threshold'))

    graph_html, silhouette_plot_html, sil_score_text, cluster_summary_html, optimal_k = compute_similarity_and_visualize_plotly(
        df, field=selected_field, threshold=threshold)

    return render_template('index.html',
                           graph_html=graph_html,
                           silhouette_plot_html=silhouette_plot_html,
                           sil_score_text=sil_score_text,
                           cluster_summary_html=cluster_summary_html,
                           selected_field=selected_field,
                           threshold=threshold,
                           optimal_k=optimal_k)

@app.route('/download-csv')
def download_csv():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'sample_insider_trading_data.csv')
    if os.path.exists(csv_path):
        @after_this_request
        def remove_file(response):
            try:
                os.remove(csv_path)
            except Exception as e:
                app.logger.error(f"Error deleting file: {e}")
            return response
        return send_file(csv_path, as_attachment=True)
    else:
        return "File not found or already downloaded.", 404

if __name__ == '__main__':
    app.run(debug=True)
