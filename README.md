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

**Day 15 — C-FIND Study Query Completed**

- Day 15 commit: `08aeb23 Add DICOM C-FIND study query`
- Next step: **Day 16 — PACS Query/Retrieve Integration**

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

#### Query SCU

- Use the Study Root Query/Retrieve Information Model
- Create and send Study-level C-FIND requests
- Search by Patient ID, Patient Name, and Study Date
- Process Pending C-FIND responses (`0xFF00`, `0xFF01`)
- Handle final success (`0x0000`)
- Treat zero-result queries as successful searches
- Display Study results in the Network tab

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
├── tools
│   └── find_scp.py
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
| 14.5 | UI Tab Refactoring                    | Completed |
|   15 | C-FIND Study Query                    | Completed |
|   16 | PACS Query/Retrieve Integration       |  Planned  |

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

## Day 14.5 — UI Tab Refactoring

As the toolkit gained more viewer, metadata, and DICOM networking features, the control panel became increasingly crowded.

The user interface was refactored using `QTabWidget` to separate the controls into three functional areas:

- **Viewer** — DICOM loading, PNG export, anonymization, zoom, Window/Level, pixel/HU inspection, distance measurement, and ROI measurement
- **Metadata** — DICOM metadata display and metadata search
- **Network** — AE configuration, C-ECHO, C-STORE SCU, and Storage SCP controls

The application now follows the following UI structure:

```text
PACS DICOM Toolkit
|
+-- Image View
|
+-- Control Tabs
    |
    +-- Viewer
    |   +-- File operations
    |   +-- View controls
    |   +-- Window / Level
    |   +-- Pixel / HU
    |   +-- Distance
    |   +-- ROI
    |
    +-- Metadata
    |   +-- DICOM metadata
    |   +-- Metadata search
    |
    +-- Network
        +-- Local / Remote AE configuration
        +-- C-ECHO
        +-- C-STORE Send
        +-- Storage SCP
```

This refactoring improves usability and separates the UI by responsibility without changing the existing DICOM processing or networking logic.

Regression testing confirmed that the existing Viewer, Metadata, C-ECHO, C-STORE, and Storage SCP functionality continued to work after the UI refactoring.

The new tab-based structure also prepares the application for upcoming PACS Query/Retrieve features.

## Day 15 — C-FIND Study Query

Day 15 introduced DICOM Query functionality using C-FIND.

PACS-DICOM-Toolkit can now query a remote Query/Retrieve SCP for studies using the DICOM Study Root Query/Retrieve Information Model.

```text
PACS-DICOM-Toolkit
    C-FIND SCU
        |
        | Association Request
        v
Remote Query/Retrieve SCP
        |
        | C-FIND Request
        | QueryRetrieveLevel = STUDY
        v
Study Search
        |
        | 0xFF00 Pending + Study Dataset
        | 0xFF00 Pending + Study Dataset
        | ...
        | 0x0000 Final Success
        v
PACS-DICOM-Toolkit
```
The Study-level query supports the following matching keys:

- Patient ID
- Patient Name
- Study Date

The query also requests the following return keys:

- Patient ID
- Patient Name
- Study Date
- Study Description
- Study Instance UID
- Accession Number
- Modalities in Study

A key concept learned during C-FIND implementation was the difference between matching keys and return keys.

```text
Matching Key
PatientID = "TEST001"
        |
        v
Search for studies belonging to TEST001

Return Key
StudyDescription = ""
StudyInstanceUID = ""
ModalitiesInStudy = ""
        |
        v
Request these values from the Query/Retrieve SCP
```

## Disclaimer

This project is intended for DICOM and PACS education and portfolio development.

It is not intended for medical diagnosis or production clinical use.
