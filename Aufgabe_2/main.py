import mbsModel
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

# Create a Qt application
app = QApplication(sys.argv)

# Create an empty model
myModel = mbsModel.mbsModel()

# Check if an FDD file path is provided
if len(sys.argv) > 1:
    # Read FDD file path from input arguments
    fdd_path = Path(sys.argv[1])
    if not myModel.importFddFile(fdd_path):
        sys.exit("Failed to load FDD file!")

    # Create path for solver input file (fds)
    fds_path = fdd_path.with_suffix(".fds")
    myModel.exportFdsFile(fds_path)

    # Create path for model database file (json)
    json_path = fdd_path.with_suffix(".json")
    myModel.saveDatabase(json_path)

    # Load database into a new model
    newModel = mbsModel.mbsModel()
    newModel.loadDatabase(json_path)
else:
    newModel = myModel

# Create the main window and pass the model to it
main_window = MainWindow(model=newModel)
main_window.show()

# Start the Qt event loop
sys.exit(app.exec())
