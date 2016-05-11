Box Designer Web App
====================

A simple web front-end to the box designer command line tool for making designs you can laser-cut.

Dependencies
------------

```
pip install reportlab
pip install flask
```

Installation
------------

2. Make the `tmp` directory writable by your web user

Running
-------

Just run `python server.py` and then try it at http://localhost:5000 in your web browser.

If you want to render a box in code, see the `test-render.py` example.

License
-------

This software is released under the [http://www.gnu.org/licenses/agpl.html](GNU Affero General Public License).
