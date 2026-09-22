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

**Day 21 — Network Cancellation and Timeout Handling Completed**

- Added cooperative cancellation using `threading.Event`
- Added a `cancelled` signal to `NetworkWorker`
- Added the `Cancel Operation` button to the Network tab
- Disabled the cancel button after the first cancellation request
- Added cancellation support to all seven DICOM SCU operations
- Added cancellation checks after Association and during multi-response operations
- Aborted active Associations safely when cancellation was detected
- Added a five-second TCP connection timeout
- Preserved ACSE, DIMSE, and network timeout settings
- Distinguished user cancellation from connection failure or timeout
- Restored network controls automatically after cancellation
- Verified C-ECHO cancellation during a blocked connection attempt
- Reduced observed cancellation completion from approximately 18 seconds to 1–2 seconds
- Verified connection failure and timeout reporting
- Verified successful C-ECHO regression result `0x0000`
- Next step: **Day 22 — Network Worker Lifecycle Refactoring**

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
- Create Study-level C-FIND requests
- Search studies by Patient ID, Patient Name, and Study Date
- Use Study Instance UID to search related Series
- Create Series-level C-FIND requests
- Return Series Number, Description, Modality, and Instance count
- Use Study and Series Instance UIDs to search individual Instances
- Create Image-level C-FIND requests for SOP Instances
- Return SOP Class UID, SOP Instance UID, and Instance Number
- Process Pending C-FIND responses (`0xFF00`, `0xFF01`)
- Handle final success (`0x0000`)
- Treat zero-result queries as successful searches
- Display Study, Series, and Instance results in the Network tab

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
|   16 | PACS Query/Retrieve Integration       | Completed |
|   17 | DICOM Retrieval with C-MOVE           | Completed |
|   18 | DICOM Retrieval with C-GET            | Completed |
|   19 | Network UI and Background Operations  | Completed |
|   20 | Network Validation, Logging, and Control | Completed |
| 20.5 | Network Validation Refactoring          | Completed |
|   21 | Network Cancellation and Timeout Handling | Completed |

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

## Day 16 — PACS Query/Retrieve Integration

Day 16 expanded the Study-level C-FIND implementation into a hierarchical PACS Query/Retrieve workflow.

The application can now navigate the DICOM information model from a Study to its Series and individual SOP Instances.

```text
Study C-FIND
    |
    | StudyInstanceUID
    v
Series C-FIND
    |
    | StudyInstanceUID
    | SeriesInstanceUID
    v
Image-level C-FIND
    |
    | SOPClassUID
    | SOPInstanceUID
    | InstanceNumber
    v
Individual DICOM Instances
```

### Study Query

The Study query uses the following Query/Retrieve level:

```python
query.QueryRetrieveLevel = "STUDY"
```

Patient ID, Patient Name, and Study Date are used as matching keys. The returned Study Instance UID identifies the selected study and becomes the matching key for the Series query.

### Series Query

The Series query uses the selected Study Instance UID:

```python
query.QueryRetrieveLevel = "SERIES"
query.StudyInstanceUID = study_instance_uid
```

The following Series information is requested:

- Series Instance UID
- Series Number
- Series Description
- Modality
- Number of related Instances

### Instance Query

Individual SOP Instances are queried using the DICOM `IMAGE` Query/Retrieve level:

```python
query.QueryRetrieveLevel = "IMAGE"
query.StudyInstanceUID = study_instance_uid
query.SeriesInstanceUID = series_instance_uid
```

Although the application function is named `find_instances()`, the standard DICOM Query/Retrieve level is `IMAGE`.

The query returns:

- SOP Class UID
- SOP Instance UID
- Instance Number

### Hierarchical Matching Keys

| Query Level | Matching Keys |
| ----------- | ------------- |
| Study | Patient ID, Patient Name, Study Date |
| Series | Study Instance UID |
| Image | Study Instance UID, Series Instance UID |

Each query result supplies the UID required by the next level.

```text
StudyInstanceUID
        |
        v
SeriesInstanceUID
        |
        v
SOPInstanceUID
```

### Network Tab Integration

The Network tab now supports the complete hierarchical query workflow:

1. Search for Studies.
2. Use the returned Study Instance UID to search for Series.
3. Select a Series Instance UID.
4. Search for individual Instances.

