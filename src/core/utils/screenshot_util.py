"""
Screenshot utility for capturing screenshots on test failures and success.
"""
import os
import time
from typing import Optional, Dict, Any
from playwright.sync_api import Page
from appium import webdriver
from src.core.utils.report_logger import ReportLogger
from src.core.utils.config_manager import ConfigManager


class ScreenshotUtil:
    """Utility class for taking screenshots."""
    
    def __init__(self):
        self.logger = ReportLogger()
        self.config_manager = ConfigManager( self.logger)
        self.screenshot_dir = self.config_manager.get_screenshot_directory()
        self._ensure_screenshot_directory()
        
    def _ensure_screenshot_directory(self):
        """Ensure screenshot directory exists."""
        try:
            os.makedirs(self.screenshot_dir, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create screenshot directory: {str(e)}")
            
    def take_screenshot(self, name: str = None, page: Page = None, driver: webdriver.Remote = None) -> str:
        """Take screenshot using Playwright or Appium."""
        try:
            if not name:
                name = f"screenshot_{int(time.time())}"
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            
            if page:
                # Playwright screenshot
                page.screenshot(path=screenshot_path)
                self.logger.log_screenshot(screenshot_path)
            elif driver:
                # Appium screenshot
                driver.save_screenshot(screenshot_path)
                self.logger.log_screenshot(screenshot_path)
            else:
                self.logger.error("No page or driver provided for screenshot")
                return ""
                
            return screenshot_path
            
        except Exception as e:
            self.logger.log_error(e, "take_screenshot")
            return ""
            
    def take_element_screenshot(self, element, name: str = None) -> str:
        """Take screenshot of specific element."""
        try:
            if not name:
                name = f"element_screenshot_{int(time.time())}"
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            
            # Check if element is Playwright or Selenium
            if hasattr(element, 'screenshot'):
                # Playwright element
                element.screenshot(path=screenshot_path)
            elif hasattr(element, 'screenshot'):
                # Selenium element
                element.screenshot(screenshot_path)
            else:
                self.logger.error("Unsupported element type for screenshot")
                return ""
                
            self.logger.log_screenshot(screenshot_path)
            return screenshot_path
            
        except Exception as e:
            self.logger.log_error(e, "take_element_screenshot")
            return ""
            
    def take_full_page_screenshot(self, page: Page, name: str = None) -> str:
        """Take full page screenshot."""
        try:
            if not name:
                name = f"full_page_screenshot_{int(time.time())}"
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            page.screenshot(path=screenshot_path, full_page=True)
            self.logger.log_screenshot(screenshot_path)
            return screenshot_path
            
        except Exception as e:
            self.logger.log_error(e, "take_full_page_screenshot")
            return ""
            
    def take_mobile_screenshot(self, driver: webdriver.Remote, name: str = None) -> str:
        """Take mobile screenshot."""
        try:
            if not name:
                name = f"mobile_screenshot_{int(time.time())}"
                
            screenshot_path = os.path.join(self.screenshot_dir, f"{name}.png")
            driver.save_screenshot(screenshot_path)
            self.logger.log_screenshot(screenshot_path)
            return screenshot_path
            
        except Exception as e:
            self.logger.log_error(e, "take_mobile_screenshot")
            return ""
            
    def take_screenshot_on_failure(self, test_name: str, page: Page = None, driver: webdriver.Remote = None) -> str:
        """Take screenshot on test failure."""
        if not self.config_manager.should_take_screenshot_on_failure() or (page==None and driver==None):
            return ""
            
        name = f"failure_{test_name}_{int(time.time())}"
        return self.take_screenshot(name, page, driver)
        
    def take_screenshot_on_success(self, test_name: str, page: Page = None, driver: webdriver.Remote = None) -> str:
        """Take screenshot on test success."""
        if not self.config_manager.should_take_screenshot_on_success():
            return ""
            
        name = f"success_{test_name}_{int(time.time())}"
        return self.take_screenshot(name, page, driver)
        
    def take_screenshot_on_step(self, step_name: str, page: Page = None, driver: webdriver.Remote = None) -> str:
        """Take screenshot on test step."""
        name = f"step_{step_name}_{int(time.time())}"
        return self.take_screenshot(name, page, driver)
        
    def cleanup_old_screenshots(self, days_old: int = 7):
        """Cleanup screenshots older than specified days."""
        try:
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            deleted_count = 0
            for filename in os.listdir(self.screenshot_dir):
                file_path = os.path.join(self.screenshot_dir, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        
            self.logger.info(f"Cleaned up {deleted_count} old screenshots")
            
        except Exception as e:
            self.logger.log_error(e, "cleanup_old_screenshots")
            
    def get_screenshot_info(self) -> Dict[str, Any]:
        """Get screenshot directory information."""
        try:
            if not os.path.exists(self.screenshot_dir):
                return {"directory": self.screenshot_dir, "exists": False}
                
            files = os.listdir(self.screenshot_dir)
            screenshot_files = [f for f in files if f.endswith('.png')]
            
            total_size = 0
            for filename in screenshot_files:
                file_path = os.path.join(self.screenshot_dir, filename)
                total_size += os.path.getsize(file_path)
                
            return {
                "directory": self.screenshot_dir,
                "exists": True,
                "total_files": len(screenshot_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            self.logger.log_error(e, "get_screenshot_info")
            return {"directory": self.screenshot_dir, "exists": False, "error": str(e)}
            
    def compress_screenshot(self, screenshot_path: str, quality: int = 85) -> str:
        """Compress screenshot to reduce file size."""
        try:
            from PIL import Image
            
            if not os.path.exists(screenshot_path):
                return screenshot_path
                
            # Open image
            image = Image.open(screenshot_path)
            
            # Create compressed version
            compressed_path = screenshot_path.replace('.png', '_compressed.jpg')
            image.save(compressed_path, 'JPEG', quality=quality, optimize=True)
            
            # Get file sizes
            original_size = os.path.getsize(screenshot_path)
            compressed_size = os.path.getsize(compressed_path)
            
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            self.logger.info(f"Screenshot compressed: {compression_ratio:.1f}% size reduction")
            
            # Remove original if compression was successful
            if compressed_size < original_size:
                os.remove(screenshot_path)
                return compressed_path
            else:
                os.remove(compressed_path)
                return screenshot_path
                
        except ImportError:
            self.logger.warning("PIL not available for screenshot compression")
            return screenshot_path
        except Exception as e:
            self.logger.log_error(e, "compress_screenshot")
            return screenshot_path
            
    def create_screenshot_gallery(self, output_path: str = None) -> str:
        """Create HTML gallery of screenshots."""
        try:
            if not output_path:
                output_path = os.path.join(self.screenshot_dir, "screenshot_gallery.html")
                
            screenshot_files = [f for f in os.listdir(self.screenshot_dir) if f.endswith('.png')]
            screenshot_files.sort(reverse=True)  # Most recent first
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Screenshot Gallery</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
                    .screenshot { border: 1px solid #ddd; padding: 10px; text-align: center; }
                    .screenshot img { max-width: 100%; height: auto; }
                    .screenshot h3 { margin: 10px 0; color: #333; }
                    .screenshot p { margin: 5px 0; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <h1>Screenshot Gallery</h1>
                <p>Generated on: {timestamp}</p>
                <div class="gallery">
            """.format(timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
            
            for filename in screenshot_files:
                file_path = os.path.join(self.screenshot_dir, filename)
                file_size = os.path.getsize(file_path)
                file_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
                
                html_content += f"""
                    <div class="screenshot">
                        <h3>{filename}</h3>
                        <img src="{filename}" alt="{filename}">
                        <p>Size: {file_size} bytes</p>
                        <p>Created: {file_time}</p>
                    </div>
                """
            
            html_content += """
                </div>
            </body>
            </html>
            """
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.logger.info(f"Screenshot gallery created: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.log_error(e, "create_screenshot_gallery")
            return ""
            
    def get_screenshot_statistics(self) -> Dict[str, Any]:
        """Get screenshot statistics."""
        try:
            info = self.get_screenshot_info()
            if not info.get("exists"):
                return info
                
            files = os.listdir(self.screenshot_dir)
            screenshot_files = [f for f in files if f.endswith('.png')]
            
            # Categorize screenshots
            failure_screenshots = [f for f in screenshot_files if f.startswith('failure_')]
            success_screenshots = [f for f in screenshot_files if f.startswith('success_')]
            step_screenshots = [f for f in screenshot_files if f.startswith('step_')]
            other_screenshots = [f for f in screenshot_files if not any(f.startswith(prefix) for prefix in ['failure_', 'success_', 'step_'])]
            
            return {
                **info,
                "failure_screenshots": len(failure_screenshots),
                "success_screenshots": len(success_screenshots),
                "step_screenshots": len(step_screenshots),
                "other_screenshots": len(other_screenshots),
                "total_screenshots": len(screenshot_files)
            }
            
        except Exception as e:
            self.logger.log_error(e, "get_screenshot_statistics")
            return {"error": str(e)}
