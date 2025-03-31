import pyshark
import os, curses
from interface import Interface

class Main:

    def __init__(self) -> None:
        self._interface = None
        self._gateway   = None
        self._sniffer   = None
        self._data      = dict()
        self._packet    = None
        self._ip        = None
        self._mac       = None
        self._port      = None


    def _execute(self) -> None:
        try:
            self._get_interface_information()
            self._iniciate_sniffer()
            self._continuous_sniff()
        except KeyboardInterrupt:  print('Process interrupted by user')
        except EOFError:           print('EOFError encountered. Tshark process ended.')
        except Exception as error: print(f'Unexpected error: {error}')
        finally: self._sniffer.close()


    def _get_interface_information(self) -> None:
        interface       = Interface()
        self._interface = interface._get_interface()
        self._gateway   = interface._get_gateway_mac()


    def _iniciate_sniffer(self) -> None:
        self._sniffer = pyshark.LiveCapture(interface=self._interface)


    def _continuous_sniff(self) -> None:
        for packet in self._sniffer.sniff_continuously():
            self._packet = packet
            self._process_packet()


    def _process_packet(self) -> None:
        self._get_ip()
        self._get_mac()
        self._get_port()
        self._update_or_add_data()
        self._prepare_data_to_display()


    def _get_ip(self) -> None:
        self._ip = self.pink(self._packet.ip.src) if 'ip' in self._packet else self.red('Unknown')


    def _get_mac(self) -> None:
        mac = self._packet.eth.src
        match mac:
            case self._gateway: self._mac = self.yellow(mac) + '(internet)'
            case _:             self._mac = self.red(mac) + '(data link)'


    def _get_port(self) -> None:
        if   'TCP' in self._packet: self._port = self._packet.tcp.srcport
        elif 'UDP' in self._packet: self._port = self._packet.udp.srcport
        else:                       self._port = None


    def _update_or_add_data(self) -> None:
        if not self._ip in self._data:
            self._add_data()
        else:
            self._update_data()


    def _add_data(self) -> None:
        self._data[self._ip] = {
            'pkts' : 1, 
            'mac'  : self._mac,
            'ports': {self._port} if self._port else set()
            }


    def _update_data(self) -> None:
        self._data[self._ip]['pkts'] += 1
        if self._port: self._data[self._ip]['ports'].add(self._port)


    def _prepare_data_to_display(self) -> None:
        os.system('clear')
        for ip, info in self._data.items():
            print(f'{ip:<23}, {info["mac"]} ({info["pkts"]})')
            print(f'    - {self.yellow("Ports")}: {", ".join(info["ports"])}')


    @staticmethod
    def pink(message: str) -> str:
        return '\033[35m' + message + '\033[0m'

    @staticmethod
    def green(message:str) -> str:
        return '\033[32m' + message + '\033[0m'

    @staticmethod
    def red(message:str) -> str:
        return '\033[31m' + message + '\033[0m'

    @staticmethod
    def yellow(message:str) -> str:
        return '\033[33m' + message + '\033[0m'




if __name__ == '__main__':
    Main()._execute()