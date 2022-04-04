class PduOutlet:
    def __init__(self, outlet_id, name, parent, state):
        self._id = outlet_id
        self._name = name
        self._parent = parent
        self._state = state

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._state

    @status.setter
    def status(self, value: bool):
        self._state = value

    def turn_off(self):
        self._parent.turn_outlet_off(self._id)
        self._state = False

    def turn_on(self):
        self._parent.turn_outlet_on(self._id)
        self._state = True

    def reboot(self):
        self._parent.reboot_outlet(self._id)

    def __str__(self):
        return f"Outlet {self._id}: {self._name}"

    def __repr__(self):
        return f"Outlet {self._id}: {self._name}"
