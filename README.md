# Web Application Structure

This web application is built using **Streamlit** and provides a range of features including user authentication, multiple pages and so on.

## Project Structure

```
WebApp (Root Directory)
├── code/                          # Main Application Logic Folder (CWD for Streamlit Cloud)
│   ├── main.py                    # Main file that manages routing
│   ├── home.py                    # Home page
│   ├── login.py                   # Login handling
│   ├── computations.py            # ML Model predictions and KPI logic
│   ├── pages/                     # Dashboard pages
│   │   ├── airbnb_page.py         # Primary price predictor
│   │   ├── renting_page.py        # Rent prediction
│   │   ├── comparison.py          # Strategy comparison
│   │   └── profile.py             # User profile updates
│   ├── data/                      # CRITICAL DATA (Accessed via path: 'code/data/___')
│   │   ├── profiles.json          # User profiles and login data
│   │   └── users.json             # User authentication data
│   │   └── paris.geojson          # GeoJSON data for map visualization
│   ├── ml_models/                 # Machine Learning Models (.sav files)
│   └── .streamlit/                # Streamlit configuration for dark theme
├── images/                        # Application assets
└── requirements.txt               # Project dependencies
```


## Setup Instructions

### 1. Install Dependencies

Install the required Python packages by running:

```bash
pip install streamlit
pip install streamlit-login-auth-ui
```

### 2. Run the Application

After installing the dependencies, you can run the web application by executing in the console (you have to be in right folder - in code folder):

```
streamlit run main.py
```

This will start the Streamlit server and open the web application in your default browser

---

## Application Features

### 1. User Authentication
- **Login and Sign-up**: Users can log in or sign up to access the app.
- **Profile Management**: Users can manage their profile information, including their email, password, and all the airbnb and renting related dataa

### 2. Pages
Multiple pages: renting, airbnb, profile,

- Airbnb: user can play around with values and find out potential income and so on

- Renting: user can play around with values and find out the right renting price

- Comparison: user can play around with values and clearly see which options is best, airbnb listing or renting


### 3. Data Storage

- Profile Data: User profile information containing also login relevant sutff (e.g., size, location, bathrooms, bedrooms, etc) is stored in `profiles.json`.

---

## Configuration

You can modify the app's configuration in the `.streamlit/config.toml` file. For example, you can adjust Streamlit's settings like the theme, i have chosen a dark one with redish tones
---
