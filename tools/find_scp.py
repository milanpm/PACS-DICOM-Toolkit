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

    study = Dataset()
    study.QueryRetrieveLevel = "STUDY"
    study.PatientID = "TEST001"
    study.PatientName = "TEST^PATIENT"
    study.StudyDate = "20260828"
    study.StudyDescription = "Test Study"
    study.StudyInstanceUID = "1.2.826.0.1.3680043.8.498.1001"
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