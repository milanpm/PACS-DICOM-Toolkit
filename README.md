# PACS-DICOM-Toolkit

> A step-by-step DICOM viewer and PACS networking project built with Python, PyQt5, pydicom, and pynetdicom.

## Project Overview

PACS-DICOM-Toolkit is a learning and portfolio project focused on medical imaging software development.

The project begins with a basic DICOM viewer and gradually expands to image interaction, measurement tools, anonymization, DICOM network communication, and PACS integration.

### Project Goals

- Understand the DICOM file structure
- Display and process medical images
- Read and search DICOM metadata
- Protect patient information through anonymization
- Implement medical image measurement tools
- Understand DICOM network services and PACS communication
- Implement DICOM Storage SCU and SCP functionality
- Progress toward practical PACS Query/Retrieve workflows
- Build a practical medical imaging software portfolio

## Current Status

**Day 14 — Storage SCP and DICOM Receive Completed**

- Repository: `milanpm/PACS-DICOM-Toolkit`
- Branch: `main`
- Latest Day 14 commit: `7f751f0 Add DICOM Storage SCP receive`
- Next step: **Day 15 — C-FIND Query**

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

#### Verification SCU

- Configure Local and Remote AE Titles
- Configure the Remote IP address and port
- Establish a DICOM Association
- Send a C-ECHO Verification request
- Interpret C-ECHO response status
- Display connection success and failure results
- Release the Association after communication
- Handle network and configuration errors

#### Storage SCU

- Send the currently opened DICOM file using C-STORE
- Request a Storage Presentation Context based on the SOP Class UID
- Establish an Association with a remote Storage SCP
- Interpret the C-STORE response status
- Display C-STORE success and failure results
- Release the Association after transmission

#### Storage SCP

- Start and stop a local Storage SCP from the application
- Configure the local Storage SCP listening port
- Use the configured Local AE Title
- Support DICOM Storage Presentation Contexts
- Accept incoming DICOM Associations
- Handle incoming C-STORE requests using `EVT_C_STORE`
- Preserve DICOM File Meta information
- Save received DICOM datasets locally
- Use the SOP Instance UID as the received filename
- Return a successful C-STORE response after saving
- Safely shut down the Storage SCP when the application closes

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
├── received
├── src
│   ├── main.py
│   ├── image_view.py
│   ├── dicom_loader.py
│   ├── dicom_network.py
│   ├── anonymizer.py
│   └── windowing.py
└── tests
```

The `received/` directory is used by the Storage SCP to store incoming DICOM objects.

Received DICOM files are excluded from Git tracking to prevent test or patient image data from being accidentally committed.

### Main Modules

| File                   | Responsibility                                                  |
| ---------------------- | --------------------------------------------------------------- |
| `src/main.py`          | Manages the application UI and overall viewer behavior          |
| `src/image_view.py`    | Manages zoom, pan, Window adjustment, and measurement overlays  |
| `src/dicom_loader.py`  | Loads DICOM files and extracts metadata                         |
| `src/dicom_network.py` | Manages DICOM Association, C-ECHO, C-STORE SCU, and Storage SCP |
| `src/anonymizer.py`    | Anonymizes patient information                                  |
| `src/windowing.py`     | Applies Window Center and Window Width transformations          |

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

## DICOM Network Testing

### C-ECHO

A remote Verification SCP can be used to verify DICOM network connectivity.

Example configuration:

```text
Local AE Title:  PACS_TOOLKIT
Remote AE Title: ANY-SCP
Remote IP:       127.0.0.1
Remote Port:     11112
```

### C-STORE Send

The currently opened DICOM object can be sent from PACS-DICOM-Toolkit to an external Storage SCP.

```text
PACS-DICOM-Toolkit
    Storage SCU
        |
        | C-STORE
        v
