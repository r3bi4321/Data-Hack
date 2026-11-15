## 3. Installation & Setup

### Step 1 – Download the application

Download the provided ZIP file and extract it to a folder on your computer.

Alternatively, clone the GitHub repository:

`https://github.com/r3bi4321/Data-Hack`

### Step 2 – Install Python

Install Python 3.13 from [python.org](https://www.python.org/downloads/).

Make sure Python and pip are available in your terminal.

### Step 3 – Install dependencies

Open PowerShell or a terminal in the extracted project folder (the folder containing `app.py`).

Run:

```powershell
python -m pip install -r requirements.txt
```

Wait until the installation is complete.

### Step 4 – Configure the data source

The application requires three CSV files containing match event data for the three periods.

For confidentiality reasons, the original Spengler Cup dataset is not included in the public GitHub repository. Access to the required data must be coordinated separately.

Copy `.env.example` and rename the copy to `.env`.

Open `.env` and enter the paths to the three CSV files:

```env
DATA_PATH_1=path/to/period1.csv
DATA_PATH_2=path/to/period2.csv
DATA_PATH_3=path/to/period3.csv
```

Replace the example paths with the actual locations of the provided CSV files.

## 4. Launching the Application

Once the installation and data configuration are complete, run:

```powershell
streamlit run app.py
```

Streamlit will start a local server and open the application in your default web browser.

If the browser does not open automatically, navigate to:

`http://localhost:8501`

The application runs locally on your computer.

To stop the application, return to the terminal and press `Ctrl + C`.