When a Study query returns exactly one result, its Study Instance UID is automatically copied into the Series Query field. The same behavior is used for a single Series result.

A shared Query Results area displays Study, Series, or Instance results without adding multiple result panels to the Network tab.

### Test Query/Retrieve SCP

The test C-FIND SCP now supports three Query/Retrieve levels:

- `STUDY`
- `SERIES`
- `IMAGE`

The test hierarchy contains one Study, two Series, and four Instances.

```text
Test Study
├── CT Axial
│   ├── Instance 1
│   ├── Instance 2
│   └── Instance 3
└── CT Scout
    └── Instance 1
```

Testing confirmed:

- One Study result
- Two Series results
- Three CT Axial Instance results
- One CT Scout Instance result
- Successful zero-result handling for unknown Study and Series UIDs

The UIDs returned by this hierarchy are used by Day 17 C-MOVE requests to select the Study or Series to retrieve.

## Day 17 — DICOM Retrieval with C-MOVE

Day 17 introduced DICOM retrieval using C-MOVE.

The application can now request all DICOM instances belonging to a selected Study or Series. The remote Query/Retrieve SCP sends the matching instances to the existing local Storage SCP using separate C-STORE sub-operations.

```text
PACS-DICOM-Toolkit
    C-MOVE SCU
        |
        | C-MOVE Request
        | Move Destination = PACS_TOOLKIT
        v
Remote Query/Retrieve SCP
    C-MOVE SCP / C-STORE SCU
        |
        | New DICOM Association
        | C-STORE Requests
        v
Local Storage SCP
    AE Title: PACS_TOOLKIT
    Port: 11113
        |
        v
received/
```

Unlike C-GET, C-MOVE does not return DICOM datasets over the original Query/Retrieve association. The remote C-MOVE SCP opens a separate association with the configured destination Storage SCP and transfers the matching instances using C-STORE.

### Study Retrieval

A Study-level C-MOVE request uses the selected Study Instance UID:

```python
identifier = Dataset()
identifier.QueryRetrieveLevel = "STUDY"
identifier.StudyInstanceUID = study_instance_uid
```

The request retrieves every matching SOP Instance in the selected Study.

```python
responses = association.send_c_move(
    identifier,
    move_destination_ae_title,
    StudyRootQueryRetrieveInformationModelMove,
)
```

### Series Retrieval

A Series-level C-MOVE request requires both the Study Instance UID and Series Instance UID:

```python
identifier = Dataset()
identifier.QueryRetrieveLevel = "SERIES"
identifier.StudyInstanceUID = study_instance_uid
identifier.SeriesInstanceUID = series_instance_uid
```

This allows the application to retrieve only the DICOM instances belonging to the selected Series.

### Move Destination

The C-MOVE SCP must know the network address of the destination Storage SCP before it can transfer any DICOM instances.

The local test configuration uses:

| Setting | Value |
| ------- | ----- |
| Move Destination AE Title | `PACS_TOOLKIT` |
| Storage SCP IP | `127.0.0.1` |
| Storage SCP Port | `11113` |
| Storage Directory | `received/` |

If the Move Destination AE Title is unknown, the C-MOVE SCP returns:

```text
0xA801 — Move Destination unknown
```

### C-MOVE Response Handling

The application monitors the number of remaining, completed, failed, and warning sub-operations returned with C-MOVE responses.

```python
status.NumberOfRemainingSuboperations
status.NumberOfCompletedSuboperations
status.NumberOfFailedSuboperations
status.NumberOfWarningSuboperations
```

The main response statuses handled by the application include:

| Status | Meaning |
| ------ | ------- |
| `0xFF00` | Pending |
| `0xFF01` | Pending with optional key warning |
| `0x0000` | Success |
| `0xB000` | Completed with warnings |
| `0xA801` | Move Destination unknown |

### Network Tab Integration

The Network tab now provides two retrieval controls:

- `Retrieve Study (C-MOVE)`
- `Retrieve Series (C-MOVE)`

The Study retrieval button uses the Study Instance UID field. The Series retrieval button uses both the Study Instance UID and Series Instance UID fields.

The local Storage SCP must be running before a retrieval request is sent. If it is not running, the application displays:

