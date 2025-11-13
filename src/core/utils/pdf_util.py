"""
PDF utility for generating PDF reports using fpdf.
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from fpdf import FPDF
from src.core.utils.report_logger import ReportLogger


class PDFUtil:
    """Utility class for PDF operations using fpdf."""
    
    def __init__(self):
        self.logger = ReportLogger()
        
    def create_pdf(self) -> FPDF:
        """Create new PDF document."""
        try:
            pdf = FPDF()
            pdf.add_page()
            self.logger.info("Created new PDF document")
            return pdf
        except Exception as e:
            self.logger.log_error(e, "create_pdf")
            raise
            
    def save_pdf(self, pdf: FPDF, file_path: str):
        """Save PDF to file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            pdf.output(file_path)
            self.logger.info(f"Saved PDF document: {file_path}")
        except Exception as e:
            self.logger.log_error(e, "save_pdf")
            raise
            
    def add_title(self, pdf: FPDF, title: str, size: int = 16):
        """Add title to PDF."""
        try:
            pdf.set_font('Arial', 'B', size)
            pdf.cell(0, 10, title, 0, 1, 'C')
            pdf.ln(5)
        except Exception as e:
            self.logger.log_error(e, "add_title")
            raise
            
    def add_heading(self, pdf: FPDF, heading: str, size: int = 12):
        """Add heading to PDF."""
        try:
            pdf.set_font('Arial', 'B', size)
            pdf.cell(0, 8, heading, 0, 1, 'L')
            pdf.ln(2)
        except Exception as e:
            self.logger.log_error(e, "add_heading")
            raise
            
    def add_text(self, pdf: FPDF, text: str, size: int = 10):
        """Add text to PDF."""
        try:
            pdf.set_font('Arial', '', size)
            pdf.cell(0, 6, text, 0, 1, 'L')
        except Exception as e:
            self.logger.log_error(e, "add_text")
            raise
            
    def add_line(self, pdf: FPDF, text: str = ""):
        """Add line to PDF."""
        try:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, text, 0, 1, 'L')
        except Exception as e:
            self.logger.log_error(e, "add_line")
            raise
            
    def add_table(self, pdf: FPDF, headers: List[str], data: List[List[str]], 
                  col_widths: List[float] = None):
        """Add table to PDF."""
        try:
            if not col_widths:
                col_widths = [40] * len(headers)
                
            # Headers
            pdf.set_font('Arial', 'B', 10)
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8, header, 1, 0, 'C')
            pdf.ln()
            
            # Data rows
            pdf.set_font('Arial', '', 9)
            for row in data:
                for i, cell in enumerate(row):
                    pdf.cell(col_widths[i], 6, str(cell), 1, 0, 'C')
                pdf.ln()
                
        except Exception as e:
            self.logger.log_error(e, "add_table")
            raise
            
    def add_image(self, pdf: FPDF, image_path: str, width: float = 100, height: float = 0):
        """Add image to PDF."""
        try:
            if os.path.exists(image_path):
                pdf.image(image_path, x=10, w=width, h=height)
                pdf.ln(5)
            else:
                self.logger.warning(f"Image file not found: {image_path}")
        except Exception as e:
            self.logger.log_error(e, "add_image")
            
    def add_page_break(self, pdf: FPDF):
        """Add page break."""
        try:
            pdf.add_page()
        except Exception as e:
            self.logger.log_error(e, "add_page_break")
            raise
            
    def add_footer(self, pdf: FPDF, text: str = None):
        """Add footer to PDF."""
        try:
            if not text:
                text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
            pdf.set_y(-15)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 10, text, 0, 0, 'C')
        except Exception as e:
            self.logger.log_error(e, "add_footer")
            raise
            
    def generate_test_summary(self, suite_name: str, passed: int, failed: int, 
                            skipped: int, duration: float) -> str:
        """Generate test summary PDF."""
        try:
            pdf = self.create_pdf()
            
            # Title
            self.add_title(pdf, f"Test Execution Summary - {suite_name}")
            
            # Summary information
            self.add_heading(pdf, "Execution Summary")
            total_tests = passed + failed + skipped
            pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
            
            summary_data = [
                ["Metric", "Value"],
                ["Total Tests", str(total_tests)],
                ["Passed", str(passed)],
                ["Failed", str(failed)],
                ["Skipped", str(skipped)],
                ["Pass Rate", f"{pass_rate:.1f}%"],
                ["Duration", f"{duration:.2f} seconds"],
                ["Execution Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            
            self.add_table(pdf, ["Metric", "Value"], 
                          [row[1:] for row in summary_data[1:]], [80, 40])
            
            # Test results chart (text-based)
            self.add_heading(pdf, "Test Results Distribution")
            self.add_text(pdf, f"Passed: {passed} tests ({pass_rate:.1f}%)")
            failed_rate = (failed / total_tests * 100) if total_tests > 0 else 0
            skipped_rate = (skipped / total_tests * 100) if total_tests > 0 else 0
            self.add_text(pdf, f"Failed: {failed} tests ({failed_rate:.1f}%)")
            self.add_text(pdf, f"Skipped: {skipped} tests ({skipped_rate:.1f}%)")
            
            # Footer
            self.add_footer(pdf)
            
            # Save PDF
            file_path = f"reports/pdf/test_summary_{suite_name}_{int(datetime.now().timestamp())}.pdf"
            self.save_pdf(pdf, file_path)
            
            return file_path
            
        except Exception as e:
            self.logger.log_error(e, "generate_test_summary")
            raise
            
    def generate_detailed_report(self, test_results: List[Dict[str, Any]], 
                               suite_name: str) -> str:
        """Generate detailed test report PDF."""
        try:
            pdf = self.create_pdf()
            
            # Title
            self.add_title(pdf, f"Detailed Test Report - {suite_name}")
            
            # Summary
            total_tests = len(test_results)
            passed_tests = len([t for t in test_results if t.get("result") == "PASSED"])
            failed_tests = len([t for t in test_results if t.get("result") == "FAILED"])
            skipped_tests = len([t for t in test_results if t.get("result") == "SKIPPED"])
            
            self.add_heading(pdf, "Summary")
            self.add_text(pdf, f"Total Tests: {total_tests}")
            self.add_text(pdf, f"Passed: {passed_tests}")
            self.add_text(pdf, f"Failed: {failed_tests}")
            self.add_text(pdf, f"Skipped: {skipped_tests}")
            
            # Test details
            self.add_heading(pdf, "Test Details")
            
            # Headers for test details table
            headers = ["Test Name", "Result", "Duration (s)", "Error"]
            col_widths = [60, 20, 20, 40]
            
            # Prepare data
            data = []
            for result in test_results:
                row = [
                    result.get("name", "")[:50],  # Truncate long names
                    result.get("result", ""),
                    f"{result.get('duration', 0):.2f}",
                    result.get("error", "")[:30] if result.get("error") else ""  # Truncate errors
                ]
                data.append(row)
                
            self.add_table(pdf, headers, data, col_widths)
            
            # Failed tests details
            failed_tests = [t for t in test_results if t.get("result") == "FAILED"]
            if failed_tests:
                self.add_page_break(pdf)
                self.add_heading(pdf, "Failed Tests Details")
                
                for i, test in enumerate(failed_tests, 1):
                    self.add_heading(pdf, f"{i}. {test.get('name', 'Unknown Test')}")
                    self.add_text(pdf, f"File: {test.get('file', 'Unknown')}")
                    self.add_text(pdf, f"Duration: {test.get('duration', 0):.2f} seconds")
                    if test.get("error"):
                        self.add_text(pdf, f"Error: {test.get('error')}")
                    self.add_line(pdf)
                    
            # Footer
            self.add_footer(pdf)
            
            # Save PDF
            file_path = f"reports/pdf/detailed_report_{suite_name}_{int(datetime.now().timestamp())}.pdf"
            self.save_pdf(pdf, file_path)
            
            return file_path
            
        except Exception as e:
            self.logger.log_error(e, "generate_detailed_report")
            raise
            
    def generate_performance_report(self, performance_data: List[Dict[str, Any]], 
                                  suite_name: str) -> str:
        """Generate performance report PDF."""
        try:
            pdf = self.create_pdf()
            
            # Title
            self.add_title(pdf, f"Performance Report - {suite_name}")
            
            # Performance summary
            self.add_heading(pdf, "Performance Summary")
            
            if performance_data:
                avg_duration = sum(d.get("duration", 0) for d in performance_data) / len(performance_data)
                min_duration = min(d.get("duration", 0) for d in performance_data)
                max_duration = max(d.get("duration", 0) for d in performance_data)
                
                self.add_text(pdf, f"Average Duration: {avg_duration:.2f} seconds")
                self.add_text(pdf, f"Minimum Duration: {min_duration:.2f} seconds")
                self.add_text(pdf, f"Maximum Duration: {max_duration:.2f} seconds")
                self.add_text(pdf, f"Total Tests: {len(performance_data)}")
                
                # Performance table
                self.add_heading(pdf, "Test Performance Details")
                headers = ["Test Name", "Duration (s)", "Status"]
                col_widths = [80, 30, 20]
                
                data = []
                for perf in performance_data:
                    row = [
                        perf.get("name", "")[:50],
                        f"{perf.get('duration', 0):.2f}",
                        perf.get("status", "")
                    ]
                    data.append(row)
                    
                self.add_table(pdf, headers, data, col_widths)
                
            # Footer
            self.add_footer(pdf)
            
            # Save PDF
            file_path = f"reports/pdf/performance_report_{suite_name}_{int(datetime.now().timestamp())}.pdf"
            self.save_pdf(pdf, file_path)
            
            return file_path
            
        except Exception as e:
            self.logger.log_error(e, "generate_performance_report")
            raise
            
    def generate_configuration_report(self, config_data: Dict[str, Any], 
                                    suite_name: str) -> str:
        """Generate configuration report PDF."""
        try:
            pdf = self.create_pdf()
            
            # Title
            self.add_title(pdf, f"Configuration Report - {suite_name}")
            
            # Configuration details
            self.add_heading(pdf, "Test Configuration")
            
            for section, data in config_data.items():
                self.add_heading(pdf, section)
                if isinstance(data, dict):
                    for key, value in data.items():
                        self.add_text(pdf, f"{key}: {value}")
                else:
                    self.add_text(pdf, str(data))
                self.add_line(pdf)
                
            # Footer
            self.add_footer(pdf)
            
            # Save PDF
            file_path = f"reports/pdf/config_report_{suite_name}_{int(datetime.now().timestamp())}.pdf"
            self.save_pdf(pdf, file_path)
            
            return file_path
            
        except Exception as e:
            self.logger.log_error(e, "generate_configuration_report")
            raise
            
    def add_chart_description(self, pdf: FPDF, chart_type: str, description: str):
        """Add chart description to PDF."""
        try:
            self.add_heading(pdf, f"{chart_type} Chart")
            self.add_text(pdf, description)
        except Exception as e:
            self.logger.log_error(e, "add_chart_description")
            raise
            
    def add_code_block(self, pdf: FPDF, code: str, language: str = ""):
        """Add code block to PDF."""
        try:
            self.add_heading(pdf, f"Code Block ({language})" if language else "Code Block")
            
            # Split code into lines and add each line
            lines = code.split('\n')
            pdf.set_font('Courier', '', 8)
            
            for line in lines:
                # Truncate very long lines
                if len(line) > 80:
                    line = line[:80] + "..."
                pdf.cell(0, 4, line, 0, 1, 'L')
                
            pdf.ln(2)
            
        except Exception as e:
            self.logger.log_error(e, "add_code_block")
            raise
            
    def add_list(self, pdf: FPDF, items: List[str], list_type: str = "bullet"):
        """Add list to PDF."""
        try:
            for item in items:
                if list_type == "bullet":
                    self.add_text(pdf, f"• {item}")
                elif list_type == "numbered":
                    self.add_text(pdf, f"{items.index(item) + 1}. {item}")
                else:
                    self.add_text(pdf, f"- {item}")
                    
        except Exception as e:
            self.logger.log_error(e, "add_list")
            raise
            
    def add_section_break(self, pdf: FPDF):
        """Add section break."""
        try:
            pdf.ln(10)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        except Exception as e:
            self.logger.log_error(e, "add_section_break")
            raise
            
    def get_pdf_info(self, pdf: FPDF) -> Dict[str, Any]:
        """Get PDF information."""
        try:
            return {
                "page_count": pdf.page_no(),
                "current_y": pdf.get_y(),
                "current_x": pdf.get_x(),
                "font_family": pdf.font_family,
                "font_style": pdf.font_style,
                "font_size": pdf.font_size
            }
        except Exception as e:
            self.logger.log_error(e, "get_pdf_info")
            return {}
            
    def add_watermark(self, pdf: FPDF, text: str):
        """Add watermark to PDF."""
        try:
            pdf.set_text_color(200, 200, 200)
            pdf.set_font('Arial', 'B', 50)
            pdf.text(50, 150, text)
            pdf.set_text_color(0, 0, 0)  # Reset color
        except Exception as e:
            self.logger.log_error(e, "add_watermark")
            raise
            
    def add_header(self, pdf: FPDF, text: str):
        """Add header to PDF."""
        try:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, text, 0, 1, 'C')
            pdf.ln(2)
        except Exception as e:
            self.logger.log_error(e, "add_header")
            raise
