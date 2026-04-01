import time

import rclpy
from rclpy.node import Node


class GzGainSetter(Node):
    def __init__(self):
        super().__init__("gz_gain_setter")
        self.declare_parameter("target_node", "/gz_ros2_control")
        self.declare_parameter("gain", 1.5)
        self.declare_parameter("timeout_s", 30.0)

        self._start = time.time()
        self._done = False
        self._timer = self.create_timer(0.2, self._tick)

    def _tick(self):
        if self._done:
            return

        timeout_s = float(self.get_parameter("timeout_s").value)
        if time.time() - self._start > timeout_s:
            self.get_logger().error("Timeout waiting to set gz gain.")
            self._done = True
            rclpy.shutdown()
            return

        target_node = str(self.get_parameter("target_node").value)
        gain = float(self.get_parameter("gain").value)

        names = self.get_node_names()
        # get_node_names() returns names without leading '/'
        if target_node.startswith("/"):
            target_node_name = target_node[1:]
        else:
            target_node_name = target_node

        if target_node_name not in names:
            return

        try:
            client = self.create_client(
                rclpy.parameter.ParameterService, f"{target_node}/set_parameters"
            )
        except Exception:
            return

        if not client.wait_for_service(timeout_sec=0.1):
            return

        from rcl_interfaces.msg import Parameter, ParameterValue
        from rcl_interfaces.srv import SetParameters

        req = SetParameters.Request()
        p = Parameter()
        p.name = "position_proportional_gain"
        p.value = ParameterValue(type=ParameterValue.TYPE_DOUBLE, double_value=gain)
        req.parameters = [p]

        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
        if future.result() is None:
            return

        results = future.result().results
        if not results or not results[0].successful:
            reason = results[0].reason if results else "unknown"
            self.get_logger().warn(f"Failed to set position_proportional_gain: {reason}")
            return

        self.get_logger().info(
            f"Set {target_node}.position_proportional_gain = {gain}"
        )
        self._done = True
        rclpy.shutdown()


def main():
    rclpy.init()
    node = GzGainSetter()
    rclpy.spin(node)

