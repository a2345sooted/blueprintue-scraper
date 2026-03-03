import os
import json
import re

class OutputHandler:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.processed_file = os.path.join(self.output_dir, "processed_blueprints.json")
        self.processed_ids = self._load_processed_ids()

    def _load_processed_ids(self):
        """
        Loads the list of already processed blueprint IDs.
        """
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except (json.JSONDecodeError, IOError):
                return set()
        return set()

    def _save_processed_ids(self):
        """
        Saves the list of processed blueprint IDs to disk.
        """
        try:
            with open(self.processed_file, "w", encoding="utf-8") as f:
                json.dump(list(self.processed_ids), f, indent=4)
        except IOError as e:
            print(f"Error saving processed IDs: {e}")

    def is_processed(self, bp_id):
        """
        Checks if a blueprint ID has already been processed.
        """
        if not bp_id:
            return False
        return bp_id in self.processed_ids

    def mark_as_processed(self, bp_id):
        """
        Adds a blueprint ID to the processed list and saves it.
        """
        if bp_id:
            self.processed_ids.add(bp_id)
            self._save_processed_ids()

    def _slugify(self, text):
        """
        Simplifies a string to be used as a directory name.
        """
        # Convert to lowercase and remove non-alphanumeric characters
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)
        return text.strip('-')

    def save_blueprint(self, title, code, summary, bp_id=None, metadata=None):
        """
        Saves blueprint details into a structured directory.
        """
        # Create a unique directory name for the blueprint
        slug = self._slugify(title)
        
        # Ensure the directory name isn't empty after slugifying
        if not slug:
            slug = "untitled-blueprint"
            
        # Include the ID if provided to ensure uniqueness
        if bp_id:
            blueprint_dir_name = f"{slug}-{bp_id}"
        else:
            blueprint_dir_name = slug
            
        blueprint_dir = os.path.join(self.output_dir, blueprint_dir_name)
        
        # If directory exists (even with ID), append a suffix to avoid overwriting
        counter = 1
        base_dir = blueprint_dir
        while os.path.exists(blueprint_dir):
            blueprint_dir = f"{base_dir}-{counter}"
            counter += 1
            
        os.makedirs(blueprint_dir)
        
        # Save the full blueprint code
        with open(os.path.join(blueprint_dir, "blueprint.txt"), "w", encoding="utf-8") as f:
            f.write(code)
            
        # Save the summary as a markdown file
        with open(os.path.join(blueprint_dir, "summary.md"), "w", encoding="utf-8") as f:
            f.write(summary)
            
        # Save metadata
        if metadata:
            with open(os.path.join(blueprint_dir, "metadata.json"), "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
                
        return blueprint_dir
