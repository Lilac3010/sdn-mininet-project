from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel

class LatencyTopo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')

        # Links with artificial delay (TCLink)
        self.addLink(h1, s1, delay='5ms',  bw=10)
        self.addLink(h2, s1, delay='5ms',  bw=10)
        self.addLink(s1, s2, delay='10ms', bw=10)
        self.addLink(s2, s3, delay='20ms', bw=10)
        self.addLink(h3, s2, delay='5ms',  bw=10)
        self.addLink(h4, s3, delay='5ms',  bw=10)

topos = {'latencytopo': (lambda: LatencyTopo())}