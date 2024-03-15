from firebase import firebase

# Initialize Firebase
firebase = firebase.FirebaseApplication('https://hakctuesx-default-rtdb.firebaseio.com/', None)

# Example project data
projects = [
    {
        'project_type': 'Networking',
        'head': 'John Doe',
        'theme': 'Wireless Network Optimization',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed gravida, diam vel...'
    },
    {
        'project_type': 'Embedded',
        'head': 'Jane Smith',
        'theme': 'IoT Device Development',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla tincidunt...'
    },
    {
        'project_type': 'Software',
        'head': 'David Johnson',
        'theme': 'Web Application Development',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis condimentum...'
    }
]

# Function to populate projects in Firebase
def populate_projects():
    for project in projects:
        firebase.post('/projects', project)

# Call the function to populate projects
populate_projects()

print("Example projects populated successfully.")
