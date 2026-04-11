import time

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue
from rcl_interfaces.srv import SetParameters


class GzGainSetter(Node):
    def __init__(self):
        super().__init__("gz_gain_setter")
        self.declare_parameter("target_node", "/gz_ros2_control")
        self.declare_parameter("gain", 1.5)
        self.declare_parameter("timeout_s", 30.0)

        self._start = time.time()
        self._done = False
        self._pending_future = None
        self._client = None
        self._target_service = ""
        self._timer = self.create_timer(0.2, self._tick)

    @staticmethod
    def _normalize_node_name(target_node: str) -> str:
        target_node = str(target_node).strip()
        if not target_node:
            return "/gz_ros2_control"
        if not target_node.startswith("/"):
            target_node = f"/{target_node}"
        return target_node

    def _resolve_target_service(self, target_node: str) -> str:
        target_node = self._normalize_node_name(target_node)
        target_service = f"{target_node}/set_parameters"

        service_names = {name for name, _types in self.get_service_names_and_types()}
        if target_service in service_names:
            return target_service

        target_leaf = target_node.rsplit("/", 1)[-1]
        for node_name, node_namespace in self.get_node_names_and_namespaces():
            full_name = f"{node_namespace.rstrip('/')}/{node_name}" if node_namespace != "/" else f"/{node_name}"
            if full_name == target_node or node_name == target_leaf:
                candidate = f"{full_name}/set_parameters"
                if candidate in service_names:
                    return candidate

        return target_service

    def _on_set_parameters_response(self, future):
        if self._done:
            return

        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().warn(f"Failed to call set_parameters: {exc}")
            self._pending_future = None
            return

        self._pending_future = None
        results = response.results
        if not results or not results[0].successful:
            reason = results[0].reason if results else "unknown"
            self.get_logger().warn(f"Failed to set position_proportional_gain: {reason}")
            return

        gain = float(self.get_parameter("gain").value)
        self.get_logger().info(
            f"Set {self._target_service} position_proportional_gain = {gain}"
        )
        self._done = True
        rclpy.shutdown()

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
        target_service = self._resolve_target_service(target_node)
        if not target_service:
            return

        if self._client is None or self._target_service != target_service:
            self._target_service = target_service
            self._client = self.create_client(SetParameters, target_service)

        if not self._client.wait_for_service(timeout_sec=0.1):
            return

        if self._pending_future is not None:
            return

        req = SetParameters.Request()
        p = Parameter()
        p.name = "position_proportional_gain"
        p.value = ParameterValue(
            type=ParameterType.PARAMETER_DOUBLE,
            double_value=gain,
        )
        req.parameters = [p]

        self._pending_future = self._client.call_async(req)
        self._pending_future.add_done_callback(self._on_set_parameters_response)


def main():
    rclpy.init()
    node = GzGainSetter()
    rclpy.spin(node)
