from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """Create an interface."""

    @abstractmethod
    def add_destination(self, user_id, destination_data):
        pass

    @abstractmethod
    def delete_destination(self, user_id, destination_id):
        pass

    @abstractmethod
    def update_destination(self, user_id, destination_id, new_poster, new_activities, new_accommodations, new_transportation):
        pass

    # @abstractmethod
    # def get_all_activities(self):
    #     pass
    #
    # @abstractmethod
    # def get_all_accommodations(self):
    #     pass
    #
    # @abstractmethod
    # def get_all_transportations(self):
    #     pass

