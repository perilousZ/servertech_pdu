import logging
import re
from typing import List
from .outlet import PduOutlet
from .protocol import ServerTechProtocol

_LOGGER = logging.getLogger(__name__)


def requires_update(f):
    """Indicates that 'update' should be called before accessing this method"""

    def wrapped(*args, **kwargs):
        self = args[0]
        self.update()
        return f(*args, **kwargs)

    return wrapped


class Commands:
    STATUS = "Status"
    OFF = "off"
    ON = "on"
    REBOOT = "reboot"
    SYSSTAT = "sysstat"


class ServerTechPDU:
    def __init__(
        self, username: str, password: str, host: str, port: str = "23"
    ) -> None:
        self._host = host
        self._port = port
        self._protocol = ServerTechProtocol(username, password, host, port)
        self._writer = ServerTechProtocol(username, password, host, port)
        self._children: List["PduOutlet"] = []
        self._mac_address: str = ""
        self._name: str = ""
        self._serial_number: str = ""
        self._model_number: str = ""
        self._active_power: str = ""
        self.get_system_info()
        self.populate_outlets()

    def close(self):
        self._protocol.close()

    def get_system_info(self):
        try:
            self._mac_address = self._get_mac_address()
            _LOGGER.debug(self.mac_address)
            self._show_towers()
            return True
        except:
            return False

    def _get_mac_address(self):
        """Returns the mac address of the PDU"""
        result = self._protocol.execute_command("show system")
        parts = result.split("\r\n")
        mac_address = None
        for x in parts:
            if "MAC Address:" in x:
                info = x.split()
                mac_address = info[2]
        return mac_address

    def _show_towers(self):
        """Basic implementation of the show towers telnet command."""
        result = self._protocol.execute_command("show towers")
        parts = result.split("\r\n")
        self._name = parts[4].split()[1]
        self._serial_number = parts[5].split()[2]
        self._model_number = parts[6].split()[2]

    def list_outlets(self) -> None:
        if len(self._children) == 0:
            self.update()
        for child in self._children:
            logging.debug(child)
            logging.debug(child.status)

    def populate_outlets(self) -> None:
        result = self._protocol.execute_command(Commands.STATUS)
        parts = result.split("\r\n")
        children = []
        for x in parts:
            if "." in x:
                info = x.split()
                state = info[2] == "On"
                child = PduOutlet(info[0], info[1], self, state)
                children.append(child)

        self._children = children

    def update(self) -> None:
        if len(self._children) == 0:
            self.populate_outlets
        state = {}
        for outlet in self._children:
            state[outlet.id] = outlet.status
        return state

    def update_all(self) -> dict:
        result = self._protocol.execute_command(Commands.STATUS)
        parts = result.split("\r\n")
        i = 0
        for x in parts:
            if "." in x:
                info = x.split()
                state = info[2] == "On"
                self._children[i].status = state
                i += 1
        state = {}
        for outlet in self._children:
            state[outlet.id] = outlet.status

        self._get_active_power()
        return state

    def turn_outlet_off(self, outlet_id: str) -> None:
        self._writer.execute_command(f"off {outlet_id}")

    def turn_outlet_on(self, outlet_id: str) -> None:
        self._writer.execute_command(f"on {outlet_id}")

    def reboot_outlet(self, outlet_id: str) -> None:
        self._writer.execute_command(f"reboot {outlet_id}")

    def get_outlet_status(self, outlet_id: str) -> str:
        result = self._protocol.execute_command(f"Status {outlet_id}")
        parts = result.split("\r\n")
        _LOGGER.debug(parts)
        info = parts[5].split()
        return info[2]

    def _get_active_power(self):
        result = self._protocol.execute_command(Commands.SYSSTAT)
        self._active_power = re.findall("[0-9]+\sWatts", result)[0].split()[0]

    @property
    def active_power(self):
        return self._active_power

    @property
    def id(self):
        # TODO: Make this into a real thing
        return self._mac_address

    @property
    def mac_address(self):
        return self._mac_address

    @property
    def name(self):
        return self._name

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def model_number(self):
        return self._model_number

    @property
    @requires_update
    def outlets(self):
        return self._children
