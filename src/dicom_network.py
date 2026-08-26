from pathlib import Path

from pydicom import dcmread
from pynetdicom import (
    AE,
    AllStoragePresentationContexts,
    evt,
)
from pynetdicom.sop_class import Verification

def verify_connection(
    local_ae_title,
    remote_ae_title,
    remote_ip,
    remote_port,
):
    """Send a DICOM C-ECHO request to a remote Application Entity."""
    association = None

    try:
        local_ae_title = local_ae_title.strip()
        remote_ae_title = remote_ae_title.strip()
        remote_ip = remote_ip.strip()
        remote_port = int(remote_port)

        ae = AE(ae_title=local_ae_title)
        ae.add_requested_context(Verification)

        ae.acse_timeout = 5
        ae.dimse_timeout = 5
        ae.network_timeout = 5

        association = ae.associate(
            remote_ip,
            remote_port,
            ae_title=remote_ae_title,
        )

        if not association.is_established:
            return False, "DICOM Association failed."

        status = association.send_c_echo()

        if not status or not hasattr(status, "Status"):
            return False, "No valid C-ECHO response was received."

        status_code = int(status.Status)

        if status_code == 0x0000:
            return True, "C-ECHO Success: 0x0000"

        return False, f"C-ECHO Failed: 0x{status_code:04X}"

    except (OSError, TypeError, ValueError) as error:
        return False, f"Network error: {error}"

    finally:
        if association is not None and association.is_established:
            association.release()


def send_dicom_file(
    file_path,
    local_ae_title,
    remote_ae_title,
    remote_ip,
    remote_port,
):
    """Send a DICOM file to a remote Storage SCP using C-STORE."""
    association = None

    try:
        local_ae_title = local_ae_title.strip()
        remote_ae_title = remote_ae_title.strip()
        remote_ip = remote_ip.strip()
        remote_port = int(remote_port)

        dataset = dcmread(file_path)

        if not hasattr(dataset, "SOPClassUID"):
            return False, "DICOM file does not contain SOPClassUID."

        if not hasattr(dataset, "SOPInstanceUID"):
            return False, "DICOM file does not contain SOPInstanceUID."

        ae = AE(ae_title=local_ae_title)

        ae.add_requested_context(dataset.SOPClassUID)

        ae.acse_timeout = 5
        ae.dimse_timeout = 10
        ae.network_timeout = 10

        association = ae.associate(
            remote_ip,
            remote_port,
            ae_title=remote_ae_title,
        )

        if not association.is_established:
            return False, "DICOM Association failed."

        status = association.send_c_store(dataset)

        if not status or not hasattr(status, "Status"):
            return False, "No valid C-STORE response was received."

        status_code = int(status.Status)

        if status_code == 0x0000:
            return True, "C-STORE Success: 0x0000"

        return False, f"C-STORE Failed: 0x{status_code:04X}"

    except (OSError, TypeError, ValueError) as error:
        return False, f"C-STORE error: {error}"

    finally:
        if association is not None and association.is_established:
            association.release()

def handle_store(event, storage_dir):
    """Handle an incoming C-STORE request and save the DICOM file."""
    try:
        dataset = event.dataset
        dataset.file_meta = event.file_meta

        storage_path = Path(storage_dir)
        storage_path.mkdir(parents=True, exist_ok=True)

        sop_instance_uid = str(dataset.SOPInstanceUID)

        output_path = storage_path / f"{sop_instance_uid}.dcm"

        dataset.save_as(
            output_path,
            enforce_file_format=True,
        )

        print(f"Received DICOM: {output_path}")

        return 0x0000

    except Exception as error:
        print(f"C-STORE receive error: {error}")
        return 0xC001

def start_storage_scp(
    local_ae_title,
    local_ip,
    local_port,
    storage_dir,
):
    """Start a DICOM Storage SCP server."""
    local_ae_title = local_ae_title.strip()
    local_ip = local_ip.strip()
    local_port = int(local_port)

    ae = AE(ae_title=local_ae_title)

    for context in AllStoragePresentationContexts:
        ae.add_supported_context(
            context.abstract_syntax,
            context.transfer_syntax,
        )

    handlers = [
        (
            evt.EVT_C_STORE,
            handle_store,
            [storage_dir],
        ),
    ]

    server = ae.start_server(
        (local_ip, local_port),
        block=False,
        evt_handlers=handlers,
    )

    return server