```text
Start the local Storage SCP before C-MOVE.
```

The Query Results area displays the retrieval level and sub-operation counts.

```text
C-MOVE completed: 4 completed, 0 failed, 0 warning.

Query Retrieve Level: STUDY
Completed: 4
Failed: 0
Warnings: 0
Remaining: 0
Storage Directory: received/
```

### Test Query/Retrieve SCP

The test Query/Retrieve SCP now supports:

- Hierarchical C-FIND at the `STUDY`, `SERIES`, and `IMAGE` levels
- C-MOVE at the `STUDY` and `SERIES` levels
- C-STORE transmission to `PACS_TOOLKIT:11113`

A sample DICOM dataset is copied and assigned the test Study, Series, and SOP Instance UIDs before transmission.

Testing confirmed:

- Study C-MOVE retrieved four DICOM instances
- First Series C-MOVE retrieved three DICOM instances
- Second Series C-MOVE retrieved one DICOM instance
- Unknown Series UID completed successfully with zero matching instances
- Unknown Move Destination returned `0xA801`
- Storage SCP received and saved the transferred files in `received/`
- C-MOVE was blocked in the UI when the local Storage SCP was not running

## Day 18 — DICOM Retrieval with C-GET

Day 18 introduced DICOM retrieval using C-GET.

Like C-MOVE, C-GET retrieves matching DICOM instances using Study Root Query/Retrieve. However, C-GET returns the instances through C-STORE sub-operations performed over the same Association as the original C-GET request.

```text
PACS-DICOM-Toolkit
    C-GET SCU / C-STORE SCP
        |
        | C-GET Request
        | QueryRetrieveLevel = STUDY or SERIES
        v
Remote Query/Retrieve SCP
    C-GET SCP / C-STORE SCU
        |
        | C-STORE Requests
        | Same Association
        v
PACS-DICOM-Toolkit
        |
        v
received/
```

Unlike C-MOVE, C-GET does not require a Move Destination AE Title, a separate Storage SCP port, or a second Association.

### Study Retrieval

A Study-level C-GET request uses the selected Study Instance UID:

```python
identifier = Dataset()
identifier.QueryRetrieveLevel = "STUDY"
identifier.StudyInstanceUID = study_instance_uid
```

The request is sent using the Study Root Query/Retrieve Information Model:

```python
responses = association.send_c_get(
    identifier,
    StudyRootQueryRetrieveInformationModelGet,
)
```

The test Study contains four DICOM instances distributed across two Series.

### Series Retrieval

A Series-level request requires both the Study Instance UID and Series Instance UID:

```python
identifier = Dataset()
identifier.QueryRetrieveLevel = "SERIES"
identifier.StudyInstanceUID = study_instance_uid
identifier.SeriesInstanceUID = series_instance_uid
```

This allows the application to retrieve only the instances belonging to the selected Series.

### Same-Association C-STORE

C-GET uses the original Association for both the C-GET request and the returned C-STORE sub-operations.

The application binds the existing Storage handler directly to the C-GET Association:

```python
handlers = [
    (
        evt.EVT_C_STORE,
        handle_store,
        [storage_dir],
    ),
]
```

```python
association = ae.associate(
    remote_ip,
    remote_port,
    ae_title=remote_ae_title,
    ext_neg=[storage_role],
    evt_handlers=handlers,
)
```

The received datasets are saved using their SOP Instance UIDs:

```text
received/<SOPInstanceUID>.dcm
```

The standalone Storage SCP does not need to be running for C-GET.

### Storage Role Negotiation

The Association requestor normally acts as an SCU. During C-GET, however, the requestor must also act as a Storage SCP to receive the returned instances.

The C-GET SCU requests the Storage SCP role:

```python
storage_role = build_role(
    SecondaryCaptureImageStorage,
    scu_role=False,
    scp_role=True,
)
```

The test C-GET SCP accepts the requestor's Storage SCP role:

```python
ae.add_supported_context(
    SecondaryCaptureImageStorage,
    scu_role=False,
    scp_role=True,
)
```

For the test dataset, only the required Secondary Capture Image Storage context is proposed. This avoids attempting to add all 170 available Storage Presentation Contexts to an Association that can contain at most 128 Presentation Contexts.

