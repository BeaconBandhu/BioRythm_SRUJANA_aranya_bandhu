from flask import Flask, request, jsonify, render_template_string
import openai
import base64

# --- Configure your OpenAI API Key ---
client = openai.OpenAI(api_key="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")

# --- Flask App Setup ---
app = Flask(__name__)

# --- In-memory cart storage ---
CART = []

# --- HTML Template (Embedded in Python) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prescription and Patient Support</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; margin: 0; }
        .container { background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; width: 90%; max-width: 500px; }
        h1 { color: #333; margin-bottom: 20px; }
        .upload-area { border: 2px dashed #ccc; border-radius: 8px; padding: 20px; cursor: pointer; transition: border-color 0.3s ease; }
        .upload-area:hover { border-color: #007bff; }
        #image-preview { max-width: 100%; height: auto; margin-top: 20px; border-radius: 8px; display: none; max-height: 300px; object-fit: contain; }
        #upload-text { color: #888; }
        .btn { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-top: 20px; font-size: 16px; }
        .btn:hover { background-color: #0056b3; }
        #upload-input { display: none; }
        #output-area { margin-top: 20px; padding: 15px; background-color: #e9ecef; border-radius: 8px; text-align: left; word-wrap: break-word; white-space: pre-wrap; }
        #cart-area { margin-top: 20px; padding: 15px; background-color: #d4edda; border-radius: 8px; text-align: center; font-weight: bold; color: #155724; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Prescription and Patient Support</h1>
        <div class="upload-area" onclick="document.getElementById('upload-input').click();">
            <p id="upload-text">Drag & drop your image here or click to browse</p>
            <input type="file" id="upload-input" accept="image/*">
            <img id="image-preview" src="#" alt="Image Preview">
        </div>
        <button class="btn" onclick="processImage()">Process Image</button>
        <button class="btn" onclick="addToCart()">Add to Cart</button>
        <div id="output-area">
            <p>Extracted Text will appear here...</p>
        </div>
        <div id="cart-area">
            Total Items in Cart: <span id="cart-count">0</span>
        </div>
    </div>

    <script>
        const uploadInput = document.getElementById('upload-input');
        const imagePreview = document.getElementById('image-preview');
        const uploadText = document.getElementById('upload-text');
        const outputArea = document.getElementById('output-area');
        const cartCount = document.getElementById('cart-count');

        let extractedText = "";

        uploadInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    uploadText.style.display = 'none';
                }
                reader.readAsDataURL(file);
            }
        });

        async function processImage() {
            const file = uploadInput.files[0];
            if (!file) {
                alert('Please select an image first.');
                return;
            }

            const formData = new FormData();
            formData.append('image', file);
            
            outputArea.innerText = 'Processing... Please wait.';

            try {
                const response = await fetch('/scan', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();

                if (response.ok) {
                    extractedText = result.text;
                    outputArea.innerText = result.text;
                } else {
                    outputArea.innerText = 'Error: ' + result.error;
                }
            } catch (error) {
                outputArea.innerText = 'An error occurred. Check server logs.';
                console.error('Fetch error:', error);
            }
        }

        async function addToCart() {
            if (!extractedText) {
                alert("Process a prescription first before adding to cart.");
                return;
            }

            try {
                const response = await fetch('/cart', {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: extractedText })
                });

                const result = await response.json();
                if (response.ok) {
                    cartCount.innerText = result.total_items;
                } else {
                    alert("Error: " + result.error);
                }
            } catch (error) {
                console.error("Error adding to cart:", error);
            }
        }
    </script>
</body>
</html>
"""

### **Flask Routes**

@app.route('/')
def index():
    """Serves the main webpage with the image upload form."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan_image():
    """Extract text from prescription image."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']

    try:
        # Encode the image
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please read the handwritten prescription in this image and extract the medicines only and how many tablets needed , separated by commas.no extra texts please"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            max_tokens=300,
        )
        
        extracted_text = response.choices[0].message.content
        return jsonify({"text": extracted_text}), 200

    except Exception as e:
        app.logger.error(f"Error processing image: {e}")
        return jsonify({"error": "Failed to process image."}), 500

@app.route('/cart', methods=['POST'])
def add_to_cart():
    """Add extracted prescription to cart and return total items."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    CART.append(data["text"])
    return jsonify({"message": "Added to cart", "total_items": len(CART)}), 200


### **Main entry point**
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
