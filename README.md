# PACS-DICOM-Toolkit

> A step-by-step DICOM viewer and PACS networking project built with Python, PyQt5, and pydicom.

## Project Overview

PACS-DICOM-Toolkit is a learning and portfolio project focused on medical imaging software development.

The project begins with a basic DICOM viewer and gradually expands to image interaction, measurement tools, anonymization, and PACS network communication.

### Project Goals

- Understand the DICOM file structure
- Display and process medical images
- Read and search DICOM metadata
- Protect patient information through anonymization
- Implement medical image measurement tools
- Understand PACS and DICOM network communication
- Build a practical medical imaging software portfolio

## Current Status

**Day 12 — DICOM Network and C-ECHO Verification Completed**

- Repository: `milanpm/PACS-DICOM-Toolkit`
- Branch: `main`
- Next step: **Day 13 — C-STORE DICOM Send**

## Features

### DICOM Viewer

- Open and display DICOM files
- Display DICOM pixel data
- Display essential metadata
- Search metadata by tag name or keyword
- Export the displayed image as a PNG file

### Image Interaction

- Zoom in and out using the mouse wheel
- Pan the image using left mouse drag
- Fit the image to the viewer
- Reset the current view
- Display the current zoom percentage

### Window and Level Controls

- Adjust Window Center and Window Width
- Enter Window values using spin boxes
- Adjust Window settings using right mouse drag
- Restore the original Window settings

### Pixel and HU Inspector

- Display the current X and Y coordinates
- Display the raw pixel value
- Display the HU value
- Apply Rescale Slope and Rescale Intercept

### Distance Measurement

- Select two measurement points with `Shift + Left Click`
- Calculate the physical distance in millimeters when Pixel Spacing is available
- Calculate the distance in pixels when Pixel Spacing is unavailable
- Display measurement points and a measurement line

### ROI Measurement

- Select a rectangular ROI with `Ctrl + Left Drag`
- Display the ROI width and height
- Calculate the mean HU value
- Calculate the minimum HU value
- Calculate the maximum HU value
- Clear the ROI overlay and measurement results

### DICOM Anonymization

- Remove or replace patient-identifying information
- Save the anonymized dataset as a separate DICOM file
- Preserve the original DICOM file

### DICOM Network

- Configure Local and Remote AE Titles
- Configure the Remote IP address and port
- Establish a DICOM Association
- Send a C-ECHO Verification request
- Display success and failure results
- Release the Association after communication
- Handle network and configuration errors

## Viewer Controls

| Action                         | Control                  |
| ------------------------------ | ------------------------ |
| Zoom in and out                | Mouse wheel              |
| Pan                            | Left mouse drag          |
| Adjust Window Center and Width | Right mouse drag         |
| Inspect Pixel and HU values    | Mouse movement           |
| Measure distance               | Shift + Left Click twice |
| Select rectangular ROI         | Ctrl + Left Drag         |
| Reset the view                 | Reset View button        |
| Reset Window settings          | Reset Window button      |
| Clear the ROI                  | Clear ROI button         |

## Project Structure

```text
PACS-DICOM-Toolkit
├── README.md
├── requirements.txt
├── samples
├── src
│   ├── main.py
│   ├── image_view.py
│   ├── dicom_loader.py
│   ├── dicom_network.py
│   ├── anonymizer.py
│   └── windowing.py
└── tests
```

### Main Modules

| File                   | Responsibility                                                 |
| ---------------------- | -------------------------------------------------------------- |
| `src/main.py`          | Manages the application UI and overall viewer behavior         |
| `src/image_view.py`    | Manages zoom, pan, Window adjustment, and measurement overlays |
| `src/dicom_loader.py`  | Loads DICOM files and extracts metadata                        |
| `src/dicom_network.py` | Manages DICOM Association and C-ECHO Verification              |
| `src/anonymizer.py`    | Anonymizes patient information                                 |
| `src/windowing.py`     | Applies Window Center and Window Width transformations         |

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/milanpm/PACS-DICOM-Toolkit.git
cd PACS-DICOM-Toolkit
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

```bash
python src/main.py
```

After launching the application, click `Open DICOM` and select a DICOM file.

> Do not upload real patient DICOM files containing personal information to GitHub.

## Dependencies

- Python
- PyQt5
- pydicom
- NumPy
- Pillow
- pynetdicom

## Learning Roadmap

|  Day | Topic                                 |  Status   |
| ---: | ------------------------------------- | :-------: |
|    1 | Basic DICOM Viewer                    | Completed |
|    2 | DICOM Anonymization and Metadata      | Completed |
|    3 | PNG Export                            | Completed |
|    4 | Metadata Search                       | Completed |
|  5–6 | Zoom and Pan                          | Completed |
|    7 | Window and Level Controls             | Completed |
|    8 | Pixel and HU Inspector                | Completed |
|    9 | Distance Measurement and Ruler        | Completed |
|   10 | Rectangular ROI Measurement           | Completed |
|   11 | DICOM Viewer Refactoring              | Completed |
|   12 | DICOM Network and C-ECHO Verification | Completed |
|   13 | C-STORE DICOM Send                    |  Planned  |
|   14 | Storage SCP and DICOM Receive         |  Planned  |
|   15 | C-FIND Query                          |  Planned  |
|   16 | PACS Integration                      |  Planned  |

## Day 11 Refactoring

Day 11 focused on separating responsibilities without changing the existing viewer behavior.

The `DicomViewer` initialization process was simplified to the following sequence:

```python
self.initialize_state()
self.setup_ui()
self.connect_signals()
```

The responsibilities were separated as follows:

- `initialize_state()` initializes DICOM data and measurement state.
- `setup_ui()` creates and arranges the UI widgets.
- `connect_signals()` manages Signal–Slot connections.
- `clear_measurements()` resets distance and ROI measurement state.

This refactoring provides a cleaner foundation for adding DICOM network configuration and communication features.

## Next Step

### Day 13 — C-STORE DICOM Send

The next step will extend the network module with DICOM Storage SCU functionality.

Planned features:

- Select a DICOM file to send
- Request a Storage Presentation Context
- Establish an Association with a Storage SCP
- Send a C-STORE request
- Interpret the C-STORE response status
- Display transfer success or failure
- Release the Association after transmission

## Disclaimer

This project is intended for DICOM and PACS education and portfolio development.

It is not intended for medical diagnosis or production clinical use.
