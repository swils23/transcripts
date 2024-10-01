import os, time

# if requirements.txt does not exist, create it
if not os.path.exists("requirements.txt"):
    raise FileNotFoundError(
        "requirements.txt not found, run pip freeze > requirements.txt"
    )

# Define the packages to be removed
packages_to_remove_startswith = ["torch"]

# get encoding of the file
with open("requirements.txt", "r") as f:
    requirements = f.readlines()

# Write the new requirements to the file
with open("requirements.txt", "w") as f:
    for requirement in requirements:
        if any(
            requirement.startswith(package) for package in packages_to_remove_startswith
        ):
            print(f"Removed {requirement.strip()}")
            continue
        f.write(requirement)
