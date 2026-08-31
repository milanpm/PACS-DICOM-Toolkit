from pydicom.dataset import Dataset
from pynetdicom import AE, evt
from pynetdicom.sop_class import (
    StudyRootQueryRetrieveInformationModelFind,
)


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


def main():
    ae = AE(ae_title="TEST_PACS")

    ae.add_supported_context(
        StudyRootQueryRetrieveInformationModelFind
    )

    handlers = [
        (
            evt.EVT_C_FIND,
            handle_find,
        ),
    ]

    print("Starting C-FIND SCP")
    print("AE Title: TEST_PACS")
    print("Port: 11112")

    ae.start_server(
        ("127.0.0.1", 11112),
        block=True,
        evt_handlers=handlers,
    )


if __name__ == "__main__":
    main()