### Troubleshooting `0xA702`

The initial C-GET test matched four instances but failed all four C-STORE sub-operations:

```text
Success: False
Completed: 0
Failed: 4
C-GET failed: 0xA702
```

The status means:

```text
0xA702 — Unable to perform sub-operations
```

The cause was reversed Storage role negotiation on the test C-GET SCP. It did not accept the Association requestor's C-STORE SCP role.

After changing the accepted requestor role to:

```python
scu_role=False
scp_role=True
```

the Study C-GET completed successfully:

```text
Completed: 4
Failed: 0
Warning: 0
```

This demonstrated that matching Query/Retrieve records and transferring their DICOM datasets are separate stages. A query can match instances while the C-STORE sub-operations still fail because of Association negotiation.

### C-GET Response Handling

The application monitors the same sub-operation counters used for C-MOVE:

```python
status.NumberOfRemainingSuboperations
status.NumberOfCompletedSuboperations
status.NumberOfFailedSuboperations
status.NumberOfWarningSuboperations
```

The primary C-GET statuses handled by the application include:

| Status | Meaning |
| ------ | ------- |
| `0xFF00` | Pending |
| `0xFF01` | Pending with optional key warning |
| `0x0000` | Success |
| `0xB000` | Completed with warnings |
| `0xA702` | Unable to perform sub-operations |

### C-MOVE and C-GET Comparison

| Characteristic | C-MOVE | C-GET |
| -------------- | ------ | ----- |
| Retrieval request | C-MOVE | C-GET |
| DICOM transfer | C-STORE | C-STORE |
| C-STORE Association | Separate Association | Same Association |
| Move Destination AE Title | Required | Not required |
| Destination address lookup | Required | Not required |
| Standalone Storage SCP | Required | Not required |
| Requestor Storage role negotiation | Not required | Required |
| Typical use | PACS-to-PACS routing | Direct retrieval by the requesting application |

### Network Tab Integration

The Network tab now provides four retrieval controls:

- `Retrieve Study (C-MOVE)`
- `Retrieve Study (C-GET)`
- `Retrieve Series (C-MOVE)`
- `Retrieve Series (C-GET)`

C-MOVE remains dependent on the separately running local Storage SCP. C-GET can run immediately because its Storage handler is attached to the C-GET Association.

The Query Results area displays the retrieval method, query level, storage location, and sub-operation counts.

```text
C-GET completed: 4 completed, 0 failed, 0 warning.

Query Retrieve Level: STUDY
Completed: 4
Failed: 0
Warnings: 0
Remaining: 0
Storage Directory: received/
Association: Same association as C-GET
```

## Day 19 — Network UI Refactoring and Background Operations

Day 19 reorganized the DICOM Network tab and moved blocking
network operations away from the PyQt GUI thread.

The DICOM networking functions were already working correctly,
but C-FIND, C-MOVE, and C-GET could block the user interface while
waiting for Association responses or transfer sub-operations.

### Network Tab Refactoring

The original Network tab used one long `QFormLayout`. As more
DICOM services were added, the controls became difficult to
navigate.

The Network tab is now divided into functional groups:

- PACS Connection
- Local Storage SCP
- Study Query
- Hierarchy Selection
- Retrieve
- Status and Results

A `QScrollArea` keeps every control accessible when the
application window is smaller than the complete Network panel.

The Network controls also use clearer labels, stronger text
contrast, and visually distinct disabled buttons.

### Background Network Worker

A reusable `NetworkWorker` was added in:

```text
src/network_worker.py
```

### Test Query/Retrieve SCP

The local Query/Retrieve SCP now supports:

- Hierarchical C-FIND at the `STUDY`, `SERIES`, and `IMAGE` levels
- C-MOVE at the `STUDY` and `SERIES` levels
- C-GET at the `STUDY` and `SERIES` levels
- C-STORE transmission over separate and same Associations

Testing confirmed:

- Study C-GET retrieved four DICOM instances
- First Series C-GET retrieved three DICOM instances
- Second Series C-GET retrieved one DICOM instance
- Unknown Study UID completed successfully with zero matching instances
- Unknown Series UID completed successfully with zero matching instances
- Received DICOM files were saved in `received/`
- C-GET succeeded without starting the standalone Storage SCP
- Correct Storage role negotiation resolved the initial `0xA702` failure

