from flask import Flask, request, render_template, jsonify
from spark_model import run_forecast
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'dataset'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            forecast_result, future_df = run_forecast(filepath)
            # Return JSON for JS to render table + charts
            return jsonify({'forecast': forecast_result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
