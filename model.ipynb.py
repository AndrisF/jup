import os
import keras
import tensorflow as tf
from keras.applications import inception_v3 as inc_net
from keras.preprocessing import image
from keras.applications.imagenet_utils import decode_predictions
from skimage.io import imread
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps
from lime import lime_image 
from skimage.segmentation import mark_boundaries
from flask import Flask, request, render_template, jsonify
print('Notebook run using keras:', keras.__version__)

model = tf.keras.models.load_model('keras_model.h5')

app = Flask(__name__)

def preprocess_image(ip):
	# swap color channels, preprocess the image, and add in a batch
	# dimension
	image = Image.open(ip).convert("RGB")
	data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
	size = (224, 224)
	image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
	image_array = np.asarray(image)
	normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
	data[0] = normalized_image_array
	return data
 
def predict_image_class(image_path):
    # Preprocess the image
    prediction = model.predict(preprocess_image(image_path))
    index = np.argmax(prediction)
    print(str(index))
    confidence_score = prediction[0][index]
    print(str(confidence_score))
    return confidence_score

images = preprocess_image('su2.jpg')
# I'm dividing by 2 and adding 0.5 because of how this Inception represents images
plt.imshow(images[0] / 2 + 0.5)

predict_image_class("su2.jpg")
####
explainer = lime_image.LimeImageExplainer()
explanation = explainer.explain_instance(images[0].astype('double'), model.predict, top_labels=1, hide_color=0, num_samples=1000)
temp, mask = explanation.get_image_and_mask(explanation.top_labels[0], positive_only=True, num_features=5, hide_rest=True)
plt.imshow(mark_boundaries(temp / 2 + 0.5, mask))
plt.savefig("test.jpg")

## positive and negative 
temp, mask = explanation.get_image_and_mask(explanation.top_labels[0], positive_only=False, num_features=10, hide_rest=False)
plt.imshow(mark_boundaries(temp / 2 + 0.5, mask))

#ind =  explanation.top_labels[0]
#dict_heatmap = dict(explanation.local_exp[ind])
#heatmap = np.vectorize(dict_heatmap.get)(explanation.segments) 

#Plot. The visualization makes more sense if a symmetrical colorbar is used.
#plt.imshow(heatmap, cmap = 'RdBu', vmin  = -heatmap.max(), vmax = heatmap.max())

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'})

    # Save the uploaded file
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Call your Python code here using the uploaded file_path
    # For example, you can use a subprocess to run your Python script

    return jsonify({'message': 'File uploaded successfully'})