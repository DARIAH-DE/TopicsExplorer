from jinja2 import Template

with open('index.html.jinja') as f:
    tmpl = Template(f.read())

with open('ergebnis.html', 'w') as f:
    f.write(tmpl.render(title = 'Demonstrator', item_list = ["Erster Punkt", "Zweiter Punkt", "Dritter Punkt"]))
