import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")

# Check templates directory
templates_dir = os.path.join(current_dir, 'templates')
print(f"Templates directory: {templates_dir}")
print(f"Templates directory exists: {os.path.exists(templates_dir)}")

if os.path.exists(templates_dir):
    print("\nFiles in templates directory:")
    for file in os.listdir(templates_dir):
        print(f"- {file}")