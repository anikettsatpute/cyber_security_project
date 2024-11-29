# create a venv
# take input from user if to create a venv or not

input="y"
read -p "Do you want to create a virtual environment? (y/n) " input

if [ $input == "y" ]; then
    echo "Creating a virtual environment"
    python3 -m venv venv
    source venv/bin/activate
else
    echo "Skipping virtual environment creation"
fi
# activate the venv
source venv/bin/activate

# install the requirements
pip install -r requirements.txt