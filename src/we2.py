from fastapi import FastAPI
from nicegui import app as nicegui_app, ui

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


# Register a page with a custom path
@ui.page('/show')
def show():
    # Your UI code goes here
    ui.label('Hello, FastAPI!')
    # Some bindings
    ui.dark_mode().bind_value(nicegui_app.storage.user, 'dark_mode')
    ui.checkbox('dark mode').bind_value(nicegui_app.storage.user, 'dark_mode')


# Integrate with your FastAPI Application
ui.run_with(
    app=app,
    storage_secret='pick your private secret here',
)