import logging, os, datetime, subprocess
from flask import Flask, render_template, request, redirect, send_from_directory

app = Flask(__name__)

# setup logging
logging.basicConfig(filename='boxmaker.log',level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("---------------------------------------------------------------------------")

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BOX_TMP_DIR = os.path.join( BASE_DIR, 'tmp', 'boxes')

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/box/create", methods=['POST'])
def create_box():
    validation_errors = _validate_box_params()
    if len(validation_errors)>0:
        error_str = ' '.join(validation_errors)
        logger.warn("Errors: "+error_str)
        return render_template('home.html', error=error_str)
    else:
        box_name = _box_name()
        logger.info('Creating box '+box_name+"...")
        # convert it to millimeters
        measurements = ['width','height','depth','material_thickness','cut_width','notch_length']
        conversion = 1
        if request.form['units']=='in':
            conversion = 25.4
        elif request.form['units']=='cm':
            conversion = 10
        details = [str(float(request.form[m])*conversion) for m in measurements]
        # and add bounding box option
        if 'bounding_box' in request.form:
            details.append( 'true' )
        else:
            details.append( 'false' )
        # now render it
        _render_box(box_name, details)
        return send_from_directory(BOX_TMP_DIR,box_name,as_attachment=True)

def _render_box(file_name, params):
    boxmaker_jar_file = "BOX-v.1.6.1.jar"
    pdf_file_path = os.path.join(BOX_TMP_DIR,file_name) 
    #command = "java -cp "+boxmaker_jar_file+" com.rahulbotics.boxmaker.CommandLine "
    #command+= pdf_file_path
    #command+= " 101.6 127 152.4 4.7625 0 11.90625 false"
    args = [ 'java', '-cp', boxmaker_jar_file, 'com.rahulbotics.boxmaker.CommandLine', pdf_file_path ] + params
    logger.info(args)
    subprocess.call(args)

def _box_name():
    return 'box-'+datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")+'.pdf'

def _validate_box_params():
    errors = []
    errors+= _numeric_errors(request.form['width'],'Width')
    errors+= _numeric_errors(request.form['depth'],'Depth')
    errors+= _numeric_errors(request.form['height'],'Height')
    errors+= _numeric_errors(request.form['material_thickness'],'Material thickness')
    errors+= _numeric_errors(request.form['notch_length'],'Notch length')
    errors+= _numeric_errors(request.form['cut_width'],'Cut width')
    return errors

def _numeric_errors(str, name):
    try:
        float(str)
        return []
    except ValueError:
        return [ name + " must be a number!"]

def _create_box_design():
    '''
    Helper function to render an actual box using the java library
    '''
    return True

if __name__ == "__main__":
    app.debug = True
    app.run()
