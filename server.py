import logging.handlers, os, datetime
from flask import Flask, render_template, request, send_from_directory
import boxmaker

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOX_TMP_DIR = os.path.join(BASE_DIR, 'tmp', 'boxes')

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        validation_errors = _validate_box_params()
        if len(validation_errors) > 0:
            error_str = ' '.join(validation_errors)
            logger.debug("Errors: "+error_str)
            return render_template('home.html', error=error_str)
        else:
            file_type = request.form['file_type']
            notched_top = request.form['notched_top'] == '1'
            box_name = _box_name(file_type)
            logger.debug('Creating box '+box_name+"...")
            # convert it to millimeters
            measurements = ['width', 'height', 'depth', 'material_thickness', 'cut_width', 'notch_length']
            conversion = 1.0
            if request.form['units'] == 'in':
                conversion = 25.4
            elif request.form['units'] == 'cm':
                conversion = 10.0
            params = {}
            for key in measurements:
                params[key] = float(request.form[key])*conversion
            # and add bounding box option
            params['bounding_box'] = True if 'bounding_box' in request.form else False
            # now render it
            logger.info(request.remote_addr + " - " + box_name)
            _render_box(box_name, file_type, params, notched_top)
            return send_from_directory(BOX_TMP_DIR, box_name, as_attachment=True)
    else:
        return render_template("home.html", boxmaker_version=boxmaker.APP_VERSION)


def _render_box(file_name, file_type, params, notched_top):
    out_file_path = os.path.join(BOX_TMP_DIR, file_name)
    boxmaker.render(out_file_path,
                    params['width'], params['height'], params['depth'],
                    params['material_thickness'], params['cut_width'], params['notch_length'],
                    params['bounding_box'], file_type, not notched_top
                    )


def _box_name(file_type):
    return 'box-'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")+'.'+file_type


def _validate_box_params():
    errors = []
    errors += _numeric_errors(request.form['width'], 'Width')
    errors += _numeric_errors(request.form['height'], 'Height')
    errors += _numeric_errors(request.form['depth'], 'Depth')
    errors += _numeric_errors(request.form['material_thickness'], 'Material thickness')
    errors += _numeric_errors(request.form['cut_width'], 'Cut width')
    errors += _numeric_errors(request.form['notch_length'], 'Notch length')
    return errors


def _numeric_errors(string, name):
    try:
        float(string)
        return []
    except ValueError:
        return [name + " must be a number!"]

if __name__ == "__main__":
    app.debug = False
    app.run()
