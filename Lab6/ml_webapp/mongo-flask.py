from flask import Flask, request, jsonify
from pymongo import MongoClient
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd
import datetime
import gridfs
import json
counter = 0

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["accelerometer_data"]
collection = db["data"]
# fs = gridfs.GridFS(db)

columns = ["time_ms","x","y","z","letter"]
# df = pd.DataFrame(columns=columns)

# Initialize a dictionary to keep track of file counters for each letter
file_counters = {}

# Define the endpoint to receive data
@app.route('/data', methods=['POST'])
def receive_data():
    # global df

    data = json.loads(request.json)  # Extract JSON data from the request
    formatted_data = []
    letter = None

    for reading in data['readings']:
        # For CSV format string: "time_ms,x,y,z,letter"
        # print(reading)
        entries = reading.split(",")
        # print(entries)
        letter = entries[4]
        formatted_data.append({
            "time_ms": float(entries[0]),
            "x": float(entries[1]),
            "y": float(entries[2]),
            "z": float(entries[3]),
            "letter": entries[4]
        })
        
    data['readings'] = formatted_data
    #append the new data to df
    # print(formatted_data)
    # print(letter)
#     new_data = pd.DataFrame(formatted_data, =columcolumnsns)

    # Track the file counter for the current letter
    # if letter not in file_counters:
    #     file_counters[letter] = 1  # Initialize counter for new letter
    # else:
    #     file_counters[letter] += 1  # Increment counter for existing letter

    # Generate the CSV filename with the counter
    # csv_file = f"{letter}_{file_counters[letter]}.csv"
    # print(f"Saving to {csv_file}")

    # with open(csv_file, 'w') as csv:
    #     new_data.to_csv(csv, mode='w',index=False, header=False)

    # csv_file = f"{letter}.csv"
    # print(csv_file)
    

    # collection.insert_many(new_data)  # Insert data into MongoDB

# Convert DataFrame to a dictionary and insert into MongoDB
#     new_data_dict = new_data.to_dict(orient="dict")
    # collection.insert_many(new_data_dict)  # Insert multiple documents into MongoDB
    collection.insert_one(data)  # Insert multiple documents into MongoDB
    # print(letter)
    # print("Received data:", data)  # Print data in the terminal
    # print(letter)
    return jsonify({"status": "success"}), 200

# Define the endpoint to receive data
@app.route('/get_data', methods=['GET'])
def show_data():
    # document = collection.find()
    # for doc in document:
    #     print("Stored data:", doc)  # Print data in the terminal

    most_recent_doc = collection.find_one(sort=[('_id', -1)])
    # print("Most recent:" , most_recent_doc)

    data = pd.DataFrame(most_recent_doc['readings'])
    X = data.to_numpy()[:, 0:-1]
    X = X[:75]

    # Convert X to a numpy array
    X = np.array(X).astype(float)

    # Define different scalers for different columns
    # scaler_first_column = MinMaxScaler(feature_range=(0, 1))  # Scaling first column to [0, 1]
    scaler_other_column = MinMaxScaler(feature_range=(-1, 1))  # Scaling first column to [0, 1]

    # X[:, 0:1] = scaler_first_column.fit_transform(X[:, 0:1])
    X[:, 1:] = scaler_other_column.fit_transform(X[:, 1:])

    X = X[:, 1:].reshape(1, 75*3)
    # X = X.reshape(1, 75*3)
    print(X.shape)

    from pickle import load
    with open("model_v1.pkl", "rb") as f:
        random_forest = load(f)
    
    prediction = random_forest.predict(X)
    print("Prediction: ", prediction)

    return jsonify({"status": "success", "letter": f"{str(prediction[0]).upper()}"}), 200

#CSV files to concatenate


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# with open("file.json", 'w') as json_file:
# json.dump(data, json_file, indent=4)
# with open("file.json", "rb") as file_data:
# file_id = fs.put(file_data, filename="file.json") 