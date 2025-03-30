from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
from openai import OpenAI

app = Flask(__name__)
swagger = Swagger(app)  # Initialize Swagger

@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")

client = OpenAI(
    api_key=os.getenv('GEMINI_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def fetch_information(topic):
    """Fetch structured information using OpenAI API (Grok-3 or GPT-4)."""
    system_prompt = (
        "You are an expert in creating structured summaries for infographic design. "
        "Format responses with Title, Key Facts (4-6 points), Statistics, Impact, and Call to Action. "
        "Keep responses factual and data-driven."
    )
    
    user_prompt = (
        f"Create a structured breakdown of '{topic}' with the following sections:\n"
        "- **Title**: A catchy title summarizing the topic.\n"
        "- **Key Facts**: Bullet points of 4-6 important facts.\n"
        "- **Statistics**: Any relevant numerical data or percentages.\n"
        "- **Impact**: A brief statement on why this topic is important.\n"
        "- **Call to Action**: A short takeaway related to the topic."
    )
    
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    print(response)
    return response.choices[0].message.content

def generate_infographic(content):
    """Generate an infographic image using OpenAI's DALL·E API."""
    response = client.images.generate(
        model="gemini-2.0-flash-exp-image-generation",
        prompt=f"Infographic: {content}. Make it visually engaging with icons, graphs, and highlights.",
        size="1024x1024",
        n=1
    )
    print(response)
    return response["data"][0]["url"]

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