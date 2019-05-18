Box Designer Web App
====================

A simple web front-end to the box designer command line tool for making designs you can laser-cut.

Dependencies
------------

```
pip install -r requirements.txt
```

Installation
------------

Make the `tmp` directory writable by your web user

Running
-------

Just run `python server.py` and then try it at http://localhost:5000 in your web browser.

If you want to render a box in code, see the `test-render.py` example.

License
-------

This software is released under the [GNU Affero General Public License](http://www.gnu.org/licenses/agpl.html).

Deploying
---------

This is built to be deployed easily to a containerized host (ie. Heroku-style).

Optional environment variables:
* MATOMO_TRACKER_URL - if you want to use Matomo analytics, fill this in
* MATOMO_SITE_ID - if you want to use Matomo analytics, fill this in

Contributors
------------

Box Designer started as a piece of Java desktop software in April of 2001 while Rahul Bhargava was a student at the MIT Media Lab. Since thenn, as it evolved into a Rails web app, and then a Python web app, others have contributed important pieces:

* @wildsparx on GitHub contributed the DXF output
* @vincentadam87 on GitHub contributed the "no top" option
* eolson [at] mit [dot] edu contributed the original notch length and kerf options
* @kentquirk on GitHub contributed SVG output and made the system generate closed curves in PDF and SVG
