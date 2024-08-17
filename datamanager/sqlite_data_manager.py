from .data_models import *
from .data_manager_interface import DataManagerInterface


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db):
        self.db = db

    def get_destinations(self, user_id, destination_id=None):
        """Get all user's destinations or a specific destination."""
        user = User.query.get(user_id)
        if user:
            if destination_id:
                return Destination.query.filter_by(user_id=user_id, id=destination_id).first()
            else:
                return user.favorites
        else:
            return []

    def add_destination(self, user_id, destination_data):
        """Add a new destination to a user's favorite destination list."""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User does not exist.")

        required_fields = ['des_name', 'poster_url', 'activities', 'accommodations', 'transportation']
        for field in required_fields:
            if field not in destination_data:
                raise ValueError(f"Missing required field:{field}")

        new_destination = Destination(
            user=user,
            des_name=destination_data['des_name'],
            poster_url=destination_data['poster_url'],
            activities=destination_data['activities'],
            accommodations=destination_data['accommodations'],
            transportation=destination_data['transportation']
        )
        self.db.session.add(new_destination)
        self.db.session.commit()

    def delete_destination(self, user_id, destination_id):
        """Delete a destination from the database."""
        destination = Destination.query.filter_by(user_id=user_id, id=destination_id).first()
        if not destination:
            return False

        print("Deleting destination", destination)

        self.db.session.delete(destination)
        self.db.session.commit()
        print("Destination deleted successfully.")
        return True

    def get_destination_by_id(self, destination_id):
        """Retrieve a destination by its ID."""
        return Destination.query.get(destination_id)

    def update_destination(self, destination_id, updated_data):
        """Update an existing destination."""
        try:
            existing_destination = Destination.query.get(destination_id)
            if not existing_destination:
                return False

            # Update only if the data is not empty
            if updated_data.get('poster_url'):
                existing_destination.poster_url = updated_data['poster_url']
            if updated_data.get('activities'):
                existing_destination.activities = updated_data['activities']
            if updated_data.get('accommodations'):
                existing_destination.accommodations = updated_data['accommodations']
            if updated_data.get('transportation'):
                existing_destination.transportation = updated_data['transportation']

            self.db.session.commit()
            print("Destination updated successfully.")
            return True
        except Exception as e:
            print(f"Error updating destination: {e}")
            return False






