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
