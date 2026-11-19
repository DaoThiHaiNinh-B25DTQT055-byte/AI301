"""
Streamlit Community Cloud Entrypoint Alias.
Forwards execution directly to app.py.
"""
import os
import runpy

app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
runpy.run_path(app_path, run_name="__main__")
