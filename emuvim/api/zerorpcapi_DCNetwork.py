"""
Distributed Cloud Emulator (dcemulator)
(c) 2015 by Manuel Peuster <manuel.peuster@upb.de>
"""

import logging
import threading
import zerorpc


logging.basicConfig(level=logging.INFO)


class ZeroRpcApiEndpointDCNetwork(object):
    """
    Simple API endpoint that offers a zerorpc-based
    interface. This interface will be used by the
    default command line client.
    It can be used as a reference to implement
    REST interfaces providing the same semantics,
    like e.g. OpenStack compute API.
    """

    def __init__(self, listenip, port, DCNetwork=None):
        if DCNetwork :
            self.connectDCNetwork(DCNetwork)
        self.ip = listenip
        self.port = port
        logging.debug("Created monitoring API endpoint %s(%s:%d)" % (
            self.__class__.__name__, self.ip, self.port))

    def connectDCNetwork(self, net):
        self.net = net
        logging.info("Connected DCNetwork to API endpoint %s(%s:%d)" % (
            self.__class__.__name__, self.ip, self.port))

    def start(self):
        thread = threading.Thread(target=self._api_server_thread, args=())
        thread.daemon = True
        thread.start()
        logging.debug("Started API endpoint %s(%s:%d)" % (
            self.__class__.__name__, self.ip, self.port))

    def _api_server_thread(self):
        s = zerorpc.Server(DCNetworkApi(self.net))
        s.bind("tcp://%s:%d" % (self.ip, self.port))
        s.run()

    def stop(self):
        logging.info("Stop the monitoring API endpoint")
        return


class DCNetworkApi(object):
    """
        The networking and monitoring commands need the scope of the
        whole DC network to find the requested vnf. So this API is intended
        to work with a DCNetwork.
        Just pass through the corresponding request to the
        selected data center network. Do not implement provisioning
        logic here because will will have multiple API
        endpoint implementations at the end.
    """

    def __init__(self, net):
        self.net = net

    def network_action_start(self, vnf_src_name, vnf_dst_name):
        # call DCNetwork method, not really datacenter specific API for now...
        # provided dc name needs to be part of API endpoint
        # no check if vnfs are really connected to this datacenter...
        logging.debug("RPC CALL: network chain start")
        try:
            c = self.net.setChain(
                vnf_src_name, vnf_dst_name)
            return str(c)
        except Exception as ex:
            logging.exception("RPC error.")
            return ex.message

    def network_action_stop(self, vnf_src_name, vnf_dst_name):
        # call DCNetwork method, not really datacenter specific API for now...
        # provided dc name needs to be part of API endpoint
        # no check if vnfs are really connected to this datacenter...
        logging.debug("RPC CALL: network chain stop")
        try:
            c = self.net.setChain(
                vnf_src_name, vnf_dst_name, cmd='del-flows')
            return c
        except Exception as ex:
            logging.exception("RPC error.")
            return ex.message

    # get egress(default) or ingress rate of a vnf
    def monitor_get_rate(self, vnf_name, direction):
        logging.debug("RPC CALL: get rate")
        try:
            c = self.net.monitor_agent.get_rate(vnf_name, direction)
            return c
        except Exception as ex:
            logging.exception("RPC error.")
            return ex.message


