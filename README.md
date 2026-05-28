# MoviWebApp

A Flask web app to manage users and their favorite movies, with data fetched from OMDb.

## Setup

1. Create virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Get a free API key from https://www.omdbapi.com/apikey.aspx

3. Create `.env` file:

```
OMDB_API_KEY=your_key_here
```

4. Run the app:

```bash
python app.py
```

Visit http://127.0.0.1:5000