## Day 20 — Network Validation, Logging, and Operation Control

Day 20 improved the reliability and usability of the DICOM
Network tab by validating user input before starting an
Association, recording timestamped network events, and preventing
conflicting UI actions while an operation is running.

### PACS Connection Validation

The Network tab now validates and normalizes the connection
settings before starting C-ECHO, C-STORE, C-FIND, C-MOVE, or
C-GET.

The validation checks include:

- Local AE Title is not empty
- Remote AE Title is not empty
- AE Titles contain no more than 16 characters
- Remote IP is a valid IPv4 or IPv6 address
- Remote Port is between `1` and `65535`
- Storage SCP Port is between `1` and `65535`

Invalid settings are rejected before creating a
`NetworkWorker` or attempting a DICOM Association.

### Query and Retrieve Input Validation

Operation-specific values are also validated before a request is
started.

- Study Date must use the `YYYYMMDD` format
- Study Date must represent a valid calendar date
- Series C-FIND requires a valid Study Instance UID
- Instance C-FIND requires valid Study and Series Instance UIDs
- Study C-MOVE and C-GET require a valid Study Instance UID
- Series C-MOVE and C-GET require valid Study and Series Instance UIDs

Validation failures are displayed in the status area, recorded in
the network log, and shown in a warning dialog.

### Timestamped Network Log

A dedicated Network Log area records operation events using the
local time in `HH:mm:ss` format.

```text
[13:52:10] VALIDATION: Local AE Title is required.
[13:52:24] Starting Storage SCP (AE: PACS_TOOLKIT, Port: 11113)
[13:52:24] SUCCESS: Storage SCP running on port 11113
[13:53:06] Stopping Storage SCP...
[13:53:06] SUCCESS: Storage SCP stopped
```

The log records:

- Validation failures
- Worker progress messages
- Successful results
- Failed results
- Unexpected worker exceptions
- Storage SCP startup and shutdown events

### Network Operation Control

Network configuration fields, query inputs, and action buttons are
disabled while a background network operation is running. This
prevents duplicate requests and configuration changes during an
active Association.

After the worker finishes, the controls are restored according to
the current application state:

- C-STORE is enabled only when a DICOM file is loaded
- Start Storage SCP is enabled only when the SCP is stopped
- Stop Storage SCP is enabled only when the SCP is running
- Local AE Title and Storage SCP Port remain locked while the SCP
  is running

The GUI remains responsive because blocking DICOM operations
continue to run through `NetworkWorker` and `QThread`.

## Day 20.5 — Network Validation Refactoring

Day 20.5 reorganized the validation code introduced on Day 20.
The goal was to improve readability and maintainability without
changing the application's visible behavior or DICOM network
operations.

### Problem

The `DicomViewer` class in `main.py` handled multiple
responsibilities:

- Reading values from PyQt5 widgets
- Validating AE Titles, IP addresses, ports, dates, and UIDs
- Displaying validation errors
- Recording network logs
- Starting DICOM network operations

As the application gained more features, keeping validation rules
inside the main window class made the file longer and more
difficult to modify safely.

### Validation Module

Reusable validation rules were moved to the new
`network_validation.py` module.

The module now provides:

- `validate_ae_title()` for DICOM AE Title validation
- `validate_port()` for TCP port validation
- `validate_ip_address()` for IPv4 and IPv6 validation
- `validate_network_connection()` for PACS connection settings
- `validate_storage_scp()` for local Storage SCP settings
- `validate_study_date_value()` for DICOM Study Date validation
- `validate_dicom_uid()` for required DICOM UID validation

A dedicated `ValidationError` exception carries both a
user-friendly title and a detailed error message.

### Separation of Responsibilities

The responsibilities are now divided as follows:

| Module | Responsibility |
| ------ | -------------- |
| `main.py` | Reads UI values and displays validation errors |
| `network_validation.py` | Validates and normalizes input values |
| `dicom_network.py` | Performs DICOM network communication |
| `network_worker.py` | Runs blocking operations outside the GUI thread |

The wrapper methods in `DicomViewer` preserve the existing return
behavior expected by C-ECHO, C-STORE, C-FIND, C-MOVE, C-GET, and
Storage SCP operations.

