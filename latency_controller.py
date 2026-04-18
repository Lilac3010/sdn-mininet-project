from pox.core import core
from pox.lib.util import dpid_to_str
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ethernet, ipv4, icmp

log = core.getLogger()

BLOCKED_PAIR = ('10.0.0.1', '10.0.0.4')  # Scenario A: h1 cannot reach h4

class LatencyController(object):
    def __init__(self):
        core.openflow.addListeners(self)
        self.mac_to_port = {}   # {dpid: {mac: port}}
        log.info("Latency Controller started")

    def _handle_ConnectionUp(self, event):
        dpid = event.dpid
        self.mac_to_port[dpid] = {}
        log.info("Switch %s connected", dpid_to_str(dpid))

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        dpid = event.dpid
        inport = event.port

        # Learn MAC → port mapping
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][packet.src] = inport

        # --- Scenario A: Block h1 ↔ h4 ---
        ip_pkt = packet.find('ipv4')
        if ip_pkt:
            src = str(ip_pkt.srcip)
            dst = str(ip_pkt.dstip)
            if (src in BLOCKED_PAIR and dst in BLOCKED_PAIR):
                log.info("BLOCKING packet %s -> %s", src, dst)
                # Install drop rule
                msg = of.ofp_flow_mod()
                msg.match.dl_type = 0x0800
                msg.match.nw_src = ip_pkt.srcip
                msg.match.nw_dst = ip_pkt.dstip
                msg.priority = 100
                # No actions = drop
                event.connection.send(msg)
                return

        # --- Normal L2 learning forwarding ---
        if packet.dst in self.mac_to_port[dpid]:
            outport = self.mac_to_port[dpid][packet.dst]
            # Install flow rule
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, inport)
            msg.idle_timeout = 30
            msg.hard_timeout = 60
            msg.priority = 10
            msg.actions.append(of.ofp_action_output(port=outport))
            msg.data = event.ofp
            event.connection.send(msg)
        else:
            # Flood if unknown
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = inport
            event.connection.send(msg)

def launch():
    core.registerNew(LatencyController)