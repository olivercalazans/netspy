import subprocess


class Interface:

    def __init__(self):
        self._interfaces     = None
        self._selected_iface = None


    def _get_interface(self) -> str:
        self._get_network_interfaces()
        self._select_an_interface()
        return self._selected_iface


    def _get_network_interfaces(self) -> None:
        try:
            result           = subprocess.run(['ip', '-o', 'link', 'show'], capture_output=True, text=True, check=True)
            self._interfaces = [line.split(': ')[1] for line in result.stdout.splitlines()]
        except subprocess.CalledProcessError:
            self._interfaces = input(f'Write an interface: ')


    def _select_an_interface(self) -> None: 
        for index, iface in enumerate(self._interfaces):
            print(f'{index} - {iface}')

        while True:
            index = input('Select an interface: ')
            index = self._validate_input(index)

            if not index:
                print('Use a number to select')
                continue

            if index >= 0 and index < len(self._interfaces):
                self._selected_iface = self._interfaces[index]
                break

            print(f'Select between 0 and {len(self._interfaces) - 1}')


    @staticmethod
    def _validate_input(index) -> int | None:
        try:    return int(index)
        except: return None


    def _get_gateway_mac(self) -> str:
        command = f"ip neigh show $(ip route show dev {self._selected_iface} | awk '/default/ {{print $3}}') | awk '{{print $5}}'"
        result  = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()