External Storage SCP
```

### C-STORE Receive

Start the Storage SCP in PACS-DICOM-Toolkit using:

```text
AE Title: PACS_TOOLKIT
Port:     11113
```

An external Storage SCU can then send a DICOM object to the toolkit.

Example using `storescu`:

```bash
storescu -aet TEST_SCU -aec PACS_TOOLKIT \
  127.0.0.1 11113 samples/test_image.dcm
```

Received DICOM objects are stored in:

```text
received/<SOPInstanceUID>.dcm
```

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
|   13 | C-STORE DICOM Send                    | Completed |
|   14 | Storage SCP and DICOM Receive         | Completed |
|   15 | C-FIND Query                          |  Planned  |
|   16 | PACS Integration                      |  Planned  |

## Day 11 — Viewer Refactoring

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

This refactoring provides a cleaner foundation for DICOM network configuration and communication features.

## Day 12 — C-ECHO Verification

Day 12 introduced DICOM network communication to PACS-DICOM-Toolkit.

The toolkit can establish a DICOM Association with a remote Application Entity and send a C-ECHO request to verify network connectivity.

```text
PACS-DICOM-Toolkit
 Verification SCU
        |
        | Association
        | C-ECHO
        v
Remote Verification SCP
```

A successful verification returns:

```text
C-ECHO Success: 0x0000
```

## Day 13 — C-STORE DICOM Send

Day 13 extended the DICOM network module with Storage SCU functionality.

The currently opened DICOM file can be sent to a remote Storage SCP using a C-STORE request.

```text
PACS-DICOM-Toolkit
    Storage SCU
        |
        | Association Request
        v
Remote Storage SCP
        |
        | Association Accept
        v
PACS-DICOM-Toolkit
        |
        | C-STORE Request
        v
Remote Storage SCP
        |
        | C-STORE Response
        v
0x0000 Success
```

## Day 14 — Storage SCP and DICOM Receive

Day 14 extended the DICOM network module with Storage SCP functionality.

PACS-DICOM-Toolkit can now receive DICOM objects from an external Storage SCU using C-STORE and save the received datasets to the local `received/` directory.

```text
External Storage SCU
        |
        | Association Request
        v
PACS-DICOM-Toolkit
     Storage SCP
        |
        | Association Accept
        v
External Storage SCU
        |
        | C-STORE Request
        v
PACS-DICOM-Toolkit
        |
        | EVT_C_STORE
        v
Save DICOM Dataset
        |
        v
received/<SOPInstanceUID>.dcm
        |
        | C-STORE Response
        v
0x0000 Success
```

Implemented features:

- Start and stop the local Storage SCP from the application
- Configure the Storage SCP listening port
- Use the Local AE Title for the Storage SCP
- Support DICOM Storage Presentation Contexts
- Accept incoming DICOM Associations
- Handle incoming C-STORE requests using `EVT_C_STORE`
- Preserve DICOM File Meta information
- Save received datasets using the SOP Instance UID as the filename
- Store received DICOM files in the `received/` directory
- Safely shut down the Storage SCP when the application closes

The Storage SCP was tested using an external `storescu` client:

```bash
storescu -aet TEST_SCU -aec PACS_TOOLKIT \
  127.0.0.1 11113 samples/test_image.dcm
```

The received DICOM object was successfully saved and reopened using pydicom, confirming that the received dataset remained a valid DICOM file.

## Next Step

### Day 15 — C-FIND Query

The next step will introduce DICOM Query functionality using C-FIND.

Planned features:

- Understand the DICOM Query/Retrieve service model
- Configure a Query/Retrieve SCP connection
- Create a C-FIND query dataset
- Send C-FIND requests
- Receive and process C-FIND responses
- Search studies using patient and study information
- Display query results in the application

This will extend PACS-DICOM-Toolkit from DICOM storage communication toward practical PACS Query/Retrieve workflows.

## Disclaimer

This project is intended for DICOM and PACS education and portfolio development.

It is not intended for medical diagnosis or production clinical use.
