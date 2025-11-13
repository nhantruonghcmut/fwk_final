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
        
    def _encode_text(self, text: str) -> str:
        """
        Encode text để tương thích với FPDF (latin-1).
        Thay thế ký tự Unicode không hỗ trợ bằng '?'.
        """
        if not text:
            return ""
        
        try:
            # Thử encode sang latin-1 trước
            text.encode('latin-1')
            return text
        except UnicodeEncodeError:
            # Nếu không được, thay thế ký tự không hỗ trợ bằng '?'
            return text.encode('latin-1', errors='replace').decode('latin-1')
        
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
            pdf.cell(0, 10, self._encode_text(title), 0, 1, 'C')
            pdf.ln(5)
        except Exception as e:
            self.logger.log_error(e, "add_title")
            raise
            
    def add_heading(self, pdf: FPDF, heading: str, size: int = 12):
        """Add heading to PDF."""
        try:
            pdf.set_font('Arial', 'B', size)
            pdf.cell(0, 8, self._encode_text(heading), 0, 1, 'L')
            pdf.ln(2)
        except Exception as e:
            self.logger.log_error(e, "add_heading")
            raise
            
    def add_text(self, pdf: FPDF, text: str, size: int = 10):
        """Add text to PDF."""
        try:
            pdf.set_font('Arial', '', size)
            pdf.cell(0, 6, self._encode_text(str(text)), 0, 1, 'L')
        except Exception as e:
            self.logger.log_error(e, "add_text")
            raise
            
    def add_line(self, pdf: FPDF, text: str = ""):
        """Add line to PDF."""
        try:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, self._encode_text(text), 0, 1, 'L')
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
                pdf.cell(col_widths[i], 8, self._encode_text(str(header)), 1, 0, 'C')
            pdf.ln()
            
            # Data rows
            pdf.set_font('Arial', '', 9)
            for row in data:
                for i, cell in enumerate(row):
                    pdf.cell(col_widths[i], 6, self._encode_text(str(cell)), 1, 0, 'C')
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
            pdf.cell(0, 10, self._encode_text(text), 0, 0, 'C')
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
                pdf.cell(0, 4, self._encode_text(line), 0, 1, 'L')
                
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
            pdf.text(50, 150, self._encode_text(text))
            pdf.set_text_color(0, 0, 0)  # Reset color
        except Exception as e:
            self.logger.log_error(e, "add_watermark")
            raise
            
    def add_header(self, pdf: FPDF, text: str):
        """Add header to PDF."""
        try:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, self._encode_text(text), 0, 1, 'C')
            pdf.ln(2)
        except Exception as e:
            self.logger.log_error(e, "add_header")
            raise
            
    def generate_allure_style_report(self, suites_data: List[Dict[str, Any]], 
                                    report_name: str = "Test Execution Report") -> str:
        """
        Generate Allure-style report với trang tổng quan và chi tiết từng suite/testcase/steps.
        
        Args:
            suites_data: List of suite data, mỗi suite có format:
                {
                    "name": "suite_name",
                    "passed": 10,
                    "failed": 2,
                    "skipped": 1,
                    "total": 13,
                    "duration": 120.5,
                    "test_cases": [
                        {
                            "name": "test_name",
                            "file": "test_file.py",
                            "class": "TestClass",
                            "method": "test_method",
                            "result": "PASSED",
                            "duration": 5.2,
                            "error": None,
                            "steps": [
                                {
                                    "name": "step_name",
                                    "data": {...},
                                    "timestamp": "...",
                                    "status": "PASSED"
                                }
                            ],
                            "screenshots": [...]
                        }
                    ]
                }
            report_name: Tên báo cáo
            
        Returns:
            Đường dẫn file PDF đã tạo
        """
        try:
            pdf = self.create_pdf()
            
            # Page 1: Overview
            self._generate_overview_page(pdf, suites_data, report_name)
            
            # Next pages: Details for each suite
            # for suite in suites_data:
            #     self._generate_suite_details(pdf, suite)
            
            # Footer for all pages
            self._add_footer_to_all_pages(pdf)
            
            # Save PDF
            file_path = f"reports/pdf/allure_style_report_{int(datetime.now().timestamp())}.pdf"
            self.save_pdf(pdf, file_path)
            
            self.logger.info(f"Generated Allure-style PDF report: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.log_error(e, "generate_allure_style_report")
            raise
            
    def _generate_overview_page(self, pdf: FPDF, suites_data: List[Dict[str, Any]], 
                                report_name: str):
        """Generate trang tổng quan với thống kê tất cả các suite."""
        try:
            # Title
            self.add_title(pdf, report_name, size=18)
            pdf.ln(5)
            
            # Tổng hợp tất cả suites
            total_passed = sum(s.get("passed", 0) for s in suites_data)
            total_failed = sum(s.get("failed", 0) for s in suites_data)
            total_skipped = sum(s.get("skipped", 0) for s in suites_data)
            total_tests = total_passed + total_failed + total_skipped
            total_duration = sum(s.get("duration", 0) for s in suites_data)
            pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
            
            # Summary statistics
            self.add_heading(pdf, "Overview", size=14)
            pdf.ln(3)
            
            summary_data = [
                ["Total Tests", str(total_tests)],
                ["Passed", str(total_passed)],
                ["Failed", str(total_failed)],
                ["Skipped", str(total_skipped)],
                ["Pass Rate", f"{pass_rate:.1f}%"],
                ["Total Duration", f"{total_duration:.2f} seconds"],
                ["Execution Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            
            self.add_table(pdf, ["Metric", "Value"], 
                          [[row[0], row[1]] for row in summary_data], [80, 50])
            
            pdf.ln(5)
            
            # Suite summary table
            self.add_heading(pdf, "Test Suite Statistics", size=14)
            pdf.ln(3)
            
            suite_headers = ["Test Suite", "Total", "Passed", "Failed", "Skipped", "Pass Rate", "Duration (s)"]
            suite_col_widths = [50, 15, 15, 15, 15, 20, 20]
            
            suite_table_data = []
            for suite in suites_data:
                suite_total = suite.get("total", 0)
                suite_passed = suite.get("passed", 0)
                suite_failed = suite.get("failed", 0)
                suite_skipped = suite.get("skipped", 0)
                suite_pass_rate = (suite_passed / suite_total * 100) if suite_total > 0 else 0
                suite_duration = suite.get("duration", 0)
                
                suite_table_data.append([
                    suite.get("name", "Unknown")[:40],
                    str(suite_total),
                    str(suite_passed),
                    str(suite_failed),
                    str(suite_skipped),
                    f"{suite_pass_rate:.1f}%",
                    f"{suite_duration:.2f}"
                ])
            
            self.add_table(pdf, suite_headers, suite_table_data, suite_col_widths)
            
        except Exception as e:
            self.logger.log_error(e, "_generate_overview_page")
            raise
            
    def _generate_suite_details(self, pdf: FPDF, suite: Dict[str, Any]):
        """Generate details for a test suite."""
        try:
            self.add_page_break(pdf)
            
            suite_name = suite.get("name", "Unknown Suite")
            self.add_title(pdf, f"Test Suite: {suite_name}", size=16)
            pdf.ln(5)
            
            # Suite summary
            suite_total = suite.get("total", 0)
            suite_passed = suite.get("passed", 0)
            suite_failed = suite.get("failed", 0)
            suite_skipped = suite.get("skipped", 0)
            suite_pass_rate = (suite_passed / suite_total * 100) if suite_total > 0 else 0
            suite_duration = suite.get("duration", 0)
            
            self.add_heading(pdf, "Suite Information", size=12)
            pdf.ln(2)
            
            suite_info = [
                ["Total Tests", str(suite_total)],
                ["Passed", str(suite_passed)],
                ["Failed", str(suite_failed)],
                ["Skipped", str(suite_skipped)],
                ["Pass Rate", f"{suite_pass_rate:.1f}%"],
                ["Execution Duration", f"{suite_duration:.2f} seconds"]
            ]
            
            self.add_table(pdf, ["Metric", "Value"], 
                          [[row[0], row[1]] for row in suite_info], [60, 40])
            
            pdf.ln(5)
            
            # Test cases list
            test_cases = suite.get("test_cases", [])
            if test_cases:
                self.add_heading(pdf, "Test Cases List", size=12)
                pdf.ln(2)
                
                # Test cases summary table
                test_case_headers = ["Test Case", "Result", "Duration (s)", "File"]
                test_case_col_widths = [70, 20, 20, 50]
                
                test_case_table_data = []
                for test_case in test_cases:
                    test_case_table_data.append([
                        test_case.get("name", "Unknown")[:60],
                        test_case.get("result", "UNKNOWN"),
                        f"{test_case.get('duration', 0):.2f}",
                        test_case.get("file", "")[:40]
                    ])
                
                self.add_table(pdf, test_case_headers, test_case_table_data, test_case_col_widths)
                
                pdf.ln(5)
                
                # Details for each test case with steps
                for test_case in test_cases:
                    self._generate_test_case_details(pdf, test_case)
                    
        except Exception as e:
            self.logger.log_error(e, "_generate_suite_details")
            raise
            
    def _generate_test_case_details(self, pdf: FPDF, test_case: Dict[str, Any]):
        """Generate details for a test case including steps."""
        try:
            # Check if page break is needed
            if pdf.get_y() > 250:
                self.add_page_break(pdf)
            
            test_name = test_case.get("name", "Unknown Test")
            test_result = test_case.get("result", "UNKNOWN")
            
            # Set color for result
            if test_result == "PASSED":
                pdf.set_text_color(0, 128, 0)  # Green
            elif test_result == "FAILED":
                pdf.set_text_color(255, 0, 0)  # Red
            elif test_result == "SKIPPED":
                pdf.set_text_color(255, 165, 0)  # Orange
            else:
                pdf.set_text_color(0, 0, 0)  # Black
            
            self.add_heading(pdf, f"Test Case: {test_name} [{test_result}]", size=11)
            pdf.set_text_color(0, 0, 0)  # Reset color
            pdf.ln(2)
            
            # Test case info
            test_info = [
                ["File", test_case.get("file", "Unknown")],
                ["Class", test_case.get("class", "N/A")],
                ["Method", test_case.get("method", "N/A")],
                ["Result", test_result],
                ["Duration", f"{test_case.get('duration', 0):.2f} seconds"]
            ]
            
            for info in test_info:
                self.add_text(pdf, f"{info[0]}: {info[1]}", size=9)
            
            pdf.ln(2)
            
            # Test steps
            steps = test_case.get("steps", [])
            if steps:
                self.add_heading(pdf, "Test Steps", size=10)
                pdf.ln(2)
                
                for idx, step in enumerate(steps, 1):
                    step_name = step.get("name", "Unknown Step")
                    step_status = step.get("status", "UNKNOWN")
                    step_data = step.get("data")
                    step_timestamp = step.get("timestamp", "")
                    
                    # Step header với status
                    if step_status == "PASSED":
                        pdf.set_text_color(0, 128, 0)
                    elif step_status == "FAILED":
                        pdf.set_text_color(255, 0, 0)
                    else:
                        pdf.set_text_color(0, 0, 0)
                    
                    pdf.set_font('Arial', 'B', 9)
                    pdf.cell(0, 6, self._encode_text(f"Step {idx}: {step_name} [{step_status}]"), 0, 1, 'L')
                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font('Arial', '', 8)
                    
                    if step_timestamp:
                        pdf.cell(0, 5, self._encode_text(f"  Timestamp: {step_timestamp}"), 0, 1, 'L')
                    
                    if step_data:
                        pdf.set_font('Courier', '', 7)
                        data_str = str(step_data)
                        # Truncate long data
                        if len(data_str) > 100:
                            data_str = data_str[:100] + "..."
                        pdf.cell(0, 4, self._encode_text(f"  Data: {data_str}"), 0, 1, 'L')
                        pdf.set_font('Arial', '', 8)
                    
                    pdf.ln(1)
            
            # Error information nếu có
            error = test_case.get("error")
            if error:
                pdf.ln(2)
                pdf.set_text_color(255, 0, 0)
                self.add_heading(pdf, "Error Details", size=10)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Courier', '', 8)
                error_lines = str(error).split('\n')
                for line in error_lines[:10]:  # Limit error lines
                    if len(line) > 80:
                        line = line[:80] + "..."
                    pdf.cell(0, 4, self._encode_text(line), 0, 1, 'L')
                pdf.set_font('Arial', '', 8)
            
            # Screenshots if available
            screenshots = test_case.get("screenshots", [])
            if screenshots:
                pdf.ln(2)
                self.add_heading(pdf, "Screenshots", size=10)
                pdf.ln(2)
                for screenshot in screenshots[:3]:  # Limit number of screenshots
                    if isinstance(screenshot, str) and os.path.exists(screenshot):
                        try:
                            self.add_image(pdf, screenshot, width=80, height=0)
                        except:
                            self.add_text(pdf, f"Screenshot: {screenshot}", size=8)
            
            pdf.ln(5)
            self.add_section_break(pdf)
            
        except Exception as e:
            self.logger.log_error(e, "_generate_test_case_details")
            raise
            
    def _add_footer_to_all_pages(self, pdf: FPDF):
        """Add footer to all pages."""
        try:
            total_pages = pdf.page_no()
            for page_num in range(1, total_pages + 1):
                pdf.page = page_num
                self.add_footer(pdf, f"Page {page_num} of {total_pages} - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            self.logger.log_error(e, "_add_footer_to_all_pages")