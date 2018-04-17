#! ../env/bin/python3

import application
import pathlib


class TestWebApplication:
    def setup_method(self):
        """
        Creating a Flask app, and a bokeh resources path for each method of
        the class.
        """
        self.app, self.bokeh_resources = application.config.create_app()
        
        
    def test_config(self):
        """
        Tests if the config loads correctly.
        """
        cwd = pathlib.Path.cwd()
        
        assert self.app.config['DEBUG'] == False
        assert self.app.import_name == 'application.config'
        assert self.app.template_folder == 'templates'
        assert self.app.static_folder == str(pathlib.Path(cwd, 'application', 'static'))
        assert self.bokeh_resources == str(pathlib.Path('application', 'static', 'bokeh_templates'))
    
    
    def test_index(self):
        return None

