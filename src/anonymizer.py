from copy import deepcopy
from pathlib import Path

import pydicom
from pydicom.dataset import Dataset


IDENTIFYING_FIELDS = [
    "PatientBirthDate",
    "PatientSex",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "OperatorsName",
    "AccessionNumber",
]


def anonymize_dataset(dataset: Dataset) -> Dataset:
    """환자 식별정보와 private tag를 제거한 복사본을 반환합니다."""
    anonymized = deepcopy(dataset)

    anonymized.PatientName = "ANONYMOUS"
    anonymized.PatientID = "ANONYMOUS"

    for field in IDENTIFYING_FIELDS:
        if hasattr(anonymized, field):
            setattr(anonymized, field, "")

    anonymized.remove_private_tags()
    anonymized.PatientIdentityRemoved = "YES"
    anonymized.DeidentificationMethod = "Basic metadata anonymization"

    return anonymized


def save_anonymized_dicom(input_path: str, output_path: str) -> Path:
    """DICOM 파일을 익명화하여 새로운 파일로 저장합니다."""
    source = Path(input_path)
    destination = Path(output_path)

    if not source.is_file():
        raise FileNotFoundError(f"DICOM file not found: {source}")

    dataset = pydicom.dcmread(str(source))
    anonymized = anonymize_dataset(dataset)

    destination.parent.mkdir(parents=True, exist_ok=True)
    anonymized.save_as(str(destination))

    return destination
