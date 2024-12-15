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
        file_name, _ = QFileDialog.getOpenFileName(self, "Load File", "", "All Files (*.*)")
        if file_name:
            QMessageBox.information(self, "Load File", f"Loaded file: {file_name}")
            # TODO: Add code to load your model data

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*.*)")
        if file_name:
            QMessageBox.information(self, "Save File", f"Saved file: {file_name}")
            # TODO: Add code to save your model data

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

 
