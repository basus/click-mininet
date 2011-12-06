#!/usr/bin/python

"""
Netgaze experimental sandbox. Uses the Mininet virtualization platform to create
a network to demonstrate use of the Netgaze DSL.
"""

import sys, time, fileinput, shutil, os
from mininet.net import init, Mininet
from mininet.node import Switch, RemoteController
from mininet.topo import Topo, Node

from mininet.util import quietRun, makeIntfPair, moveIntf, isShellBuiltin
from mininet.moduledeps import moduleDeps, pathCheck, OVS_KMOD, OF_KMOD, TUN

from mininet.log import lg, info, error, debug, output
from mininet.cli import CLI
from mininet.term import *

flush = sys.stdout.flush
START_TIME = 0
STATIC_ARP = True
DEBUG = False


class ClickSwitch( Switch ):
    """Click kernel-space switch, based on OVSKernelSwitch.
       Currently only works in the root namespace."""

    def __init__( self, name, configPath=None, dp=None, **kwargs ):
        """Init.
           name: name for switch
           dp: netlink id (0, 1, 2, ...)
           defaultMAC: default MAC as unsigned int; random value if None"""
        Switch.__init__( self, name, **kwargs )
        self.dp = 'dp%i' % dp
        self.intf = self.dp
        if not configPath:
            configPath = os.path.join(os.getcwd(), "test.click")
        self.configPath = configPath + ".intf"
        shutil.copy(configPath, self.configPath)

    @staticmethod
    def setup():
        "Ensure any dependencies are loaded; if not, try to load them."
        pathCheck( 'click-install', 'click-uninstall',
            moduleName='Click Kernel Switch')

    def intfRename(self, intf, intfName):
        for line in fileinput.input(self.configPath, inplace=True):
            print line.replace(intfName, intf)

    def linkAs(self, node2, intfName, port1=None, port2=None):
        intf1, intf2 = super(ClickSwitch, self).linkTo(node2, port1, port2)
        self.intfRename(intf1, intfName)
        quietRun('ifconfig ' + intf1 + ' up')
        return intf1, intf2

    def start( self, controllers ):
        self.cmd("click-install " + self.configPath)
        quietRun('ifconfig lo up')
        print "ClickSwitch started\n"

    def stop( self ):
        self.cmd("click-uninstall")
        os.remove(self.configPath)


def start(ip="127.0.0.1",port="6633",app="Netgaze"):
    net = Mininet(switch=ClickSwitch,
                  controller=lambda name: RemoteController(name, defaultIP=ip, port=int(port)))

    net.addController('c0')
    h1 = net.addHost('h1', ip='144.0.3.0')
    h2 = net.addHost('h2', ip='132.0.2.0')
    sw = net.addSwitch("click")
    sw.linkAs(h1, "h1")
    sw.linkAs(h2, "h2")

    net.start()
    net.staticArp()

    output("Network ready\n")
    time.sleep(3)
    # Enter CLI mode
    # output("Press Ctrl-d or type exit to quit\n")

    # lg.setLogLevel('info')
    # CLI(net)
    # lg.setLogLevel('output')
    # net.stop()

    # Run a simple file transfer test
    output(h1.cmd("./serve.sh"))
    output(h2.cmd("wget 144.0.3.0"))

start()
