import logging
import telnetlib
import time

_LOGGER = logging.getLogger(__name__)


class ServerTechProtocol:
    """Implementation of the ServerTech PDU protocol."""

    def __init__(
        self, username: str, password: str, host: str, port: str = "23"
    ) -> None:
        """Initialize and connect to the protocol.
        :param username: Username used to log onto the pdu
        :param password: Password used to log onto the pdu
        :param host: Host IP address as a string
        :param port: Port as a string (Default: 23)
        """
        self._username = username
        self._password = password
        self.host = host
        self.port = port
        self._session = None
        self._connect()

    def close(self):
        self._session.close()

    def _connect(self) -> None:
        """Establish the telnet connection."""
        if self._session is None:
            _LOGGER.debug("Connecting")
            _LOGGER.debug(f"{self.host} {self.port}")
            self._session = telnetlib.Telnet(self.host, self.port, timeout=5)
            _LOGGER.debug("Connected, Logging In")
            self._log_in()
            _LOGGER.debug(f"Logged In")

        if not self._check_connection():
            self._session = telnetlib.Telnet(self.host, self.port)
            self._log_in()

    def _log_in(self) -> None:
        """Log in to the connection using the supplied credentials."""
        username = f"{self._username}\n".encode()
        password = f"{self._password}\n".encode()
        try:
            self._session.read_until(b"Username: ", timeout=1)
            # _LOGGER.error(test)
            self._session.write(username)
            self._session.read_until(b"Password: ", timeout=1)
            # _LOGGER.error(test)
            self._session.write(password)
        except EOFError:
            self._connect()

    def execute_command(self, command: str) -> str:
        # TODO: Return dict the has status and results data
        """Executes the specified telnet command and returns the result.
        :param command: The command that needs to be executed as a str
        """
        # _LOGGER.info("EXECUTING COMMAND")

        if not self._check_connection():
            _LOGGER.debug("Reconnecting")
            self._connect()
        self._session.read_very_lazy()
        # _LOGGER.info(f"Doing Command {command}")
        self._session.write(f"{command}\n".encode())
        # A timeout here indicates that the command is not valid
        # There's probably a better way to handle this
        data = self._session.read_until(b"Command successful", timeout=1)
        data = data.decode("ascii")
        if "Invalid command" in data:
            _LOGGER.error(f"Invalid Command: '{command}'")
        # Do this so that the check connection method works for whenever the next call is
        # This may not be needed once the connection is closed by the actual server.
        self._session.read_very_eager()
        # print(data)
        return data

    def _check_connection(self) -> bool:
        """Checks whether the telnet connection is still active."""
        try:
            self._session.read_very_eager()
            return True
        except EOFError:
            _LOGGER.debug("Connection is closed")
            return False
