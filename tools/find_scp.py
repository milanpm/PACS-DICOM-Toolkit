"""
File Name: find_scp.py
Created Date: 2026-08-24
Modified Date: 2026-09-01
Author: Alex
Description:
    Provides a test DICOM Query/Retrieve SCP supporting hierarchical
    C-FIND, C-MOVE, and C-GET operations for local PACS integration
    testing.
"""

from copy import deepcopy
from pathlib import Path

from pydicom import dcmread
from pydicom.dataset import Dataset
from pynetdicom import (
    AE,
    StoragePresentationContexts,
    evt,
)
from pynetdicom.sop_class import (
    SecondaryCaptureImageStorage,
    StudyRootQueryRetrieveInformationModelFind,
    StudyRootQueryRetrieveInformationModelGet,
    StudyRootQueryRetrieveInformationModelMove,
)


def create_test_instances():
    """Create test instances for Query/Retrieve operations."""
    project_dir = Path(__file__).resolve().parents[1]
    sample_path = project_dir / "samples" / "test_image.dcm"

    source = dcmread(sample_path)

    study_instance_uid = "1.2.826.0.1.3680043.8.498.1001"

    instance_data = [
        (
            "1.2.826.0.1.3680043.8.498.2001",
            "1.2.826.0.1.3680043.8.498.3001",
            "1",
        ),
        (
            "1.2.826.0.1.3680043.8.498.2001",
            "1.2.826.0.1.3680043.8.498.3002",
            "2",
        ),
        (
            "1.2.826.0.1.3680043.8.498.2001",
            "1.2.826.0.1.3680043.8.498.3003",
            "3",
        ),
        (
            "1.2.826.0.1.3680043.8.498.2002",
            "1.2.826.0.1.3680043.8.498.4001",
            "1",
        ),
    ]

    instances = []

    for series_uid, sop_instance_uid, instance_number in instance_data:
        instance = deepcopy(source)

        instance.PatientID = "TEST001"
        instance.PatientName = "TEST^PATIENT"
        instance.StudyDate = "20260828"
        instance.StudyDescription = "Test Study"
        instance.AccessionNumber = "ACC001"
        instance.StudyInstanceUID = study_instance_uid
        instance.SeriesInstanceUID = series_uid
        instance.SOPInstanceUID = sop_instance_uid
        instance.InstanceNumber = instance_number

        if series_uid.endswith("2001"):
            instance.SeriesNumber = "1"
            instance.SeriesDescription = "CT Axial"
        else:
            instance.SeriesNumber = "2"
            instance.SeriesDescription = "CT Scout"

        if instance.file_meta is not None:
            instance.file_meta.MediaStorageSOPInstanceUID = (
                sop_instance_uid
            )

        instances.append(instance)

    return instances


