from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMenuBar, QFileDialog, QMessageBox
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.all import vtkInteractorStyleTrackballCamera, vtkCamera
from vtkmodules.vtkRenderingCore import vtkRenderer
import mbsModel


class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()

        # Initialize the model and set up the renderer
        self.model = model
        self.renderer = vtkRenderer()

        # Set up the main window properties
        self.setWindowTitle("pyFreeDyn Viewer")
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
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close_app)

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load File", "", "JSON Files (*.json)")
        if file_name:
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

    def close_app(self):
        self.close()


##--------------------------------------------------------------------------------------------------------------------##
##      RENDER WINDOW ADJUSTMENT AND UPDATES TO RENDERER
##--------------------------------------------------------------------------------------------------------------------##
    def update_renderer(self):
        """Clear the renderer and display the updated model."""
        self.renderer.RemoveAllViewProps()  # Clear the current visualization
        self.model.showModel(self.renderer)  # Render the updated model

        # Adjust the camera to fit the new model
        self.fit_camera()

        self.vtk_render_window.Render()  # Refresh the VTK window

    def fit_camera(self):
        """Adjust the camera to fit the model in the render window."""
        # Set up the camera to fit the bounding box of the model
        camera = self.renderer.GetActiveCamera()

        # Get the bounds of the model in world coordinates
        bounds = self.renderer.ComputeVisiblePropBounds()

        if bounds:
            # Set the camera's position and focal point based on the model's bounds
            camera.SetFocalPoint((bounds[0] + bounds[1]) / 2,
                                 (bounds[2] + bounds[3]) / 2,
                                 (bounds[4] + bounds[5]) / 2)

            # Adjust the camera's view angle and position
            offset = 50.0
            camera.SetPosition(bounds[1] + offset, bounds[3] + offset, bounds[5] + offset)  # move camera to isometric view
            camera.SetViewUp(0, 1, 0)  # Set the camera's "up" direction
            camera.Zoom(1)  # Zoom out a bit to avoid being too zoomed in

        # Update the view
        self.vtk_render_window.Render()
