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

    def update_destination(self, user_id, destination_id, new_poster, new_activities, new_accommodations, new_transportation):
        """Update an existing destination."""
        existing_destination = Destination.query.filter_by(user_id=user_id, id=destination_id).first()
        if not existing_destination:
            return False

        existing_destination.poster_url = new_poster
        existing_destination.activities = new_activities
        existing_destination.accommodations = new_accommodations
        existing_destination.transportation = new_transportation
        self.db.session.commit()
        print("Destination updated successfully.")






