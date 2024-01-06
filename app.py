from flask import Flask, request, render_template_string, redirect, url_for
import json
from multiprocessing import Process
import dns

# Initialize the Flask application
app = Flask(__name__)

# File path for the NAT table
nat_table_file = 'dns_nat_table.json'

# Function to start the Flask app
def start_flask_app():
    # Run the Flask app on port 8080 accessible on all network interfaces
    app.run(port=8080,host='0.0.0.0')

# Function to start the DNS server
def start_dns_server():
    # Call the main function of the DNS server backend
    dns.main()

# Function to load the NAT table from a JSON file
def load_nat_table():
    try:
        with open(nat_table_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty dictionary if the file is not found or JSON is invalid
        return {}

# Function to save the NAT table to a JSON file
def save_nat_table(nat_table):
    with open(nat_table_file, 'w') as file:
        json.dump(nat_table, file, indent=4)

# Route for the index page
@app.route('/')
def index():
    nat_table = load_nat_table()
    # Render the index page with the current NAT table
    return render_template_string('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNS Proxy</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <style>
        body {
            background-color: #121212;
            color: #e4e4e4;
        }
        .container {
            padding-top: 20px;
        }
        .nav-tabs .nav-link.active {
            color: #fff;
            background-color: #343a40;
            border-color: #343a40;
        }
        .nav-tabs .nav-link {
            border: 1px solid #343a40;
            color: #fff;
        }
        .btn-primary, .btn-secondary, .btn-danger {
            color: #fff;
        }
        .btn-primary {
            background-color: #6c757d;
            border-color: #6c757d;
        }
        .btn-secondary {
            background-color: #6c757d;
            border-color: #6c757d;
        }
        .btn-danger {
            background-color: #dc3545;
            border-color: #dc3545;
        }
        .btn-delete-record {
            color: #ffffff;
            background-color: #ff6666; /* Lighter red */
            border-color: #ff6666;
        }

        .btn-delete-record:hover {
            color: #ffffff;
            background-color: #ff4d4d; /* Even lighter red on hover */
            border-color: #ff4d4d;
        }

        .list-group-item {
            background-color: #1e1e1e;
            border: 1px solid #323232;
        }
        .form-control {
            background-color: #323232;
            border: 1px solid #4b4b4b;
            color: #ddd;
        }
        .form-label {
            color: #ddd;
        }
        /* Additional styles to align delete button */
        .align-btn {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .align-btn form {
            margin-left: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center">Welcome to DNS Proxy</h1>
        <!-- Nav tabs -->
        <h2 class="text-center mt-4">Configuration</h2>

        <ul class="nav nav-tabs" id="natTab" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" id="add-nat-tab" data-toggle="tab" href="#add-nat" role="tab" aria-controls="add-nat" aria-selected="true">Add NAT Rule</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="update-resolver-tab" data-toggle="tab" href="#update-resolver" role="tab" aria-controls="add-nat" aria-selected="false">Update Resolver</a>
            </li>
        </ul>
        
        <!-- Tab panes -->
        <div class="tab-content">
            <div class="tab-pane fade show active" id="add-nat" role="tabpanel" aria-labelledby="add-nat-tab">
                <form action="/add" method="post">
                    <div class="form-group">
                        <label for="zone">Zone:</label>
                        <input type="text" class="form-control" id="zone" name="zone" required>
                    </div>
                    <div class="form-group">
                        <label for="src_ip">Real Subnet:</label>
                        <input type="text" class="form-control" id="src_ip" name="src_ip" required>
                    </div>
                    <div class="form-group">
                        <label for="dst_ip">NAT Subnet:</label>
                        <input type="text" class="form-control" id="dst_ip" name="dst_ip" required>
                    </div>
                    <div class="form-group">
                        <label for="resolver">Resolver (optional, default: 1.1.1.1):</label>
                        <input type="text" class="form-control" id="resolver" name="resolver">
                    </div>
                    <button type="submit" class="btn btn-primary">Add Entry</button>
                </form>
            </div>
            <div class="tab-pane fade" id="update-resolver" role="tabpanel" aria-labelledby="update-resolver-tab">
                <form action="/update_resolver" method="post">
                    <div class="form-group">
                        <label for="zone_resolver">Zone:</label>
                        <input type="text" class="form-control" id="zone_resolver" name="zone_resolver" required>
                    </div>
                    <div class="form-group">
                        <label for="new_resolver">New Resolver IP:</label>
                        <input type="text" class="form-control" id="new_resolver" name="new_resolver" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Update Resolver</button>
                </form>
            </div>
        </div>
        
        <!-- Display Current NAT Table -->
        <h2 class="text-center mt-4">Current NAT Table</h2>
        <ul class="list-group">
            {% for zone, data in nat_table.items() %}
                <li class="list-group-item">
                    <ul class="list-group">
                            <li class="d-flex justify-content-between align-items-center">
                    {{ zone }} - Resolver: {{ data.get("resolver", "1.1.1.1") }}
                    <form action="/delete_zone" method="post" style="display: inline;">
                                    <input type="hidden" name="zone" value="{{ zone }}">
                                    <button type="submit" class="btn btn-danger btn-sm">⚠️ Delete Zone</button>
                                </form>
                            </li>
                    </ul>
                    <br>                    
                    <ul class="list-group">
                        {% for src, dst in data.get("mappings", {}).items() %}
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                {{ src }} -> {{ dst }}
                                <form action="/delete" method="post" style="display: inline;">
                                    <input type="hidden" name="zone" value="{{ zone }}">
                                    <input type="hidden" name="src_ip" value="{{ src }}">
                                    <button type="submit" class="btn btn-delete-record btn-sm">Delete Record</button>
                                </form>
                            </li>
                        {% endfor %}
                    </ul>
                </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
''', nat_table=nat_table)

# Route to add a new NAT entry
@app.route('/add', methods=['POST'])
def add_entry():
    # Extract data from the form submission
    zone = request.form['zone']
    src_ip = request.form['src_ip']
    dst_ip = request.form['dst_ip']
    resolver = request.form.get('resolver', '1.1.1.1')
    
    # Load and update the NAT table
    nat_table = load_nat_table()

    if zone not in nat_table:
        nat_table[zone] = {"resolver": resolver, "mappings": {}}

    nat_table[zone]["mappings"][src_ip] = dst_ip

    # Save the updated NAT table and redirect to the index page
    save_nat_table(nat_table)
    return redirect(url_for('index'))

# Route to update a resolver for a specific zone
@app.route('/update_resolver', methods=['POST'])
def update_resolver():
    zone_resolver = request.form['zone_resolver']
    new_resolver = request.form['new_resolver']
    nat_table = load_nat_table()

    if zone_resolver in nat_table:
        nat_table[zone_resolver]["resolver"] = new_resolver

    save_nat_table(nat_table)
    return redirect(url_for('index'))

# Route to delete a specific NAT mapping
@app.route('/delete', methods=['POST'])
def delete_entry():
    zone = request.form['zone']
    src_ip = request.form['src_ip']
    nat_table = load_nat_table()

    if zone in nat_table and src_ip in nat_table[zone]["mappings"]:
        del nat_table[zone]["mappings"][src_ip]

    save_nat_table(nat_table)
    return redirect(url_for('index'))

# Route to delete an entire zone from the NAT table
@app.route('/delete_zone', methods=['POST'])
def delete_zone_entry():
    zone = request.form['zone']
    nat_table = load_nat_table()


    del nat_table[zone]

    save_nat_table(nat_table)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Start the DNS server in a separate process
    dns_process = Process(target=start_dns_server)
    dns_process.start()
    
    # Start the Flask app in the main process without the reloader
    start_flask_app()