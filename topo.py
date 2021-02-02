#!/usr/bin/python

"""     
                        h2
                        |
                        |
                  h1---r0---r1-----h4
                             |
                             |
                             h3
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        defaultr0IP = '192.168.1.1/24'  # IP address for r0-eth1
        defaultr1IP = '192.168.1.2/24'  # IP address for r0-eth1
        r0 = self.addNode( 'r0', cls=LinuxRouter, ip=defaultr0IP ) 
        r1 = self.addNode( 'r1', cls=LinuxRouter, ip=defaultr1IP )

        
        h1 = self.addHost( 'h1', ip='192.168.2.100/24',
                           defaultRoute='via 192.168.2.1' )
        h2 = self.addHost( 'h2', ip='192.168.3.100/24',
                           defaultRoute='via 192.168.3.1' )
        h3 = self.addHost( 'h3', ip='192.168.5.100/24',
                           defaultRoute='via 192.168.5.1' )
        h4 = self.addHost( 'h4', ip='192.168.4.100/24',
                           defaultRoute='via 192.168.4.1' )
        self.addLink(r0, r1, intfName1 ='r0-eth1', param1={'ip' : defaultr0IP}, intfName2 = 'r1-eth1', param2={'ip' : defaultr1IP})
        self.addLink( h1, r0, intfName2='r0-eth2',
                      params2={ 'ip' : '192.168.2.1/24' } )  # for clarity
        self.addLink( h2, r0, intfName2='r0-eth3',
                      params2={ 'ip' : '192.168.3.1/24' } )
        self.addLink( h3, r1, intfName2='r1-eth3',
                      params2={ 'ip' : '192.168.5.1/24' } )
        self.addLink( h4, r1, intfName2='r1-eth2',
                      params2={ 'ip' : '192.168.4.1/24' } )

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    net.start()
    net['r0'].cmd('ip route add 192.168.4.0/24 via 192.168.1.2 dev r0-eth1')
    net['r0'].cmd('ip route add 192.168.5.0/24 via 192.168.1.2 dev r0-eth1')
    net['r1'].cmd('ip route add 192.168.2.0/24 via 192.168.1.1 dev r1-eth1')
    net['r1'].cmd('ip route add 192.168.3.0/24 via 192.168.1.1 dev r1-eth1')
    net['r1'].cmd('iptables -A FORWARD -p icmp -d 192.168.4.100 -j DROP')
    """
    net['h1'].cmd('iperf3 -s &')
    net['h3'].cmd('iperf3 -c 192.168.2.100 -n 500M -b 100M > iperf.out')
    """
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
