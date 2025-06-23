# Similarity Network on SEBI Orders

This web application visualizes the similarity network of SEBI (Securities and Exchange Board of India) Insider Trading orders using interactive network graphs and clustering metrics. Users can explore document similarities based on various fields and adjust the similarity threshold to see how clusters form.

## Features

- **Interactive Network Graph:** Visualizes document similarity as a network using Plotly.
- **Customizable Field & Threshold:** Select which field to compare (e.g., "Monetary Penalty Imposed", "Order Type") and set the similarity threshold.
- **Silhouette Score & Plot:** Displays clustering quality metrics and silhouette scores for different cluster counts.
- **Cluster Summary:** Shows representative labels and sizes for each detected cluster.
- **MongoDB Integration:** Fetches SEBI order data directly from a MongoDB Atlas database.

## Requirements

- Python 3.8+
- MongoDB Atlas account (with access to the SEBI dataset)
- The following Python packages:
  - Flask
  - pandas
  - pymongo
  - scikit-learn
  - networkx
  - plotly

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repo-url>
   cd court-agent-working-dir/similarity_network
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *(Create `requirements.txt` if missing, with the packages listed above.)*

3. **Configure MongoDB:**
   - The MongoDB URI is set in `utils/graph_module.py`. Update it if you have different credentials or database details.

## Usage

1. **Run the Flask app:**

   ```bash
   python app.py
   ```

2. **Open your browser:**
   - Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

3. **Interact:**
   - Select the field and similarity threshold.
   - View the network graph, silhouette plot, and cluster summary.

## Project Structure

```text
similarity_network/
│
├── app.py                      # Flask application entry point
├── utils/
│   └── graph_module.py         # Data fetching, similarity, and visualization logic
├── templates/
│   └── index.html              # Main HTML template
├── static/
│   └── style.css               # (Optional) Custom styles
└── README.md                   # This file
```

## Notes

- The application requires access to the SEBI Insider Trading dataset in MongoDB.
- For production use, set `debug=False` in `app.py`.
- For any issues or feature requests, please open an issue in the repository.

---
