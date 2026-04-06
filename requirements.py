import subprocess
import pkg_resources
from tabulate import tabulate
import importlib
import inspect
import os

def get_package_version(package_name):
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return "Not installed"

def get_package_upgrade_info(requirements_file):
    with open(requirements_file, 'r') as f:
        packages = f.read().splitlines()

    upgrade_info = []

    for package in packages:
        package_name, current_version = package.split('==')
        new_version = get_package_version(package_name)
        if new_version != "Not installed" and new_version != current_version:
            upgrade_info.append([package_name, current_version, new_version])

    return upgrade_info

def print_upgrade_info(upgrade_info):
    if upgrade_info:
        print("\nPackages that need to be upgraded:")
        print(tabulate(upgrade_info, headers=["Package", "Current Version", "New Version"], tablefmt="grid"))
    else:
        print("\nAll packages are up-to-date.")

def upgrade_packages(requirements_file):
    upgrade_info = get_package_upgrade_info(requirements_file)

    for package_name, current_version, new_version in upgrade_info:
        print(f"Upgrading {package_name} from {current_version} to {new_version}...")
        try:
            subprocess.check_call(['pip', 'install', '--upgrade', package_name])
        except subprocess.CalledProcessError:
            print(f"Failed to upgrade {package_name}")

    update_requirements(requirements_file)

    return upgrade_info

def print_package_versions(requirements_file):
    with open(requirements_file, 'r') as f:
        requirements = f.readlines()

    installed_packages = []
    not_installed_packages = []

    for req in requirements:
        package_name = req.strip().split('==')[0]
        current_version = get_package_version(package_name)

        if current_version == "Not installed":
            not_installed_packages.append(package_name)
        else:
            installed_packages.append([package_name, current_version])

    if installed_packages:
        print("\nCurrently installed packages:")
        print(tabulate(installed_packages, headers=["Package", "Installed Version"], tablefmt="grid"))

    if not_installed_packages:
        print("\nPackages not installed:")
        for package in not_installed_packages:
            print(f"- {package}")

    additional_packages = ['python', 'pip', 'setuptools', 'wheel']
    additional_versions = []
    for package in additional_packages:
        version = get_package_version(package)
        additional_versions.append([package, version])

    print("\nAdditional key packages:")
    print(tabulate(additional_versions, headers=["Package", "Version"], tablefmt="grid"))

    return not_installed_packages

def update_requirements(requirements_file):
    with open(requirements_file, 'r') as f:
        requirements = f.readlines()

    updated_requirements = []
    for req in requirements:
        package_name = req.strip().split('==')[0]
        current_version = get_package_version(package_name)
        if current_version != "Not installed":
            updated_requirements.append(f"{package_name}=={current_version}\n")
        else:
            updated_requirements.append(req)

    with open(requirements_file, 'w') as f:
        f.writelines(updated_requirements)

    print(f"Requirements.txt file updated with current installed versions.")

def install_missing_packages(not_installed_packages, requirements_file):
    if not_installed_packages:
        print("Installing missing packages:")
        for package in not_installed_packages:
            print(f"Installing {package}...")
            try:
                subprocess.check_call(['pip', 'install', package])
                print(f"{package} installed successfully.")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}")
        print("All missing packages installed successfully.")
        update_requirements(requirements_file)
    else:
        print("All required packages are already installed.")

def print_package_details(not_installed_packages, folder):
    os.makedirs(folder, exist_ok=True)
    for package_name in not_installed_packages:
        output_file = os.path.join(folder, f"{package_name}_details.txt")
        with open(output_file, 'w') as f:
            f.write(print_package_info(package_name))

