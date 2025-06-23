import pandas as pd
from pymongo import MongoClient

def fetch_documents():
    mongo_uri = "mongodb+srv://ns24z459:SEBI_Mongo_123@sebi.hb8ouni.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(mongo_uri)
    db = client['SEBI']
    collection = db['InsiderTrading_1']
    documents = list(collection.find({}))
    return pd.DataFrame(documents)


def compute_similarity_and_visualize_plotly(df, field, threshold=0.5):
    import random
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import LabelEncoder
    import networkx as nx
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.colors
    from sklearn.cluster import KMeans

    values = df[field].fillna("").astype(str)
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(values)

    sil_scores = []
    K_range = range(2, 11)

    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(vectors.toarray())
        score = silhouette_score(vectors.toarray(), cluster_labels, metric='cosine')
        sil_scores.append(score)

    # Convert Silhouette Plot to Plotly
    sil_fig = px.bar(x=list(K_range), y=sil_scores, labels={'x': 'Number of Clusters (k)', 'y': 'Silhouette Score'})
    sil_fig.update_layout(title='Silhouette Scores for k = 2 to 10', template='plotly_white')
    silhouette_plot_html = sil_fig.to_html(full_html=False)

    cosine_sim = cosine_similarity(vectors)

    G = nx.Graph()
    for i in range(len(df)):
        G.add_node(i, label=values[i])

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            if cosine_sim[i][j] >= threshold:
                G.add_edge(i, j, weight=cosine_sim[i][j])

    pos = nx.spring_layout(G, seed=42, k=0.5)

    # --- Detect clusters ---
    clusters = list(nx.connected_components(G))
    cluster_map = {}
    for cluster_id, nodes in enumerate(clusters):
        for node in nodes:
            cluster_map[node] = cluster_id

    # --- Get representative value for each cluster ---
    cluster_labels = {}
    for cluster_id, nodes in enumerate(clusters):
        label_values = [values[node] for node in nodes if values[node].strip()]
        representative_label = max(set(label_values), key=label_values.count) if label_values else f"Unnamed {cluster_id}"
        cluster_labels[cluster_id] = representative_label

    # --- Assign colors ---
    unique_cluster_ids = list(cluster_labels.keys())
    color_palette = plotly.colors.qualitative.Plotly
    random.shuffle(color_palette)
    cluster_colors = {cid: color_palette[i % len(color_palette)] for i, cid in enumerate(unique_cluster_ids)}

    # --- Edge trace ---
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # --- Node trace ---
    node_x, node_y, node_texts, node_colors = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        doc = df.iloc[node]
        hover_text = f"""
        <b>Case ID:</b> {doc.get('_id', '')}<br>
        <b>Date of Order:</b> {doc.get('Date of Order', '')}<br>
        <b>Case Name:</b> {doc.get('Case Name', '')}<br>
        <b>Order Type:</b> {doc.get('Order Type', '')}<br>
        <b>Violation Tag:</b> {doc.get('Type of Insider Trading', '')}<br>
        <b>Penalty Amount:</b> ₹{doc.get('Monetary Penalty Imposed', '')}<br>
        <b>Filename:</b> {doc.get('filename', '')}
        """
        node_texts.append(hover_text)

        cluster_id = cluster_map.get(node, 0)
        node_colors.append(cluster_colors[cluster_id])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hovertext=node_texts,
        hoverinfo='text',
        marker=dict(
            showscale=False,
            size=10,
            color=node_colors,
            line_width=1
        )
    )

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    legend_traces = []
    for cid in unique_cluster_ids:
        label = cluster_labels[cid]
        size = sum(1 for v in cluster_map.values() if v == cid)
        legend_traces.append(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=cluster_colors[cid]),
            legendgroup=label,
            showlegend=True,
            name=f"{label} ({size} nodes)"
        ))

    fig = go.Figure(data=[edge_trace, node_trace] + legend_traces,
                    layout=go.Layout(
                        title=f'Similarity Network for "{field}" (Threshold: {threshold})',
                        showlegend=True,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(title='UMAP-Dim 1', showgrid=False, zeroline=False),
                        yaxis=dict(title='UMAP-Dim 2', showgrid=False, zeroline=False)
                    ))

    try:
        labels = df[field].fillna("").astype(str).tolist()
        label_encoder = LabelEncoder()
        encoded_labels = label_encoder.fit_transform(labels)
        sil_score = silhouette_score(vectors.toarray(), encoded_labels, metric='cosine')
        silhouette_score_text = f"Silhouette Score (label-based): {sil_score:.4f}"
    except ValueError as e:
        silhouette_score_text = f"Silhouette Score could not be computed: {e}"

    cluster_summary_html = "<h3>Cluster Summary</h3><ul>"
    for cluster_id, nodes in enumerate(clusters):
        label = cluster_labels[cluster_id]
        count = len(nodes)
        cluster_summary_html += f"<li><b>Cluster {cluster_id}:</b> Label = '{label}', Size = {count}</li>"
    cluster_summary_html += "</ul>"

    return fig.to_html(full_html=False), silhouette_plot_html, silhouette_score_text, cluster_summary_html
