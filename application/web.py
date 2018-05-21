import application
import flask
import shutil
import tempfile
import pathlib
import werkzeug.exceptions


app, dumpdir, archivedir = application.config.create_app()

@app.route('/')
def index():
    """
    Renders the main page, and unlinks the content (if any) in the temporary
    folders. A warning pops up, if the machine is not connected to the internet.
    """
    application.utils.unlink_content(dumpdir)
    application.utils.unlink_content(archivedir)

    if application.utils.is_connected():
        return flask.render_template('index.html')
    else:
        return flask.render_template('index.html', internet='warning')


@app.route('/help')
def help():
    """
    Renders the help page.
    """
    return flask.render_template('help.html')


@app.route('/modeling', methods=['POST'])
def modeling():
    """
    Streams the modeling page, printing useful information to the UI.
    The generated data will be dumped into a tempdir (specified above).
    """
    def stream_template(template_name, **context):
        app.update_template_context(context)
        t = app.jinja_env.get_template(template_name)
        return t.stream(context)
    stream = flask.stream_with_context(application.modeling.workflow(dumpdir, archivedir))
    return flask.Response(stream_template('modeling.html', info=stream))


@app.route('/model')
def model():
    """
    Loads the dumped data, deletes the temporary data, and renders the model page.
    """
    data = application.utils.load_data(dumpdir)
    return flask.render_template('model.html', **data)


@app.route('/download')
def download():
    """
    Sends the ZIP archive.
    """
    return flask.send_file(str(pathlib.Path(archivedir, 'topicmodeling.zip')))


@app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_http_exception(e):
    """
    Handles any HTTP Exception, shows a Bootstrap modal with the error
    message and renders the index.html again.
    """
    return flask.render_template('index.html', http='error', error_message=e)

for code in werkzeug.exceptions.default_exceptions:
    app.errorhandler(code)(handle_http_exception)


@app.after_request
def add_header(r):
    """
    Clears the cache after a request.
    """
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
