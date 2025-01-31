from flask import Flask, request
from flask import render_template
import settings
import utils
import numpy as np
import cv2
import predictions as pred

app = Flask(__name__)
app.secret_key = 'document_scanner_app'

docscan = utils.DocumentScan()


@app.route('/', methods=['GET', 'POST'])
def scandoc():

    if request.method == 'POST':
        file = request.files['image_name']
        upload_image_path = utils.save_upload_image(file)
        print('Image saved in = ', upload_image_path)
        # predict the coordinates of the document
        four_points, size = docscan.document_scanner(upload_image_path)
        print(four_points, size)
        if four_points is None:
            message = 'UNABME TO LOCATE THE CO-ORDINATES: points displayed are random'
            points = [
                {'x': 10, 'y': 10},
                {'x': 120, 'y': 10},
                {'x': 120, 'y': 120},
                {'x': 10, 'y': 120},
            ]
            return render_template('scanner.html',
                                   points=points,
                                   fileupload=True,
                                   message=message)
        else:
            points = utils.array_to_json_format(four_points)
            message = 'Located the coordinates of document'
            return render_template('scanner.html',
                                   points=points,
                                   fileupload=True,
                                   message=message)

        return render_template('scanner.html')

    return render_template('scanner.html')


@app.route('/transform', methods=['POST'])
def transform():
    try:
        points = request.json['data']
        array = np.array(points)
        magic_color = docscan.calibrate_to_original_size(array)
        # utils.save_image(magic_color, 'magic_color.jpg')
        filename = 'magic_color.jpg'
        magic_image_path = settings.join_path(settings.MEDIA_DIR, filename)
        cv2.imwrite(magic_image_path, magic_color)

        return 'success'
    except:
        return 'fail'


@app.route('/prediction')
def prediction():
    # load the wrap image
    wrap_image_filepath = settings.join_path(
        settings.MEDIA_DIR, 'magic_color.jpg')
    image = cv2.imread(wrap_image_filepath)
    image_bb, results = pred.getPredictions(image)

    bb_filename = settings.join_path(settings.MEDIA_DIR, 'bounding_box.jpg')
    cv2.imwrite(bb_filename, image_bb)

    return render_template('predictions.html', results=results)


@app.route('/about')
def about():
    return render_template('about.html')

def clean_value(value):
    if isinstance(value, list):
        return ', '.join(value).replace('[', '').replace(']', '').replace("'", "")
    return value

# Add the custom filter to your Jinja2 environment
app.jinja_env.filters['clean_value'] = clean_value

if __name__ == "__main__":
    app.run(debug=True)
