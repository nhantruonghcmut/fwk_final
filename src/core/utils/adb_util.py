"""
ADB utility for managing Android devices and emulators.
"""
import subprocess
import time
from typing import List, Dict, Any, Optional
from src.core.utils.report_logger import ReportLogger


class ADBUtil:
    """Utility class for ADB operations."""
    
    def __init__(self):
        self.logger = ReportLogger()
        self.adb_path = "adb"
        
    def execute_adb_command(self, command: str) -> tuple[str, str, int]:
        """Execute ADB command and return output, error, and return code."""
        try:
            full_command = f"{self.adb_path} {command}"
            self.logger.debug(f"Executing ADB command: {full_command}")
            
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            self.logger.error("ADB command timed out")
            return "", "Command timed out", 1
        except Exception as e:
            self.logger.log_error(e, "execute_adb_command")
            return "", str(e), 1
            
    def get_devices(self) -> List[Dict[str, str]]:
        """Get list of connected devices."""
        try:
            stdout, stderr, returncode = self.execute_adb_command("devices")
            
            if returncode != 0:
                self.logger.error(f"Failed to get devices: {stderr}")
                return []
                
            devices = []
            lines = stdout.strip().split('\n')[1:]  # Skip header line
            
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        device_id = parts[0]
                        status = parts[1]
                        devices.append({
                            "device_id": device_id,
                            "status": status
                        })
                        
            self.logger.info(f"Found {len(devices)} connected devices")
            return devices
            
        except Exception as e:
            self.logger.log_error(e, "get_devices")
            return []
            
    def get_device_info(self, device_id: str) -> Dict[str, str]:
        """Get device information."""
        try:
            device_info = {}
            
            # Get device properties
            properties = [
                "ro.product.model",
                "ro.product.brand",
                "ro.product.device",
                "ro.build.version.release",
                "ro.build.version.sdk",
                "ro.product.manufacturer"
            ]
            
            for prop in properties:
                stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell getprop {prop}")
                if returncode == 0 and stdout.strip():
                    device_info[prop] = stdout.strip()
                    
            # Get screen resolution
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell wm size")
            if returncode == 0 and stdout.strip():
                device_info["screen_size"] = stdout.strip()
                
            # Get screen density
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell wm density")
            if returncode == 0 and stdout.strip():
                device_info["screen_density"] = stdout.strip()
                
            self.logger.info(f"Retrieved device info for {device_id}")
            return device_info
            
        except Exception as e:
            self.logger.log_error(e, "get_device_info")
            return {}
            
    def install_app(self, device_id: str, apk_path: str) -> bool:
        """Install APK on device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} install {apk_path}")
            
            if returncode == 0:
                self.logger.info(f"Successfully installed APK on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to install APK: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "install_app")
            return False
            
    def uninstall_app(self, device_id: str, package_name: str) -> bool:
        """Uninstall app from device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} uninstall {package_name}")
            
            if returncode == 0:
                self.logger.info(f"Successfully uninstalled {package_name} from {device_id}")
                return True
            else:
                self.logger.error(f"Failed to uninstall app: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "uninstall_app")
            return False
            
    def start_app(self, device_id: str, package_name: str, activity_name: str) -> bool:
        """Start app on device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(
                f"-s {device_id} shell am start -n {package_name}/{activity_name}"
            )
            
            if returncode == 0:
                self.logger.info(f"Successfully started {package_name} on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to start app: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "start_app")
            return False
            
    def stop_app(self, device_id: str, package_name: str) -> bool:
        """Stop app on device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell am force-stop {package_name}")
            
            if returncode == 0:
                self.logger.info(f"Successfully stopped {package_name} on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to stop app: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "stop_app")
            return False
            
    def clear_app_data(self, device_id: str, package_name: str) -> bool:
        """Clear app data."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell pm clear {package_name}")
            
            if returncode == 0:
                self.logger.info(f"Successfully cleared data for {package_name} on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to clear app data: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "clear_app_data")
            return False
            
    def get_running_apps(self, device_id: str) -> List[str]:
        """Get list of running apps."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell dumpsys activity activities")
            
            if returncode == 0:
                # Parse output to extract package names
                apps = []
                lines = stdout.split('\n')
                for line in lines:
                    if 'package=' in line:
                        package = line.split('package=')[1].split()[0]
                        if package not in apps:
                            apps.append(package)
                            
                self.logger.info(f"Found {len(apps)} running apps on {device_id}")
                return apps
            else:
                self.logger.error(f"Failed to get running apps: {stderr}")
                return []
                
        except Exception as e:
            self.logger.log_error(e, "get_running_apps")
            return []
            
    def take_screenshot(self, device_id: str, output_path: str) -> bool:
        """Take screenshot of device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell screencap -p /sdcard/screenshot.png")
            
            if returncode == 0:
                # Pull screenshot to local machine
                stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} pull /sdcard/screenshot.png {output_path}")
                
                if returncode == 0:
                    self.logger.info(f"Screenshot saved to {output_path}")
                    return True
                else:
                    self.logger.error(f"Failed to pull screenshot: {stderr}")
                    return False
            else:
                self.logger.error(f"Failed to take screenshot: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "take_screenshot")
            return False
            
    def input_text(self, device_id: str, text: str) -> bool:
        """Input text on device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell input text '{text}'")
            
            if returncode == 0:
                self.logger.info(f"Successfully input text on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to input text: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "input_text")
            return False
            
    def tap_coordinates(self, device_id: str, x: int, y: int) -> bool:
        """Tap coordinates on device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell input tap {x} {y}")
            
            if returncode == 0:
                self.logger.info(f"Successfully tapped coordinates ({x}, {y}) on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to tap coordinates: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "tap_coordinates")
            return False
            
    def swipe(self, device_id: str, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000) -> bool:
        """Swipe on device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(
                f"-s {device_id} shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}"
            )
            
            if returncode == 0:
                self.logger.info(f"Successfully swiped on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to swipe: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "swipe")
            return False
            
    def press_key(self, device_id: str, key_code: int) -> bool:
        """Press key on device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell input keyevent {key_code}")
            
            if returncode == 0:
                self.logger.info(f"Successfully pressed key {key_code} on {device_id}")
                return True
            else:
                self.logger.error(f"Failed to press key: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "press_key")
            return False
            
    def get_logcat(self, device_id: str, package_name: str = None, lines: int = 100) -> str:
        """Get logcat output."""
        try:
            command = f"-s {device_id} logcat -d"
            if package_name:
                command += f" | grep {package_name}"
            command += f" | tail -n {lines}"
            
            stdout, stderr, returncode = self.execute_adb_command(command)
            
            if returncode == 0:
                self.logger.info(f"Retrieved logcat for {device_id}")
                return stdout
            else:
                self.logger.error(f"Failed to get logcat: {stderr}")
                return ""
                
        except Exception as e:
            self.logger.log_error(e, "get_logcat")
            return ""
            
    def clear_logcat(self, device_id: str) -> bool:
        """Clear logcat."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} logcat -c")
            
            if returncode == 0:
                self.logger.info(f"Successfully cleared logcat for {device_id}")
                return True
            else:
                self.logger.error(f"Failed to clear logcat: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "clear_logcat")
            return False
            
    def get_device_battery_info(self, device_id: str) -> Dict[str, Any]:
        """Get device battery information."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell dumpsys battery")
            
            if returncode == 0:
                battery_info = {}
                lines = stdout.split('\n')
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key in ['level', 'temperature', 'voltage']:
                            try:
                                battery_info[key] = int(value)
                            except ValueError:
                                battery_info[key] = value
                        else:
                            battery_info[key] = value
                            
                self.logger.info(f"Retrieved battery info for {device_id}")
                return battery_info
            else:
                self.logger.error(f"Failed to get battery info: {stderr}")
                return {}
                
        except Exception as e:
            self.logger.log_error(e, "get_device_battery_info")
            return {}
            
    def get_device_memory_info(self, device_id: str) -> Dict[str, Any]:
        """Get device memory information."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell cat /proc/meminfo")
            
            if returncode == 0:
                memory_info = {}
                lines = stdout.split('\n')
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().split()[0]  # Get first number
                        
                        try:
                            memory_info[key] = int(value)
                        except ValueError:
                            memory_info[key] = value
                            
                self.logger.info(f"Retrieved memory info for {device_id}")
                return memory_info
            else:
                self.logger.error(f"Failed to get memory info: {stderr}")
                return {}
                
        except Exception as e:
            self.logger.log_error(e, "get_device_memory_info")
            return {}
            
    def reboot_device(self, device_id: str) -> bool:
        """Reboot device."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} reboot")
            
            if returncode == 0:
                self.logger.info(f"Successfully initiated reboot for {device_id}")
                return True
            else:
                self.logger.error(f"Failed to reboot device: {stderr}")
                return False
                
        except Exception as e:
            self.logger.log_error(e, "reboot_device")
            return False
            
    def wait_for_device(self, device_id: str, timeout: int = 60) -> bool:
        """Wait for device to be ready."""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                devices = self.get_devices()
                device = next((d for d in devices if d["device_id"] == device_id), None)
                
                if device and device["status"] == "device":
                    self.logger.info(f"Device {device_id} is ready")
                    return True
                    
                time.sleep(2)
                
            self.logger.error(f"Device {device_id} not ready after {timeout} seconds")
            return False
            
        except Exception as e:
            self.logger.log_error(e, "wait_for_device")
            return False
            
    def is_device_connected(self, device_id: str) -> bool:
        """Check if device is connected."""
        try:
            devices = self.get_devices()
            device = next((d for d in devices if d["device_id"] == device_id), None)
            return device is not None and device["status"] == "device"
        except Exception as e:
            self.logger.log_error(e, "is_device_connected")
            return False
            
    def get_installed_packages(self, device_id: str) -> List[str]:
        """Get list of installed packages."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell pm list packages")
            
            if returncode == 0:
                packages = []
                lines = stdout.split('\n')
                
                for line in lines:
                    if line.startswith('package:'):
                        package = line.replace('package:', '').strip()
                        packages.append(package)
                        
                self.logger.info(f"Found {len(packages)} installed packages on {device_id}")
                return packages
            else:
                self.logger.error(f"Failed to get installed packages: {stderr}")
                return []
                
        except Exception as e:
            self.logger.log_error(e, "get_installed_packages")
            return []
            
    def get_package_info(self, device_id: str, package_name: str) -> Dict[str, str]:
        """Get package information."""
        try:
            stdout, stderr, returncode = self.execute_adb_command(f"-s {device_id} shell dumpsys package {package_name}")
            
            if returncode == 0:
                package_info = {}
                lines = stdout.split('\n')
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        package_info[key] = value
                        
                self.logger.info(f"Retrieved package info for {package_name}")
                return package_info
            else:
                self.logger.error(f"Failed to get package info: {stderr}")
                return {}
                
        except Exception as e:
            self.logger.log_error(e, "get_package_info")
            return {}
            
    def set_adb_path(self, adb_path: str):
        """Set custom ADB path."""
        self.adb_path = adb_path
        self.logger.info(f"Set ADB path to: {adb_path}")
        
    def get_adb_version(self) -> str:
        """Get ADB version."""
        try:
            stdout, stderr, returncode = self.execute_adb_command("version")
            
            if returncode == 0:
                version = stdout.strip()
                self.logger.info(f"ADB version: {version}")
                return version
            else:
                self.logger.error(f"Failed to get ADB version: {stderr}")
                return ""
                
        except Exception as e:
            self.logger.log_error(e, "get_adb_version")
            return ""