def print_package_info(package_name):
    try:
        package = importlib.import_module(package_name)
        output = f"Package: {package_name}\n"
        output += "Docstring:\n"
        output += f"{package.__doc__}\n\n"
        
        output += "Attributes and Variables:\n"
        for attr_name, attr_value in inspect.getmembers(package, lambda a: not(inspect.isroutine(a))):
            output += f"  - {attr_name}: {type(attr_value).__name__}\n"

        output += "\nModules:\n"
        for module_name, module in inspect.getmembers(package, inspect.ismodule):
            output += f"  - {module_name}\n"
        
        output += "\nFunctions:\n"
        for function_name, function in inspect.getmembers(package, inspect.isfunction):
            output += f"  - {function_name}()\n"
            output += f"    Docstring: {function.__doc__}\n"

        output += "\nClasses:\n"
        for class_name, class_obj in inspect.getmembers(package, inspect.isclass):
            output += f"  - {class_name}\n"
            output += f"    Docstring: {class_obj.__doc__}\n"
            output += "    Methods:\n"
            for method_name, method in inspect.getmembers(class_obj, inspect.isfunction):
                output += f"      - {method_name}()\n"
                output += f"        Docstring: {method.__doc__}\n"

        output += "---\n"
        return output
    except ImportError:
        return f"Error: {package_name} could not be imported.\n"

def print_all_package_info(requirements_file, folder):
    os.makedirs(folder, exist_ok=True)
    with open(requirements_file, 'r') as f:
        requirements = f.readlines()

    for req in requirements:
        package_name = req.strip().split('==')[0]
        output_file = os.path.join(folder, f"{package_name}_info.txt")
        try:
            with open(output_file, 'w') as f:
                f.write(print_package_info(package_name))
        except ValueError as e:
            print(f"Error with {package_name}: {e}. Skipping...")

def install_specific_package(package_name, requirements_file):
    current_version = get_package_version(package_name)
    if current_version == "Not installed":
        print(f"Installing {package_name}...")
        try:
            subprocess.check_call(['pip', 'install', package_name])
            new_version = get_package_version(package_name)
            print(f"{package_name} installed successfully (version {new_version}).")
            
            with open(requirements_file, 'r') as f:
                requirements = f.readlines()
            
            package_in_requirements = False
            updated_requirements = []
            for req in requirements:
                if req.strip().split('==')[0] == package_name:
                    updated_requirements.append(f"{package_name}=={new_version}\n")
                    package_in_requirements = True
                else:
                    updated_requirements.append(req)
            
            if not package_in_requirements:
                updated_requirements.append(f"{package_name}=={new_version}\n")
            
            with open(requirements_file, 'w') as f:
                f.writelines(updated_requirements)
            
            print(f"Requirements.txt updated with {package_name}=={new_version}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name}")
    else:
        print(f"{package_name} is already installed (version {current_version}).")

def main():
    requirements_file = "requirements.txt"
    output_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(output_dir, "package_info")
    not_installed_file = os.path.join(folder, "not_installed_packages.txt")

    while True:
        print("\nPackage Manager Menu:")
        print("1. Print Package Versions")
        print("2. Show Upgrade Information")
        print("3. Upgrade Packages")
        print("4. Install Missing Packages")
        print("5. Install Specific Package")
        print("6. Update Requirements.txt")
        print("7. Print Package Details (not installed)")
        print("8. Print All Package Info")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        if choice == "1":
            not_installed_packages = print_package_versions(requirements_file)
        elif choice == "2":
            upgrade_info = get_package_upgrade_info(requirements_file)
            print_upgrade_info(upgrade_info)
        elif choice == "3":
            upgraded_packages = upgrade_packages(requirements_file)
            print("\nUpgraded Package Versions:")
            print(tabulate(upgraded_packages, headers=["Package", "Old Version", "New Version"], tablefmt="grid"))
        elif choice == "4":
            not_installed_packages = print_package_versions(requirements_file)
            install_missing_packages(not_installed_packages, requirements_file)
        elif choice == "5":
            package_name = input("Enter the name of the package to install: ")
            install_specific_package(package_name, requirements_file)
        elif choice == "6":
            update_requirements(requirements_file)
        elif choice == "7":
            not_installed_packages = print_package_versions(requirements_file)
            print_package_details(not_installed_packages, folder)
            print(f"Package details for not installed packages saved to: {not_installed_file}")
        elif choice == "8":
            print_all_package_info(requirements_file, folder)
            print(f"Package information saved to: {folder}")
        elif choice == "9":
            print("Exiting Package Manager...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