### Verification

The refactoring was verified with independent validation checks
and GUI regression testing.

Testing confirmed:

- Valid PACS connection settings are normalized and accepted
- Multiple invalid connection settings are reported together
- Valid Storage SCP settings are accepted
- Invalid Study Date formats and calendar dates are rejected
- Valid DICOM UIDs are accepted
- Invalid and missing DICOM UIDs are rejected
- Invalid UID checks do not print unnecessary `pydicom` warnings
- The application starts normally after the refactoring
- Existing validation messages appear in the status area and log
- Network UI behavior remains unchanged

## Day 21 — Network Cancellation and Timeout Handling

Day 21 added cooperative cancellation and explicit timeout handling
to the asynchronous DICOM network operations.

The goal was to let the user request cancellation without forcibly
terminating a `QThread` or leaving a DICOM Association and network
resources in an unsafe state.

### Cooperative Cancellation

`NetworkWorker` now owns a thread-safe `threading.Event`.

When the user selects `Cancel Operation`, the GUI calls:

```python
self.network_worker.request_cancel()
```

The worker records the request by setting the Event. Network
operations receive `is_cancel_requested()` as a callback and check
it at safe interruption points.

This approach is cooperative cancellation. The worker thread is not
terminated forcibly.

### Cancellation Flow

The cancellation sequence is:

1. The user starts a DICOM network operation.
2. Network controls are disabled and the cancel button is enabled.
3. The operation runs in `NetworkWorker`.
4. The user selects `Cancel Operation`.
5. The worker records the cancellation request.
6. The network function detects the request.
7. An established Association is aborted safely.
8. The worker emits the `cancelled` signal.
9. The GUI records the cancellation and restores its controls.

The cancel button becomes disabled immediately after the first
request to prevent duplicate cancellation requests.

### Supported Operations

Cancellation support was added to all seven SCU operation paths:

- C-ECHO
- C-STORE
- Study C-FIND
- Series C-FIND
- Instance C-FIND
- C-MOVE
- C-GET

C-FIND, C-MOVE, and C-GET check for cancellation while processing
multiple responses. C-ECHO and C-STORE check after Association and
rely on their configured timeout when blocked inside a request.

### Association Cleanup

Normal operations use:

```python
association.release()
```

Cancelled operations use:

```python
association.abort()
```

`release()` performs a negotiated, normal Association shutdown.
`abort()` ends an Association when the current operation cannot
continue normally.

### Timeout Configuration

Each DICOM SCU now uses an explicit TCP connection timeout in
addition to the existing DICOM networking timeouts.

| Timeout | Purpose |
| ------- | ------- |
| `connection_timeout` | Limits the TCP connection attempt |
| `acse_timeout` | Limits Association control operations |
| `dimse_timeout` | Limits DIMSE response waiting |
| `network_timeout` | Limits network inactivity |

The TCP connection timeout is configured as:

```python
ae.connection_timeout = 5
```

Before this setting was added, `connection_timeout` was `None`, so
the operating system controlled how long a blocked TCP connection
attempt could wait.

### Status and Logging

Cancellation and connection failure or timeout are reported
separately.

Example cancellation log:

```text
[14:10:02] C-ECHO: Working...
[14:10:06] C-ECHO: Cancellation requested...
[14:10:07] CANCELLED: C-ECHO cancelled
```

Example connection failure or timeout log:

```text
[14:12:37] C-ECHO: Working...
[14:12:42] FAILED: DICOM Association failed or timed out.
```

### Verification

Testing confirmed:

- The `Cancel Operation` button is enabled only during an operation
- Duplicate cancellation requests are prevented
- C-ECHO cancellation is reported through the `cancelled` signal
- Network controls are restored after cancellation
- A blocked connection attempt respects the five-second connection timeout
- Observed cancellation completion improved from approximately
  18 seconds to 1–2 seconds
- Connection failure or timeout is reported without freezing the GUI
- A running test PACS still returns `C-ECHO Success: 0x0000`
- All Python source files pass compilation checks

## Disclaimer

This project is intended for DICOM and PACS education and portfolio development.

It is not intended for medical diagnosis or production clinical use.
