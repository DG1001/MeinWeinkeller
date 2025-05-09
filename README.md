# Mein Weinkeller - Wine Cellar Management App

"Mein Weinkeller" is a web application built with Flask to help you manage your personal wine collection. You can add new wines, edit existing entries, search your collection, and upload images for your wines.

## Features

*   **Wine Management:** Add, view, edit, and delete wines from your collection.
*   **Detailed Information:** Store details like name, vintage, winery, grape variety, region, storage location, drinking temperature, purchase date, price, stock, and personal notes.
*   **Image Uploads:** Upload multiple images for each wine and delete them if needed.
*   **Search Functionality:** Search your wine collection by keyword, grape variety, winery, or vintage.
*   **Responsive Design:** User interface designed with Bootstrap for usability on various devices.
*   **Subtle Background:** A pleasant background image enhances the visual experience.

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    It's assumed you have Flask and Werkzeug. If you have a `requirements.txt` file, you would run:
    ```bash
    pip install -r requirements.txt 
    ```
    If not, install Flask and other dependencies manually:
    ```bash
    pip install Flask Werkzeug openai
    ```

4.  **Set up OpenAI API Key:**
    This application uses OpenAI's API for generating wine descriptions. You need to have an OpenAI API key.
    Set it as an environment variable:
    ```bash
    export OPENAI_API_KEY='your_openai_api_key_here'
    ```
    On Windows, use `set OPENAI_API_KEY=your_openai_api_key_here` in Command Prompt or `$env:OPENAI_API_KEY='your_openai_api_key_here'` in PowerShell.
    If the API key is not set, the AI features will be disabled.

5.  **Initialize the database:**
    This will create the `weinkeller.db` SQLite database file and populate it with the schema and any initial sample data.
    ```bash
    python init_db.py
    ```

6.  **Create the upload directory:**
    The application saves uploaded images to `static/uploads/`.
    ```bash
    mkdir -p static/uploads
    ```
    (The application also attempts to create this directory if it doesn't exist when an image is uploaded.)

## Usage

1.  **Run the Flask application:**
    ```bash
    python app.py
    ```

2.  **Open your web browser** and navigate to:
    `http://localhost:5000` or `http://0.0.0.0:5000`

    You should see the main page of the "Mein Weinkeller" application. From there, you can:
    *   View your wine collection.
    *   Add new wines using the "Neuer Wein" link.
    *   Click on a wine to see its details.
    *   Edit or delete wines from their detail page.
    *   Use the "Erweiterte Suche" for more specific filtering.

## Database

The application uses an SQLite database named `weinkeller.db`. The schema is defined in `schema.sql`.
The `init_db.py` script is used to create and initialize this database.

## Technologies Used

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, Bootstrap 5
*   **Database:** SQLite
*   **Image Handling:** Werkzeug for secure filenames

---

Feel free to contribute or suggest improvements!
