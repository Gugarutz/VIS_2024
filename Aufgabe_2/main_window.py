from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMenuBar, QFileDialog, QMessageBox, QDialog, QFormLayout, QLineEdit, QPushButton
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.all import vtkInteractorStyleTrackballCamera, vtkCamera
from vtkmodules.vtkRenderingCore import vtkRenderer
import mbsModel
import body  # Ensure body module is imported
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()

        # Initialize the model and set up the renderer
        self.model = model
        self.renderer = vtkRenderer()

        # Set up the main window properties
        self.setWindowTitle("FreePyne Viewer")
        self.resize(1024, 768)

        # Set up the central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Set up the layout
        layout = QVBoxLayout(self.central_widget)

        # Use QVTKRenderWindowInteractor to manage the render window
        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        layout.addWidget(self.vtk_widget)

        # Bind the renderer to the render window
        self.vtk_render_window = self.vtk_widget.GetRenderWindow()
        self.vtk_render_window.AddRenderer(self.renderer)

        # Set up the interactor
        self.vtk_interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        style = vtkInteractorStyleTrackballCamera()
        self.vtk_interactor.SetInteractorStyle(style)
        self.vtk_interactor.Initialize()

        # Create the menu bar
        self.create_menu_bar()

        # Show the model
        self.update_renderer()

    def create_menu_bar(self):
        # Menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Add actions to the File menu
        file_menu.addAction("Load", self.load_file)
        file_menu.addAction("Save", self.save_file)
        file_menu.addAction("Import FDD", self.import_fdd)
        file_menu.addAction("Import OBJ", self.import_obj)  # New menu item for importing OBJ
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close_app)

        # View menu
        view_menu = menu_bar.addMenu("View")

        # Add actions to the View menu
        view_menu.addAction("ISO",   lambda: self.change_view("ISO"))
        view_menu.addAction("Right", lambda: self.change_view("Right"))
        view_menu.addAction("Top",   lambda: self.change_view("Top"))
        view_menu.addAction("Front", lambda: self.change_view("Front"))

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load File", "", "JSON Files (*.json)")
        if file_name:
            self.model.clearModel()  # Clear the current model
            if self.model.loadDatabase(file_name):
                QMessageBox.information(self, "Load File", f"Loaded file: {file_name}")
                self.update_renderer()  # Update renderer with the new model
            else:
                QMessageBox.critical(self, "Error", "Failed to load JSON file.")

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json)")
        if file_name:
            if self.model.saveDatabase(file_name):
                QMessageBox.information(self, "Save File", f"Saved file: {file_name}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save JSON file.")

    def import_fdd(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Fdd File", "", "FDD Files (*.fdd)")
        if file_name:
            QMessageBox.information(self, "Import FDD", f"Imported FDD file: {file_name}")
            # Import the FDD file into the model
            if self.model.importFddFile(file_name):  # Assuming this method is implemented in mbsModel
                self.update_renderer()  # Update renderer with the new model
            else:
                QMessageBox.critical(self, "Error", "Failed to import FDD file.")

    def import_obj(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Import OBJ File", "", "OBJ Files (*.obj)")
        if file_name:
            dialog = QDialog(self)
            dialog.setWindowTitle("Set Position, Rotation, and Color")

            layout = QFormLayout(dialog)
            position_input = QLineEdit(dialog)
            rotation_input = QLineEdit(dialog)
            color_input = QLineEdit(dialog)
            layout.addRow("Position (x,y,z):", position_input)
            layout.addRow("Rotation (x,y,z):", rotation_input)
            layout.addRow("Color (r,g,b)(%):", color_input)

            button_box = QWidget(dialog)
            button_layout = QVBoxLayout(button_box)
            ok_button = QPushButton("OK", dialog)
            cancel_button = QPushButton("Cancel", dialog)
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addRow(button_box)

            def on_ok():
                position = list(map(float, position_input.text().split(',')))
                rotation = list(map(float, rotation_input.text().split(',')))
                color = [c / 100.0 for c in map(int, color_input.text().split(','))]
                self.add_obj_to_model(file_name, position, rotation, color)
                dialog.accept()

            def on_cancel():
                dialog.reject()

            ok_button.clicked.connect(on_ok)
            cancel_button.clicked.connect(on_cancel)

            dialog.exec()

    def add_obj_to_model(self, file_name, position, rotation, color):
        parameter = {
            "mass": {"type": "float", "value": 1.0},
            "COG": {"type": "vector", "value": [0.0, 0.0, 0.0]},
            "geometry": {"type": "filepath", "value": file_name},
            "position": {"type": "vector", "value": position},
            "x_axis": {"type": "vector", "value": [1.0, 0.0, 0.0]},
            "y_axis": {"type": "vector", "value": [0.0, 1.0, 0.0]},
            "z_axis": {"type": "vector", "value": [0.0, 0.0, 1.0]},
            "color": {"type": "colorvector", "value": color + [0]}
        }

        # Apply rotation to the axes
        rotation_matrix = self.euler_to_rotation_matrix(rotation)
        parameter["x_axis"]["value"] = rotation_matrix.dot([1.0, 0.0, 0.0]).tolist()
        parameter["y_axis"]["value"] = rotation_matrix.dot([0.0, 1.0, 0.0]).tolist()
        parameter["z_axis"]["value"] = rotation_matrix.dot([0.0, 0.0, 1.0]).tolist()

        new_body = body.rigidBody(parameter=parameter)
        self.model._mbsModel__mbsObjectList.append(new_body)  # Use the correct attribute
        self.update_renderer()

    def euler_to_rotation_matrix(self, rotation):
        # Convert Euler angles to a rotation matrix.
        rx, ry, rz = np.deg2rad(rotation)
        cos_rx, sin_rx = np.cos(rx), np.sin(rx)
        cos_ry, sin_ry = np.cos(ry), np.sin(ry)
        cos_rz, sin_rz = np.cos(rz), np.sin(rz)

        rotation_x = np.array([[1, 0, 0],
                               [0, cos_rx, -sin_rx],
                               [0, sin_rx, cos_rx]])

        rotation_y = np.array([[cos_ry, 0, sin_ry],
                               [0, 1, 0],
                               [-sin_ry, 0, cos_ry]])

        rotation_z = np.array([[cos_rz, -sin_rz, 0],
                               [sin_rz, cos_rz, 0],
                               [0, 0, 1]])

        return rotation_z.dot(rotation_y).dot(rotation_x)

    def close_app(self):
        self.close()


##--------------------------------------------------------------------------------------------------------------------##
##      RENDER WINDOW ADJUSTMENT AND UPDATES TO RENDERER
##--------------------------------------------------------------------------------------------------------------------##
    def update_renderer(self):
        # Clear the renderer and display the updated model.
        self.renderer.RemoveAllViewProps()  # Clear the current visualization
        self.model.showModel(self.renderer)  # Render the updated model

        # Adjust the camera to fit the new model
        self.change_view("Iso")

        self.vtk_render_window.Render()  # Refresh the VTK window

    def change_view(self, view):
        # Change the camera view based on the selected option.
        if not self.renderer:
            return

        # Adjust the camera to the selected view
        camera = self.renderer.GetActiveCamera()

        # Get the bounds of the model in world coordinates
        bounds = self.renderer.ComputeVisiblePropBounds()

        if bounds:
            # Calculate the center of the bounding box
            center = [(bounds[0] + bounds[1]) / 2,
                      (bounds[2] + bounds[3]) / 2,
                      (bounds[4] + bounds[5]) / 2]

            # Calculate the maximum dimension of the bounding box
            max_dim = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])

            # Set the camera's position based on the selected view
            margin = 1.2  # 20% margin
            if view   == "ISO":
                camera.SetPosition(center[0] + max_dim * margin, center[1] + max_dim * margin, center[2] + max_dim * margin)
                camera.SetViewUp(0, 1, 0)
            elif view == "Right":
                camera.SetPosition(center[0], center[1], center[2] + max_dim * margin)
                camera.SetViewUp(0, 1, 0)
            elif view == "Front":
                camera.SetPosition(center[0] + max_dim * margin, center[1], center[2])
                camera.SetViewUp(0, 1, 0)
            elif view == "Top":
                camera.SetPosition(center[0], center[1] + max_dim * margin, center[2])
                camera.SetViewUp(1, 0, 0)

            camera.SetFocalPoint(center)
            camera.SetClippingRange(0.1, max_dim * margin * 3)

        # Reset the camera and apply the new view
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
