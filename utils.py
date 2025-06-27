import pandas as pd
import numpy as np
from datetime import datetime
import labstep

class Query_Info:
    def __init__(self, 
                user: labstep.entities.user.model.User, 
                USER_EMAIL: str, 
                API_KEY: str, 
                API_NAME: str, 
                WORKSPACE_NAME: str = "Laboratory for Applied Virology and Precision Medicine"):
        
        self.user_email = USER_EMAIL
        self.api_key = API_KEY
        self.api_name = API_NAME
        self.workspace_name = WORKSPACE_NAME
        self.user = user
        self.workspace_id = self.__workspace_id()
        if self.workspace_id is None:
            raise ValueError(f"Workspace '{self.workspace_name}' not found.")
        self.workspace = self.user.getWorkspace(self.workspace_id)
    
    def __workspace_id(self):
        """Get the ID of the workspace."""
        for workspace in self.user.getWorkspaces():
            if workspace["name"] == self.workspace_name:
                return workspace["id"]
        return None
    
    # Get all experiments in the workspace
    def get_experiment(self):
        experiments = self.workspace.getExperiments()

        experiments_list = []
        for experiment in experiments:
            experiments_list.append([
                experiment.id,
                experiment.name,
                experiment.author.get("name", "Unknown"),
                experiment.author.get("id", "Unknown")
            ])
        return pd.DataFrame(experiments_list, columns=["ID", "Experiment Name", "Author Name", "Author ID"])

    def get_protocol(self):
        protocols = self.workspace.getProtocols()

        protocols_list = []
        for protocol in protocols:

            protocols_list.append([
                protocol.id,
                protocol.name,
                protocol.author.get("name", "Unknown"),
                protocol.author.get("id", "Unknown")
            ])
        return pd.DataFrame(protocols_list, columns=["ID", "Protocol Name", "Author Name", "Author ID"])
    
    def get_resources(self):
        resources = self.workspace.getResources()
        
        resources_list = []
        for resource in resources:
            formatted_date = (
                datetime.fromisoformat(resource.updated_at).strftime('%Y-%m-%d')
                if resource.updated_at else "Invalid date"
            )
            resources_list.append([
                resource.id,
                resource.name or "Unknown",
                resource.available_resource_item_count,
                resource.available_resource_item_count_alert_threshold or "Unspecified",
                formatted_date,
            ])

        return pd.DataFrame(resources_list, columns=["ID", "Resource Name", "Available Count", "Alert Threshold", "Last Updated"])
    
    def get_devices(self):
        devices = self.workspace.getDevices()
        
        devices_list = []
        for device in devices:
            devices_list.append([
                device.id,
                device.name or "Unknown",])

        return pd.DataFrame(devices_list, columns=["ID", "Device Name"])

    def get_device_booking(self, device_id: None):
        if device_id is None:
            raise ValueError("Device ID must be provided to get bookings.")
        if not isinstance(device_id, int):
            device_id = int(device_id)
        # Get the device object
        if not self.user.getDevice(device_id):
            raise ValueError(f"Device with ID {device_id} does not exist in the workspace.")
        device = self.user.getDevice(device_id)
        device_bookings = device.getDeviceBookings()

        return device_bookings
    
    def get_device_category(self, device_id: None):
        if device_id is None:
            raise ValueError("Device ID must be provided to get bookings.")
        if not isinstance(device_id, int):
            device_id = int(device_id)
        # Get the device object
        if not self.user.getDevice(device_id):
            raise ValueError(f"Device with ID {device_id} does not exist in the workspace.")
        device = self.user.getDevice(device_id)
        device_category = device.getDeviceCategory()

        return device_category
    
    def get_resource_category_id(self):
        """Get the ID of the resource category."""
        resource_categories = self.workspace.getResourceCategorys()
        resource_category_id = []
        if not resource_categories:
            raise ValueError("No resource categories found in the workspace.")
        # Find the resource category with the name "General"
        for resource_category in resource_categories:
            resource_category_id.append([
                resource_category["name"],
                resource_category["id"],                    
                ])
        return pd.DataFrame(resource_category_id, columns=["Resource Category Name", "Resource Category ID"])
        # return resource_category_id



class Edit_Resources(Query_Info):
    def __init__(self, 
                user: labstep.entities.user.model.User, 
                USER_EMAIL: str, 
                API_KEY: str, 
                API_NAME: str, 
                WORKSPACE_NAME: str = "Laboratory for Applied Virology and Precision Medicine"):
        super().__init__(user, USER_EMAIL, API_KEY, API_NAME, WORKSPACE_NAME)
        user.setWorkspace(self.workspace_id)
    
    def add_new_resource(self, resource_name: str = None, resource_category_name: str = None, alert_threshold: int = None):
        if resource_name is None or resource_category_name is None:
            raise ValueError("Resource name, category name must be provided.")
        
        # Get the resource category ID
        resource_category_id_df = self.get_resource_category_id()
        match = resource_category_id_df[
            resource_category_id_df["Resource Category Name"] == resource_category_name
            ]
        if match.empty:
            raise ValueError(f"Resource category '{resource_category_name}' not found.")
        resource_category_id = int(match["Resource Category ID"].iloc[0])

        # Create a new resource
        new_resource = self.user.newResource(name=resource_name, resource_category_id=resource_category_id)
        return print(f"Resource '{resource_name}' created with ID: {new_resource.id}")