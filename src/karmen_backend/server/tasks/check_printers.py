from server import app, celery
from server.database import printers
from server import clients
from server.services import network


@celery.task(name="check_printers")
def check_printers():
    app.logger.debug("Checking known printers...")
    for raw_printer in printers.get_printers():
        printer = clients.get_printer_instance(raw_printer)
        printer.is_alive()
        current_hostname = network.get_avahi_hostname(printer.ip)
        printers.update_printer(
            uuid=printer.uuid,
            name=printer.name,
            hostname=current_hostname or printer.hostname,
            ip=printer.ip,
            port=printer.port,
            protocol=printer.protocol,
            client=printer.client_name(),
            client_props={
                "version": printer.client_info.version,
                "connected": printer.client_info.connected,
                "access_level": printer.client_info.access_level,
                "api_key": printer.client_info.api_key,
                "webcam": printer.webcam(),
            },
            printer_props=printer.get_printer_props(),
        )
