from pydicom import dcmread
from pynetdicom import AE
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
