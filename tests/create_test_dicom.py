from datetime import datetime
from pathlib import Path

import numpy as np
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid


output_path = Path("samples/test_image.dcm")
output_path.parent.mkdir(parents=True, exist_ok=True)

file_meta = FileMetaDataset()
file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
file_meta.MediaStorageSOPInstanceUID = generate_uid()
file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
file_meta.ImplementationClassUID = generate_uid()

dataset = FileDataset(
    str(output_path),
    {},
    file_meta=file_meta,
    preamble=b"\0" * 128,
)

now = datetime.now()

dataset.SOPClassUID = file_meta.MediaStorageSOPClassUID
dataset.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
dataset.PatientName = "TEST^PATIENT"
dataset.PatientID = "TEST001"
dataset.Modality = "OT"
dataset.StudyDate = now.strftime("%Y%m%d")
dataset.StudyTime = now.strftime("%H%M%S")

rows = 512
columns = 512

x = np.linspace(0, 65535, columns, dtype=np.uint16)
pixel_array = np.tile(x, (rows, 1))

dataset.Rows = rows
dataset.Columns = columns
dataset.SamplesPerPixel = 1
dataset.PhotometricInterpretation = "MONOCHROME2"
dataset.BitsAllocated = 16
dataset.BitsStored = 16
dataset.HighBit = 15
dataset.PixelRepresentation = 0
dataset.WindowCenter = 32768
dataset.WindowWidth = 65536
dataset.PixelData = pixel_array.tobytes()

dataset.save_as(str(output_path), enforce_file_format=True)

print(f"Created: {output_path}")
