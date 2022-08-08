from __future__ import print_function

import sys
import ipaddress
import ipcalc

from django.shortcuts import render


def index(request):
    return render(request, "input.html")


def result(request):
    ip_address = request.POST['ip_address']
    cdir = request.POST['cdir']

    try:
        ipaddress.IPv4Address(ip_address)
        cdir = int(cdir)
    except (ipaddress.AddressValueError, ValueError) as e:
        return render(request, "result.html", {"result": e})

    ip = IPCalculator(ip_address=ip_address, cdir=cdir)
    return render(request, "result.html", {"result": ip.get_info(sep='<br>')})

def _dec_to_binary(ip_address):
    return list(map(lambda x: bin(x)[2:].zfill(8), ip_address))


def _negation_mask(net_mask):
    wild = list()
    for i in net_mask:
        wild.append(255 - int(i))
    return wild


class IPCalculator(object):
    def __init__(self, ip_address, cdir=24):
        if '/' in ip_address:
            self._address_val, self._cidr = ip_address.split('/')
            self._address = tuple(map(int, self._address_val.split('.')))
        else:
            self._address_val = ip_address
            self._address = tuple(map(int, ip_address.split('.')))
            self._cidr = cdir
        self._subnet = ipcalc.Network(f'{self._address_val}/{self._cidr}')
        self.binary_IP = _dec_to_binary(self._address)
        self.ip_class = self._subnet.info()
        self.mask = self.get_net_mask()
        self.binary_Mask = _dec_to_binary(self.mask)
        self.negation_Mask = _dec_to_binary(_negation_mask(self.mask))
        self.network = self.get_network_ip()
        self.broadcast = self.broadcast_ip()

    def get_info(self, sep='\n'):
        return f'{sep}'.join(
            [("Calculating the IP range of: %s/%s" % (".".join(map(str, self._address)), self._cidr)),
             "==================================",
             ("Netmask: %s" % (".".join(map(str, self.mask)))),
             ("Network ID: %s" % (".".join(map(str, self.network)))),
             ("Subnet Broadcast address: %s" % (".".join(map(str, self.broadcast)))),
             ("Host min: %s" % (self.host_min())),
             ("Host max: %s" % (self.host_max())),
             ("Max number of hosts: %s" % (self.number_of_host())),
             ("IP class: %s" % self.ip_class),
             ("Given IP address belongs to class: %s" % self.find_class()),
             ("Host Address (binary): %s" % self.dec_to_bin(".".join(map(str, self._address)))),
             ("Mask (binary): %s" % self.dec_to_bin(".".join(map(str, self.mask)))),
             ("Network Address (binary): %s" % self.dec_to_bin(".".join(map(str, self.network)))),
             ("Broadcast address (binary): %s" % self.dec_to_bin(".".join(map(str, self.broadcast)))),
             ("First available host address (binary): %s" % self.dec_to_bin((self.host_min()))),
             ("Last available host address (binary): %s" % self.dec_to_bin((self.host_min())))])

    def __repr__(self):
        print(self.get_info())

    def get_net_mask(self):
        mask = [0, 0, 0, 0]
        for i in range(int(self._cidr)):
            mask[i // 8] += 1 << (7 - i % 8)
        return mask

    def broadcast_ip(self):
        broadcast = list()
        for x, y in zip(self.binary_IP, self.negation_Mask):
            broadcast.append(int(x, 2) | int(y, 2))
        return broadcast

    def get_network_ip(self):
        network = list()
        for x, y in zip(self.binary_IP, self.binary_Mask):
            network.append(int(x, 2) & int(y, 2))
        return network

    def host_min(self):
        min_range = self.network
        min_range[-1] += 1
        return ".".join(map(str, min_range))

    def host_max(self):
        max_range = self.broadcast
        max_range[-1] -= 1
        return ".".join(map(str, max_range))

    def number_of_host(self):
        return (2 ** sum(map(lambda x: sum(c == '1' for c in x), self.negation_Mask))) - 2

    def find_class(self):
        if 0 <= self._address[0] <= 127:
            return "A"
        elif 128 <= self._address[0] <= 191:
            return "B"
        elif 192 <= self._address[0] <= 223:
            return "C"
        elif 224 <= self._address[0] <= 239:
            return "D"
        else:
            return "E"

    @staticmethod
    def dec_to_bin(ip):
        ip_array = filter(None, ip.split('.'))
        ip_bin = ['{0:08b}'.format(int(el)) for el in ip_array]
        return '.'.join(ip_bin)


if __name__ == '__main__':
    ip_value = sys.argv[1] if len(sys.argv) > 1 else sys.exit(0)
    ip = IPCalculator(ip_value)
    ip.__repr__()
