from flask import Flask, jsonify, request
from flask_cors import CORS
from services.openai_service import generate_chat_response
from utils.middleware import authenticate_supabase_token
from auth.register_user import register_user
from auth.login_user import login_user
from supabase import create_client, Client
from services.filter_service import FilterService  # Import the new filter service
from services.google_maps_service import GoogleMapsService  # Import the Google Maps service


app = Flask(__name__)
CORS(app)
import os

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route('/')
def index():
    return jsonify({'message': 'Flask app is running!'})

# Initialize services
google_maps_service = GoogleMapsService()
filter_service = FilterService()

@app.route('/api/activities', methods=['POST'])
def get_activities():
    data = request.json

    # Receive places from frontend
    places = data.get('places', [])
    budget = data.get('budget')
    group_size = data.get('group_size')

    # Print to debug
    print("Received places:", places)
    for place in places:
        print("Tags for place '{}': {}".format(place['name'], place['tags']))  # Ensure tags are an array

    # Apply filters for budget and group size
    filtered_places = filter_service.apply_filters(places, budget, group_size)

    # Print the filtered places
    print("Filtered places:", filtered_places)

    return jsonify({'places': filtered_places})




# Route for registering a user
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json

    # Ensure email and password are in the request body
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Call the register_user function
    response = register_user(email, password)

    # Return the response as JSON
    return jsonify(response)


#  Route for logging in a user
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    print(data)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    response = login_user(email, password)
    return jsonify(response)


@app.route('/api/logout', methods=['POST'])
def logout():
    """
    This function logs out the user using Supabase and returns the raw response for inspection.
    """
    try:
        # Call Supabase's sign-out method
        response = supabase.auth.sign_out()

        # Return the raw response for inspection (stringified)
        return jsonify({"response": str(response)}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"message": f"An error occurred during logout: {str(e)}"}), 500
    
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Parse the incoming JSON request body
        data = request.json
        print('Received data:', data)

        # Generate chat response using OpenAI
        response = generate_chat_response(data)
        return jsonify({'message': response})

    except Exception as e:
        # Return any errors as a response
        return jsonify({
            'error': f'Something went wrong. Details: {str(e)}'
        }), 500
    

if __name__ == '__main__':
    app.run(debug=True)
