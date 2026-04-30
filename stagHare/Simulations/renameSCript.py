import os
import json


def rename_ecab_files(directory_path="results/", old_prefix="ECab", new_prefix="ECab99"):
    """
    Rename all ECab files to include the gene version number
    Example: ECabSelfPlayRound.json -> ECab99SelfPlayRound.json
    """
    renamed_count = 0

    for file in os.listdir(directory_path):
        if file.startswith(old_prefix) and file.endswith('.json'):
            old_path = os.path.join(directory_path, file)

            # Create new filename by replacing the prefix
            new_file = file.replace(old_prefix, new_prefix, 1)
            new_path = os.path.join(directory_path, new_file)

            # Rename the file
            os.rename(old_path, new_path)
            renamed_count += 1
            print(f"Renamed: {file} -> {new_file}")

    print(f"\nTotal files renamed: {renamed_count}")
    return renamed_count


# Also update the JSON content to reflect the new name if needed
def update_json_scenario_names(directory_path="results/", old_prefix="ECab", new_prefix="ECab99"):
    """
    Update the scenario_type field inside JSON files to match new naming
    """
    updated_count = 0

    for file in os.listdir(directory_path):
        if file.startswith(new_prefix) and file.endswith('.json'):
            file_path = os.path.join(directory_path, file)

            with open(file_path, 'r') as f:
                data = json.load(f)

            # Update the file content if needed (depends on your JSON structure)
            # This is optional - only if your JSONs store the scenario name internally

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            updated_count += 1

    print(f"JSON files updated: {updated_count}")


import os


def undo_double_rename(directory_path="results/"):
    """
    Fix files that were accidentally renamed twice
    Example: ECab9999SelfPlayRound.json -> ECab99SelfPlayRound.json
    """
    fixed_count = 0

    for file in os.listdir(directory_path):
        if file.startswith("ECab9999") and file.endswith('.json'):
            old_path = os.path.join(directory_path, file)

            # Remove one "99" from the name
            new_file = file.replace("ECab9999", "ECab99", 1)
            new_path = os.path.join(directory_path, new_file)

            os.rename(old_path, new_path)
            fixed_count += 1
            print(f"Fixed: {file} -> {new_file}")

    print(f"\nTotal files fixed: {fixed_count}")
    return fixed_count


# if __name__ == "__main__":
#     undo_double_rename("results/")
#     print("\nDone! Files restored to ECab99 prefix.")
#
#
# # if __name__ == "__main__":
# #     # Rename files from ECab -> ECab99
# #     # rename_ecab_files("results/", "ECab", "ECab99")
# #     #
# #     # print("\nDone! Files renamed successfully.")