def handle_find(event):
    """Handle incoming Study Root C-FIND requests."""

    identifier = event.identifier

    print("C-FIND request received")
    print(identifier)

    query_level = str(
        getattr(identifier, "QueryRetrieveLevel", "")
    ).strip().upper()

    study_instance_uid = "1.2.826.0.1.3680043.8.498.1001"

    if query_level == "STUDY":
        study = Dataset()
        study.QueryRetrieveLevel = "STUDY"
        study.PatientID = "TEST001"
        study.PatientName = "TEST^PATIENT"
        study.StudyDate = "20260828"
        study.StudyDescription = "Test Study"
        study.StudyInstanceUID = study_instance_uid
        study.AccessionNumber = "ACC001"
        study.ModalitiesInStudy = "CT"

        patient_id = str(
            getattr(identifier, "PatientID", "")
        ).strip()

        patient_name = str(
            getattr(identifier, "PatientName", "")
        ).strip()

        study_date = str(
            getattr(identifier, "StudyDate", "")
        ).strip()

        if patient_id and patient_id != study.PatientID:
            yield 0x0000, None
            return

        if patient_name and patient_name != str(study.PatientName):
            yield 0x0000, None
            return

        if study_date and study_date != study.StudyDate:
            yield 0x0000, None
            return

        yield 0xFF00, study
        yield 0x0000, None
        return

    if query_level == "SERIES":
        requested_study_uid = str(
            getattr(identifier, "StudyInstanceUID", "")
        ).strip()

        if requested_study_uid != study_instance_uid:
            yield 0x0000, None
            return

        series_data = [
            {
                "series_instance_uid":
                    "1.2.826.0.1.3680043.8.498.2001",
                "series_number": "1",
                "series_description": "CT Axial",
                "modality": "CT",
                "instance_count": "3",
            },
            {
                "series_instance_uid":
                    "1.2.826.0.1.3680043.8.498.2002",
                "series_number": "2",
                "series_description": "CT Scout",
                "modality": "CT",
                "instance_count": "1",
            },
        ]

        for item in series_data:
            series = Dataset()
            series.QueryRetrieveLevel = "SERIES"
            series.StudyInstanceUID = study_instance_uid
            series.SeriesInstanceUID = item["series_instance_uid"]
            series.SeriesNumber = item["series_number"]
            series.SeriesDescription = item["series_description"]
            series.Modality = item["modality"]
            series.NumberOfSeriesRelatedInstances = (
                item["instance_count"]
            )

            yield 0xFF00, series

        yield 0x0000, None
        return

    if query_level == "IMAGE":
        requested_study_uid = str(
            getattr(identifier, "StudyInstanceUID", "")
        ).strip()

        requested_series_uid = str(
            getattr(identifier, "SeriesInstanceUID", "")
        ).strip()

        if requested_study_uid != study_instance_uid:
            yield 0x0000, None
            return

        instance_data = {
            "1.2.826.0.1.3680043.8.498.2001": [
                {
                    "instance_number": "1",
                    "sop_instance_uid":
                        "1.2.826.0.1.3680043.8.498.3001",
                },
                {
                    "instance_number": "2",
                    "sop_instance_uid":
                        "1.2.826.0.1.3680043.8.498.3002",
                },
                {
                    "instance_number": "3",
                    "sop_instance_uid":
                        "1.2.826.0.1.3680043.8.498.3003",
                },
            ],
            "1.2.826.0.1.3680043.8.498.2002": [
                {
                    "instance_number": "1",
                    "sop_instance_uid":
                        "1.2.826.0.1.3680043.8.498.4001",
                },
            ],
        }

        matching_instances = instance_data.get(
            requested_series_uid,
            [],
        )

        for item in matching_instances:
            instance = Dataset()
            instance.QueryRetrieveLevel = "IMAGE"
            instance.StudyInstanceUID = study_instance_uid
            instance.SeriesInstanceUID = requested_series_uid
            instance.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
            instance.SOPInstanceUID = item["sop_instance_uid"]
            instance.InstanceNumber = item["instance_number"]

            yield 0xFF00, instance

        yield 0x0000, None
        return

    print(f"Unsupported QueryRetrieveLevel: {query_level}")
    yield 0xC000, None


