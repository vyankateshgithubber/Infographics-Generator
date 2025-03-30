from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os

app = Flask(__name__)
swagger = Swagger(app)  # Initialize Swagger

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def fetch_information(topic):
    try:
        """Fetch structured information using Google Gemini Pro."""
        prompt = (
            "Create a structured breakdown of the following topic. Format as follows:\n"
            "Title: [Catchy title]\n"
            "Key Facts:\n- [4-6 bullet points]\n"
            "Statistics: [Relevant numerical data]\n"
            "Impact: [Brief importance statement]\n"
            "Call to Action: [Short takeaway]\n\n"
            f"Topic: {topic}"
        )
        
        response = client.models.generate_content(
             model="gemini-2.0-flash",
              contents=[prompt])
        #print(response)
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None
    

@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")

def generate_infographic(content):
    try:
        """Generate an infographic image using Gemini Pro Vision."""
        prompt = f"Create Image Create an infographic image visualization for:\n{content}\nMake it visually engaging with icons, graphs, and highlights."
        
        response = client.models.generate_images(
                model="imagen-3.0-generate-001",
                prompt=prompt
                
            )
        print(response)
        
        for generated_image in response.generated_images:
          # Open the image from binary data
          image = Image.open(BytesIO(generated_image.image.image_bytes))
          
          # Save the image to a temporary buffer
          buffered = BytesIO()
          image.save(buffered, format="PNG")
          
          # Convert to base64 string
          img_str = base64.b64encode(buffered.getvalue()).decode()
          
          # Create the base64 URL
          img_base64_url = f"data:image/png;base64,{img_str}"
          
          # Save locally if needed
          image.save('gemini-native-image.png')
          
          return img_base64_url
        
        
        return None
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

@app.route("/generate_infographic", methods=["POST"])
def generate_infographic_endpoint():
    """
    Generate an infographic image for a given topic.
    ---
    tags:
      - Infographic
    parameters:
      - name: topic
        in: body
        type: string
        required: true
        description: The topic for which to generate the infographic.
    responses:
      200:
        description: Infographic generated successfully
        schema:
          type: object
          properties:
            topic:
              type: string
              description: The topic provided by the user.
            image_url:
              type: string
              description: The URL of the generated infographic image.
      400:
        description: Bad request (e.g., missing topic)
    """
    print(request.json)
    data = request.json
    topic = data.get("topic")
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    # Step 1: Fetch Information
    structured_data = fetch_information(topic)
    print(structured_data)
    # Step 2: Generate Infographic Image
    image_url = generate_infographic(structured_data)
    
    return jsonify({"topic": topic, "image_url": image_url})

if __name__ == "__main__":
    app.run(debug=True)


