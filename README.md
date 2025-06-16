# Court Agent Working Directory

This project provides tools and scripts for working with court-related data in JSON format.

## Setup Guide

### 1. Clone the Repository

```sh
git clone <repository-url>
cd court-agent-working-dir
```

### 2. Create and Activate Conda Environment

```sh
conda create -n court-agent-env python=3.10
conda activate court-agent-env
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Load the Sample JSON

To load and inspect the sample JSON file:

```python
import json

with open('sample.json', 'r') as f:
    data = json.load(f)
print(data)
```

Replace `'sample.json'` with your actual sample file name if different.

---

For more details, see the code comments and individual