def handle_move(event):
    """Handle incoming Study Root C-MOVE requests."""
    identifier = event.identifier

    print("C-MOVE request received")
    raw_destination = event.move_destination

    if isinstance(raw_destination, bytes):
        move_destination = raw_destination.decode(
            "ascii",
            errors="ignore",
        ).strip()
    else:
        move_destination = str(raw_destination).strip()

    print(f"Raw Move Destination: {raw_destination!r}")
    print(f"Move Destination: {move_destination}")
    print(identifier)

    if move_destination != "PACS_TOOLKIT":
        print(f"Unknown Move Destination: {move_destination}")
        yield (None, None)
        return

    # Destination Storage SCP address
    yield ("127.0.0.1", 11113)

    query_level = str(
        getattr(identifier, "QueryRetrieveLevel", "")
    ).strip().upper()

    study_instance_uid = str(
        getattr(identifier, "StudyInstanceUID", "")
    ).strip()

    series_instance_uid = str(
        getattr(identifier, "SeriesInstanceUID", "")
    ).strip()

    expected_study_uid = "1.2.826.0.1.3680043.8.498.1001"

    instances = create_test_instances()
    matching_instances = []

    if query_level == "STUDY":
        if study_instance_uid == expected_study_uid:
            matching_instances = instances

    elif query_level == "SERIES":
        if study_instance_uid == expected_study_uid:
            matching_instances = [
                instance
                for instance in instances
                if str(instance.SeriesInstanceUID)
                == series_instance_uid
            ]

    else:
        print(f"Unsupported QueryRetrieveLevel: {query_level}")
        yield 0
        yield 0xC000, None
        return

    print(
        f"C-MOVE matched {len(matching_instances)} instance(s)"
    )

    # Number of required C-STORE sub-operations
    yield len(matching_instances)

    for instance in matching_instances:
        if event.is_cancelled:
            yield 0xFE00, None
            return

        print(
            "Sending instance: "
            f"{instance.SOPInstanceUID}"
        )

        yield 0xFF00, instance


def handle_get(event):
    """Handle incoming Study Root C-GET requests."""
    identifier = event.identifier

    print("C-GET request received")
    print(identifier)

    query_level = str(
        getattr(identifier, "QueryRetrieveLevel", "")
    ).strip().upper()

    study_instance_uid = str(
        getattr(identifier, "StudyInstanceUID", "")
    ).strip()

    series_instance_uid = str(
        getattr(identifier, "SeriesInstanceUID", "")
    ).strip()

    expected_study_uid = "1.2.826.0.1.3680043.8.498.1001"

    instances = create_test_instances()
    matching_instances = []

    if query_level == "STUDY":
        if study_instance_uid == expected_study_uid:
            matching_instances = instances

    elif query_level == "SERIES":
        if study_instance_uid == expected_study_uid:
            matching_instances = [
                instance
                for instance in instances
                if str(instance.SeriesInstanceUID)
                == series_instance_uid
            ]

    else:
        print(
            f"Unsupported QueryRetrieveLevel: {query_level}"
        )
        yield 0
        yield 0xC000, None
        return

    print(
        f"C-GET matched {len(matching_instances)} instance(s)"
    )

    # Number of required C-STORE sub-operations
    yield len(matching_instances)

    for instance in matching_instances:
        if event.is_cancelled:
            yield 0xFE00, None
            return

        print(
            "Sending instance via C-GET: "
            f"{instance.SOPInstanceUID}"
        )

        yield 0xFF00, instance


def main():
    ae = AE(ae_title="TEST_PACS")

    ae.add_supported_context(
        StudyRootQueryRetrieveInformationModelFind
    )

    ae.add_supported_context(
        StudyRootQueryRetrieveInformationModelMove
    )

    ae.add_supported_context(
        StudyRootQueryRetrieveInformationModelGet
    )

    ae.add_supported_context(
        SecondaryCaptureImageStorage,
        scu_role=False,
        scp_role=True,
    )

    ae.requested_contexts = StoragePresentationContexts

    handlers = [
        (
            evt.EVT_C_FIND,
            handle_find,
        ),
        (
            evt.EVT_C_MOVE,
            handle_move,
        ),
        (
            evt.EVT_C_GET,
            handle_get,
        ),
    ]

    print("Starting Query/Retrieve SCP")
    print("Services: C-FIND, C-MOVE, C-GET")
    print("AE Title: TEST_PACS")
    print("Port: 11112")
    print("Move Destination: PACS_TOOLKIT -> 127.0.0.1:11113")

    ae.start_server(
        ("127.0.0.1", 11112),
        block=True,
        evt_handlers=handlers,
    )


if __name__ == "__main__":
    main()
