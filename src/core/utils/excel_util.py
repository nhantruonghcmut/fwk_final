"""
Excel utility for reading and writing Excel files using openpyxl.
"""
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from src.core.utils.report_logger import ReportLogger


class ExcelUtil:
    """Utility class for Excel operations using openpyxl."""
    
    def __init__(self):
        self.logger = ReportLogger()
        
    def create_workbook(self) -> Workbook:
        """Create new workbook."""
        try:
            workbook = Workbook()
            self.logger.info("Created new Excel workbook")
            return workbook
        except Exception as e:
            self.logger.log_error(e, "create_workbook")
            raise
            
    def load_workbook(self, file_path: str) -> Workbook:
        """Load existing workbook."""
        try:
            workbook = load_workbook(file_path)
            self.logger.info(f"Loaded Excel workbook: {file_path}")
            return workbook
        except Exception as e:
            self.logger.log_error(e, "load_workbook")
            raise
            
    def save_workbook(self, workbook: Workbook, file_path: str):
        """Save workbook to file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            workbook.save(file_path)
            self.logger.info(f"Saved Excel workbook: {file_path}")
        except Exception as e:
            self.logger.log_error(e, "save_workbook")
            raise
            
    def write_data_to_sheet(self, workbook: Workbook, sheet_name: str, data: List[List[Any]], 
                           headers: List[str] = None, start_row: int = 1):
        """Write data to worksheet."""
        try:
            if sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
            else:
                worksheet = workbook.create_sheet(sheet_name)
                
            # Write headers if provided
            if headers:
                for col, header in enumerate(headers, 1):
                    cell = worksheet.cell(row=start_row, column=col, value=header)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                    
            # Write data
            for row_idx, row_data in enumerate(data, start_row + (1 if headers else 0)):
                for col_idx, value in enumerate(row_data, 1):
                    worksheet.cell(row=row_idx, column=col_idx, value=value)
                    
            # Auto-adjust column widths
            self._auto_adjust_columns(worksheet)
            
            self.logger.info(f"Written {len(data)} rows to sheet '{sheet_name}'")
            
        except Exception as e:
            self.logger.log_error(e, "write_data_to_sheet")
            raise
            
    def read_data_from_sheet(self, workbook: Workbook, sheet_name: str, 
                           start_row: int = 1, end_row: int = None) -> List[List[Any]]:
        """Read data from worksheet."""
        try:
            worksheet = workbook[sheet_name]
            data = []
            
            max_row = end_row if end_row else worksheet.max_row
            
            for row in range(start_row, max_row + 1):
                row_data = []
                for col in range(1, worksheet.max_column + 1):
                    cell_value = worksheet.cell(row=row, column=col).value
                    row_data.append(cell_value)
                data.append(row_data)
                
            self.logger.info(f"Read {len(data)} rows from sheet '{sheet_name}'")
            return data
            
        except Exception as e:
            self.logger.log_error(e, "read_data_from_sheet")
            raise
            
    def read_data_as_dict(self, workbook: Workbook, sheet_name: str, 
                         start_row: int = 1, end_row: int = None) -> List[Dict[str, Any]]:
        """Read data as list of dictionaries."""
        try:
            worksheet = workbook[sheet_name]
            data = []
            
            # Get headers from first row
            headers = []
            for col in range(1, worksheet.max_column + 1):
                header = worksheet.cell(row=start_row, column=col).value
                headers.append(header or f"Column_{col}")
                
            max_row = end_row if end_row else worksheet.max_row
            
            # Read data rows
            for row in range(start_row + 1, max_row + 1):
                row_dict = {}
                for col, header in enumerate(headers, 1):
                    cell_value = worksheet.cell(row=row, column=col).value
                    row_dict[header] = cell_value
                data.append(row_dict)
                
            self.logger.info(f"Read {len(data)} rows as dictionaries from sheet '{sheet_name}'")
            return data
            
        except Exception as e:
            self.logger.log_error(e, "read_data_as_dict")
            raise
            
    def create_test_report(self, test_results: List[Dict[str, Any]], suite_name: str) -> str:
        """Create test execution report."""
        try:
            workbook = self.create_workbook()
            
            # Test Summary Sheet
            self._create_test_summary_sheet(workbook, test_results, suite_name)
            
            # Test Details Sheet
            self._create_test_details_sheet(workbook, test_results)
            
            # Test Statistics Sheet
            self._create_test_statistics_sheet(workbook, test_results)
            
            # Save workbook
            file_path = f"reports/excel/test_report_{suite_name}_{int(time.time())}.xlsx"
            self.save_workbook(workbook, file_path)
            
            return file_path
            
        except Exception as e:
            self.logger.log_error(e, "create_test_report")
            raise
            
    def _create_test_summary_sheet(self, workbook: Workbook, test_results: List[Dict[str, Any]], suite_name: str):
        """Create test summary sheet."""
        try:
            worksheet = workbook.active
            worksheet.title = "Test Summary"
            
            # Summary data
            total_tests = len(test_results)
            passed_tests = len([t for t in test_results if t.get("result") == "PASSED"])
            failed_tests = len([t for t in test_results if t.get("result") == "FAILED"])
            skipped_tests = len([t for t in test_results if t.get("result") == "SKIPPED"])
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            summary_data = [
                ["Test Suite", suite_name],
                ["Total Tests", total_tests],
                ["Passed", passed_tests],
                ["Failed", failed_tests],
                ["Skipped", skipped_tests],
                ["Pass Rate", f"{pass_rate:.1f}%"],
                ["Execution Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            
            self.write_data_to_sheet(workbook, "Test Summary", summary_data, 
                                   headers=["Metric", "Value"], start_row=1)
            
        except Exception as e:
            self.logger.log_error(e, "_create_test_summary_sheet")
            raise
            
    def _create_test_details_sheet(self, workbook: Workbook, test_results: List[Dict[str, Any]]):
        """Create test details sheet."""
        try:
            worksheet = workbook.create_sheet("Test Details")
            
            # Headers
            headers = ["Test Name", "Test File", "Test Class", "Test Method", 
                      "Result", "Duration (s)", "Error Message", "Screenshots"]
            
            # Data
            data = []
            for result in test_results:
                row = [
                    result.get("name", ""),
                    result.get("file", ""),
                    result.get("class", ""),
                    result.get("method", ""),
                    result.get("result", ""),
                    result.get("duration", 0),
                    result.get("error", ""),
                    result.get("screenshots", "")
                ]
                data.append(row)
                
            self.write_data_to_sheet(workbook, "Test Details", data, headers=headers)
            
        except Exception as e:
            self.logger.log_error(e, "_create_test_details_sheet")
            raise
            
    def _create_test_statistics_sheet(self, workbook: Workbook, test_results: List[Dict[str, Any]]):
        """Create test statistics sheet."""
        try:
            worksheet = workbook.create_sheet("Test Statistics")
            
            # Calculate statistics
            durations = [r.get("duration", 0) for r in test_results if r.get("duration")]
            avg_duration = sum(durations) / len(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            
            # Group by result
            result_counts = {}
            for result in test_results:
                result_type = result.get("result", "UNKNOWN")
                result_counts[result_type] = result_counts.get(result_type, 0) + 1
                
            # Group by test file
            file_counts = {}
            for result in test_results:
                test_file = result.get("file", "Unknown")
                file_counts[test_file] = file_counts.get(test_file, 0) + 1
                
            # Statistics data
            stats_data = [
                ["Average Duration", f"{avg_duration:.2f}s"],
                ["Minimum Duration", f"{min_duration:.2f}s"],
                ["Maximum Duration", f"{max_duration:.2f}s"],
                ["", ""],
                ["Result Distribution", ""],
                *[[result, count] for result, count in result_counts.items()],
                ["", ""],
                ["Tests by File", ""],
                *[[file, count] for file, count in file_counts.items()]
            ]
            
            self.write_data_to_sheet(workbook, "Test Statistics", stats_data, 
                                   headers=["Metric", "Value"], start_row=1)
            
        except Exception as e:
            self.logger.log_error(e, "_create_test_statistics_sheet")
            raise
            
    def _auto_adjust_columns(self, worksheet):
        """Auto-adjust column widths."""
        try:
            for column in worksheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                        
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except Exception as e:
            self.logger.log_error(e, "_auto_adjust_columns")
            
    def create_data_driven_sheet(self, workbook: Workbook, sheet_name: str, 
                                test_data: List[Dict[str, Any]]) -> str:
        """Create data-driven test sheet."""
        try:
            if not test_data:
                return ""
                
            # Get headers from first data item
            headers = list(test_data[0].keys())
            
            # Convert data to list of lists
            data = []
            for item in test_data:
                row = [item.get(header, "") for header in headers]
                data.append(row)
                
            self.write_data_to_sheet(workbook, sheet_name, data, headers=headers)
            
            self.logger.info(f"Created data-driven sheet '{sheet_name}' with {len(data)} rows")
            return sheet_name
            
        except Exception as e:
            self.logger.log_error(e, "create_data_driven_sheet")
            raise
            
    def read_test_data(self, file_path: str, sheet_name: str = None) -> List[Dict[str, Any]]:
        """Read test data from Excel file."""
        try:
            workbook = self.load_workbook(file_path)
            
            if sheet_name:
                return self.read_data_as_dict(workbook, sheet_name)
            else:
                # Read from first sheet
                first_sheet = workbook.sheetnames[0]
                return self.read_data_as_dict(workbook, first_sheet)
                
        except Exception as e:
            self.logger.log_error(e, "read_test_data")
            raise
            
    def update_cell(self, workbook: Workbook, sheet_name: str, row: int, col: int, value: Any):
        """Update specific cell."""
        try:
            worksheet = workbook[sheet_name]
            worksheet.cell(row=row, column=col, value=value)
            self.logger.debug(f"Updated cell {sheet_name}!{row}:{col} = {value}")
        except Exception as e:
            self.logger.log_error(e, "update_cell")
            raise
            
    def get_cell_value(self, workbook: Workbook, sheet_name: str, row: int, col: int) -> Any:
        """Get cell value."""
        try:
            worksheet = workbook[sheet_name]
            return worksheet.cell(row=row, column=col).value
        except Exception as e:
            self.logger.log_error(e, "get_cell_value")
            raise
            
    def add_chart(self, workbook: Workbook, sheet_name: str, chart_type: str, 
                  data_range: str, position: str = "E2"):
        """Add chart to worksheet."""
        try:
            from openpyxl.chart import BarChart, LineChart, PieChart
            
            worksheet = workbook[sheet_name]
            
            if chart_type.lower() == "bar":
                chart = BarChart()
            elif chart_type.lower() == "line":
                chart = LineChart()
            elif chart_type.lower() == "pie":
                chart = PieChart()
            else:
                chart = BarChart()
                
            chart.title = f"{chart_type.title()} Chart"
            chart.add_data(worksheet[data_range])
            worksheet.add_chart(chart, position)
            
            self.logger.info(f"Added {chart_type} chart to sheet '{sheet_name}'")
            
        except Exception as e:
            self.logger.log_error(e, "add_chart")
            raise
            
    def format_cells(self, workbook: Workbook, sheet_name: str, 
                    cell_range: str, font: Font = None, fill: PatternFill = None,
                    alignment: Alignment = None, border: Border = None):
        """Format cells in worksheet."""
        try:
            worksheet = workbook[sheet_name]
            
            for row in worksheet[cell_range]:
                for cell in row:
                    if font:
                        cell.font = font
                    if fill:
                        cell.fill = fill
                    if alignment:
                        cell.alignment = alignment
                    if border:
                        cell.border = border
                        
            self.logger.info(f"Formatted cells {cell_range} in sheet '{sheet_name}'")
            
        except Exception as e:
            self.logger.log_error(e, "format_cells")
            raise
            
    def merge_cells(self, workbook: Workbook, sheet_name: str, cell_range: str):
        """Merge cells in worksheet."""
        try:
            worksheet = workbook[sheet_name]
            worksheet.merge_cells(cell_range)
            self.logger.info(f"Merged cells {cell_range} in sheet '{sheet_name}'")
        except Exception as e:
            self.logger.log_error(e, "merge_cells")
            raise
            
    def get_sheet_names(self, workbook: Workbook) -> List[str]:
        """Get all sheet names."""
        try:
            return workbook.sheetnames
        except Exception as e:
            self.logger.log_error(e, "get_sheet_names")
            return []
            
    def delete_sheet(self, workbook: Workbook, sheet_name: str):
        """Delete worksheet."""
        try:
            workbook.remove(workbook[sheet_name])
            self.logger.info(f"Deleted sheet '{sheet_name}'")
        except Exception as e:
            self.logger.log_error(e, "delete_sheet")
            raise
            
    def copy_sheet(self, workbook: Workbook, source_sheet: str, target_sheet: str):
        """Copy worksheet."""
        try:
            source = workbook[source_sheet]
            target = workbook.copy_worksheet(source)
            target.title = target_sheet
            self.logger.info(f"Copied sheet '{source_sheet}' to '{target_sheet}'")
        except Exception as e:
            self.logger.log_error(e, "copy_sheet")
            raise
            
    def get_workbook_info(self, workbook: Workbook) -> Dict[str, Any]:
        """Get workbook information."""
        try:
            return {
                "sheet_names": workbook.sheetnames,
                "sheet_count": len(workbook.sheetnames),
                "active_sheet": workbook.active.title
            }
        except Exception as e:
            self.logger.log_error(e, "get_workbook_info")
            return {}
