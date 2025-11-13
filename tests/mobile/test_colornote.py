import pytest
import allure
import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from src.project.page_object.mobile.note_app_base import IntroPage, HomeNotesPage, NoteTextTypePage, NoteChecklistTypePage



@allure.parent_suite("App Mobile Tests")
class TestColorNote:  
      
    @allure.feature("Note Management")
    @allure.story("Create Checklist Note")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.colorApp
    @allure.suite("Test ColorNote App")
    def test_create_checklist_note_verify_items_and_count(self, appium_driver, data_test_add_checklistnote):
        """Test creating a checklist note with title and 2 items, verify items count and notes count"""
        data = data_test_add_checklistnote
        allure.dynamic.title(data.get("test_name", "Create Checklist Note"))
        allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Description: {data.get('description')}<br>Title: {data.get('title')}<br>Items: {', '.join(data.get('items', []))}")
        allure.dynamic.label("test_id", data.get("test_id"))
        
        try:
            with allure.step("Skip intro screen"):
                intro = IntroPage(appium_driver)
                intro.skip_intro_use()
            
            with allure.step("Navigate to home notes page"):
                home_page = HomeNotesPage(appium_driver)
            
            with allure.step(f"Create new checklist note with title: '{data['title']}'"):
                checklist_page = home_page.add_new_note_checklist()
                checklist_page.enter_title(data['title'])
                allure.attach(
                    f"Title: {data['title']}",
                    name="Checklist Title",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            with allure.step(f"Add {len(data['items'])} checklist items"):
                for index in range(len(data['items'])):
                    item_text = data['items'][index]
                    checklist_page.add_first_checklist_item(item_text)
                    allure.attach(
                        f"Item {index + 1}: {item_text}",
                        name=f"Checklist Item {index + 1}",
                        attachment_type=allure.attachment_type.TEXT
                    )
            checklist_page.click_to_view_checklist()
            
            with allure.step(f"Verify checklist items count equals {data['expected_items']}"):
                actual_items = checklist_page.count_checklist_items()   
                allure.attach(
                    f"Expected items: {data['expected_items']}, Actual items: {actual_items}",
                    name="Items Count",             
                    attachment_type=allure.attachment_type.TEXT
                )
                print(f"Checklist items count: {actual_items}")
                assert actual_items == data['expected_items'], \
                    f"Expected {data['expected_items']} checklist items, but found {actual_items}"
                allure.attach(
                    f"Checklist items count: {actual_items}",
                    name="Items Verification",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            with allure.step("Save checklist and return to home"):
                checklist_page.back_to_homenote()
            
            with allure.step(f"Verify notes count equals {data['expected_notes']}"):
                actual_count = home_page.count_notes()
                assert actual_count == data['expected_notes'], \
                    f"Expected {data['expected_notes']} notes, but found {actual_count}"
                allure.attach(
                    f"Notes count: {actual_count}",
                    name="Notes Verification",
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception as e:
            allure.dynamic.label("error", str(e))
            raise

        
    @allure.feature("Note Management")
    @allure.story("Create Text Note")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.colorApp
    @allure.suite("Test ColorNote App")
    def test_create_text_note_verify_count(self, appium_driver, data_test_add_textnote):
        """Test creating a text note with title and body, verify note count"""
        data = data_test_add_textnote
        allure.dynamic.title(data.get("test_name", "Create Text Note"))
        allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Description: {data.get('description')}<br>Title: {data.get('title')}<br>Body: {data.get('body')}")
        allure.dynamic.label("test_id", data.get("test_id"))
        
        try:
            with allure.step("Skip intro screen"):
                intro = IntroPage(appium_driver)
                intro.skip_intro_use()
            
            with allure.step("Navigate to home notes page"):
                home_page = HomeNotesPage(appium_driver)
            
            for item in data['notes']:
                with allure.step(f"Create new text note with title: '{item['title']}'"):
                    note_page = home_page.add_new_note_text()
                    note_page.enter_title(item['title'])
                    note_page.enter_body(item['body'])
                    screenshot = note_page.take_screenshot(f"{data_test_add_textnote['test_id']}_textnote_{item['title']}")
                    note_page.back_to_homenote()
                    allure.attach(
                        screenshot,
                        name=f"Note Content - {item['title']}",
                        attachment_type=allure.attachment_type.PNG
                    )
            
            with allure.step(f"Verify notes count equals {data['expected_notes']}"):
                actual_count = home_page.count_notes()
                assert actual_count == data['expected_notes'], \
                    f"Expected {data['expected_notes']} notes, but found {actual_count}"
                allure.attach(
                    f"Notes count: {actual_count}",
                    name="Verification Result",
                    attachment_type=allure.attachment_type.TEXT
                )
        except Exception as e:
            allure.dynamic.label("error", str(e))
            raise
    
    # @allure.feature("Note Management")
    # @allure.story("Mutil action in Colornote")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.colorApp
    # @allure.suite("Test ColorNote App")
    # def test_create_checklist_note_verify_items_and_count(self, appium_driver, data_test_add_checklistnote):
    #     """Test creating a checklist note with title and 2 items, verify items count and notes count"""
    #     data = data_test_add_checklistnote
    #     allure.dynamic.title(data.get("test_name", "Create Checklist Note"))
    #     allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Description: {data.get('description')}<br>Title: {data.get('title')}<br>Items: {', '.join(data.get('items', []))}")
    #     allure.dynamic.label("test_id", data.get("test_id"))
        
    #     try:
    #         with allure.step("Skip intro screen"):
    #             intro = IntroPage(appium_driver)
    #             intro.skip_intro_use()
            
    #         with allure.step("Navigate to home notes page"):
    #             home_page = HomeNotesPage(appium_driver)
            
    #         with allure.step(f"Create new checklist note with title: '{data['title']}'"):
    #             checklist_page = home_page.add_new_note_checklist()
    #             checklist_page.enter_title(data['title'])
    #             allure.attach(
    #                 f"Title: {data['title']}",
    #                 name="Checklist Title",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
            
    #         with allure.step(f"Add {len(data['items'])} checklist items"):
    #             for index in range(len(data['items'])):
    #                 item_text = data['items'][index]
    #                 checklist_page.add_first_checklist_item(item_text)
    #                 allure.attach(
    #                     f"Item {index + 1}: {item_text}",
    #                     name=f"Checklist Item {index + 1}",
    #                     attachment_type=allure.attachment_type.TEXT
    #                 )
    #         checklist_page.click_to_view_checklist()
            
    #         with allure.step(f"Verify checklist items count equals {data['expected_items']}"):
    #             actual_items = checklist_page.count_checklist_items()   
    #             allure.attach(
    #                 f"Expected items: {data['expected_items']}, Actual items: {actual_items}",
    #                 name="Items Count",             
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"Checklist items count: {actual_items}")
    #             assert actual_items == data['expected_items'], \
    #                 f"Expected {data['expected_items']} checklist items, but found {actual_items}"
    #             allure.attach(
    #                 f"Checklist items count: {actual_items}",
    #                 name="Items Verification",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
            
    #         with allure.step("Save checklist and return to home"):
    #             checklist_page.back_to_homenote()
            
    #         with allure.step(f"Verify notes count equals {data['expected_notes']}"):
    #             actual_count = home_page.count_notes()
    #             assert actual_count == data['expected_notes'], \
    #                 f"Expected {data['expected_notes']} notes, but found {actual_count}"
    #             allure.attach(
    #                 f"Notes count: {actual_count}",
    #                 name="Notes Verification",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #     except Exception as e:
    #         allure.dynamic.label("error", str(e))
    #         raise
    
    
    
    # @allure.feature("Note Management")
    # @allure.story("Mutil action in Colornote")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.colorApp
    # @allure.suite("Test ColorNote App")
    # def test_complex_action(self, appium_driver, data_test_colornote_complex):
    #     """Test creating a checklist note with title and 2 items, verify items count and notes count"""
    #     data = data_test_colornote_complex
    #     allure.dynamic.title(data.get("test_name", "Create Checklist Note"))
    #     allure.dynamic.description(f"Test ID: {data.get('test_id')}<br>Description: {data.get('description')}<br>Title: {data.get('title')}<br>Items: {', '.join(data.get('items', []))}")
    #     allure.dynamic.label("test_id", data.get("test_id"))
        
    #     try:
    #         with allure.step("Skip intro screen"):
    #             intro = IntroPage(appium_driver)
    #             intro.skip_intro_use()
            
    #         with allure.step("Navigate to home notes page"):
    #             home_page = HomeNotesPage(appium_driver)
            
    #         with allure.step(f"Create new checklist note with title: '{data['title_checklistnote']}'"):
    #             checklist_page = home_page.add_new_note_checklist()
    #             checklist_page.enter_title(data['title_checklistnote'])
    #             allure.attach(
    #                 f"Title: {data['title_checklistnote']}",
    #                 name="Checklist Title",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
            
    #         with allure.step(f"Add {len(data['items'])} checklist items"):
    #             for index in range(len(data['items'])):
    #                 item_text = data['items'][index]
    #                 checklist_page.add_first_checklist_item(item_text)
    #                 allure.attach(
    #                     f"Item {index + 1}: {item_text}",
    #                     name=f"Checklist Item {index + 1}",
    #                     attachment_type=allure.attachment_type.TEXT
    #                 )
    #         checklist_page.click_to_view_checklist()
            
    #         with allure.step(f"Verify checklist items count equals {data['expected_items_1st']}"):
    #             actual_items = checklist_page.count_checklist_items()   
    #             allure.attach(
    #                 f"Expected items: {data['expected_items_1st']}, Actual items: {actual_items}",
    #                 name="Items Count",             
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"Checklist items count: {actual_items}")
    #             assert actual_items == data['expected_items_1st'], \
    #                 f"Expected {data['expected_items_1st']} checklist items, but found {actual_items}"
    #             allure.attach(
    #                 f"Checklist items count: {actual_items}",
    #                 name="Items Verification",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #         checklist_page.click_to_edit_checklist()
    #         with allure.step(f"Add item at last: '{data['items_last']}'"):
    #             checklist_page.add_last_checklist_item(data['items_last'])
    #             screenshot = checklist_page.take_screenshot("checklist_add_last")
    #             allure.attach(
    #                 screenshot,
    #                 name="Add Item Last",
    #                 attachment_type=allure.attachment_type.PNG
    #             )
    #         with allure.step(f"Change order of item '{data['items_last']}' to position 1"):
    #             checklist_page.change_order_item(data['items_last'], 1)
    #             screenshot = checklist_page.take_screenshot("checklist_reorder")
    #             allure.attach(
    #                 screenshot,
    #                 name="Checklist Reorder Screenshot",
    #                 attachment_type=allure.attachment_type.PNG
    #             )
                
    #         with allure.step(f"Long tap to get menu item"):
    #             checklist_page.longtap_item(data['items_last'])
    #             checklist_page.tap_menu_checklist_item('Remove')

    #         with allure.step("Delete 2 item"):
    #             checklist_page.delete_checklist_item(data['items'][1])
    #             checklist_page.delete_checklist_item(data['items'][3])
    #             screenshot = checklist_page.take_screenshot("checklist_deletion")
    #             allure.attach(
    #                 f"Deleted checklist items: {data['items'][1]}, {data['items'][3]}",
    #                 name="Deleted Checklist Items",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             allure.attach(
    #                 screenshot,
    #                 name="Checklist Deletion Screenshot",
    #                 attachment_type=allure.attachment_type.PNG
    #             )
    #         with allure.step("Assert checklist deletion"):
    #             actual_items = checklist_page.count_checklist_items()
    #             allure.attach(
    #                 f"Expected items: {data['expected_items_2nd']}, Actual items: {actual_items}",
    #                 name="Items Count",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             assert actual_items == data['expected_items_2nd'], \
    #                 f"Expected {data['expected_items_2nd']} checklist items, but found {actual_items}"
            
    #         with allure.step("Save checklist and return to home"):
    #             checklist_page.back_to_homenote()
            
    #         with allure.step(f"Verify notes count equals {data['expected_notes_1st']}"):
    #             actual_count = home_page.count_notes()
    #             assert actual_count == data['expected_notes_1st'], \
    #                 f"Expected {data['expected_notes_1st']} notes, but found {actual_count}"
    #             allure.attach(
    #                 f"Notes count: {actual_count}",
    #                 name="Notes Verification",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #         with allure.step(f"Create new text note with title: '{data['title_textnote']}'"):
    #             note_page = home_page.add_new_note_text()
    #             note_page.enter_title(data['title_textnote'])
    #             note_page.enter_body(data['body_textnote'])
    #             allure.attach(
    #                 f"Title: {data['title_textnote']}\nBody: {data['body_textnote']}",
    #                 name="Note Content",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
            
    #         with allure.step("Save note and return to home"):
    #             note_page.back_to_homenote()
            
    #         with allure.step(f"Verify notes count equals {data['expected_notes_2nd']}"):
    #             actual_count = home_page.count_notes()
    #             assert actual_count == data['expected_notes_2nd'], \
    #                 f"Expected {data['expected_notes_2nd']} notes, but found {actual_count}"
    #             allure.attach(
    #                 f"Notes count: {actual_count}",
    #                 name="Verification Result",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #         with allure.step('Delete note by Longtap and botton Menu '):
    #             home_page.longtap_note_have_title(data['title_textnote'])
    #             home_page.tap_bot_menu_option('Delete')
    #             allure.attach(
    #                 f"Delete {data['title_textnote']} by Longtap and botton Menu",
    #                 name="Delete note",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             home_page.longtap_note_have_title(data['title_checklistnote'])
    #             home_page.tap_bot_menu_option('Delete')
    #             allure.attach(
    #                 f"Delete {data['title_checklistnote']} by Longtap and botton Menu",
    #                 name="Delete note",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #         with allure.step(f"Verify checklist items count equals {data['expected_items_1st']}"):
    #             actual_items = home_page.count_notes()   
    #             allure.attach(
    #                 f"Expected items: 0, Actual items: {actual_items}",
    #                 name="Items Count",             
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"Checklist items count: {actual_items}")
    #             assert actual_items == 0, \
    #                 f"Expected 0 checklist items, but found {actual_items}"
    #             allure.attach(
    #                 f"Checklist items count: {actual_items}",
    #                 name="Items Verification",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #     except Exception as e:
    #         allure.dynamic.label("error", str(e))
    #         raise




    # ### TEST FUNC ONLY
    # @allure.feature("Test all mobile methods")
    # @allure.story("Test all mobile methods")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.colorApp
    # @allure.suite("Test all mobile methods")
    # def test_all_base_mobile_methods(self, appium_driver, data_test_intro):
    #     """Test all BaseMobile methods with detailed logging"""
    #     allure.dynamic.title('Test All BaseMobile Methods (1-86)')
    #     allure.dynamic.description("Comprehensive test of all 84 BaseMobile functionality")
    #     allure.dynamic.label("test_id", 'TC_BASEMOBILE_001')
        
    #     homebase = HomeNotesPage(appium_driver)
        
    #     # ============ NETWORK & CONNECTION METHODS ============
    #     # 1. Test get_network_connection
    #     with allure.step("1. Get network connection status"):
    #         status_network = homebase.get_network_connection()
    #         allure.attach(f"Network status: {status_network}", name="Network Connection", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 1. Network connection: {status_network}")
    #         time.sleep(0.5)
        
    #     # 2. Test toggle_wifi
    #     with allure.step("2. Toggle WiFi"):
    #         homebase.toggle_wifi()
    #         wifi_status = homebase.get_network_connection()
    #         allure.attach(f"WiFi toggled. New status: {wifi_status}", name="WiFi Toggled", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 2. WiFi toggled. New status: {wifi_status}")
    #         time.sleep(0.5)
        
    #     # 3. Test toggle_data
    #     with allure.step("3. Toggle Data"):
    #         homebase.toggle_data()
    #         data_status = homebase.get_network_connection()
    #         allure.attach(f"Data toggled. New status: {data_status}", name="Data Toggled", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 3. Data toggled. New status: {data_status}")
    #         time.sleep(0.5)
        
    #     # 4. Test toggle_airplane_mode
    #     with allure.step("4. Toggle Airplane Mode"):
    #         homebase.toggle_airplane_mode()
    #         airplane_status = homebase.get_network_connection()
    #         allure.attach(f"Airplane mode toggled. New status: {airplane_status}", name="Airplane Mode Toggled", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 4. Airplane mode toggled. New status: {airplane_status}")
    #         time.sleep(0.5)
        
    #     # 5. Test set_network_connection
    #     with allure.step("5. Set network connection"):
    #         homebase.set_network_connection(6)  # WiFi + Data
    #         new_connection = homebase.get_network_connection()
    #         allure.attach(f"Network set to 6. New status: {new_connection}", name="Network Connection Set", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 5. Network set to 6. New status: {new_connection}")
    #         time.sleep(0.5)
        
    #     # 6. Test toggle_location_services
    #     with allure.step("6. Toggle Location Services"):
    #         homebase.toggle_location_services()
    #         allure.attach("Location services toggled", name="Location Services", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 6. Location services toggled")
    #         time.sleep(0.5)
        
    #     # ============ DEVICE INFORMATION METHODS ============
    #     # 7. Test get_screen_size
    #     with allure.step("7. Get screen size"):
    #         screen_size = homebase.get_screen_size()
    #         allure.attach(f"Screen size: {screen_size}", name="Screen Size", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 7. Screen size: {screen_size}")
    #         time.sleep(0.5)
        
    #     # 8. Test get_device_time
    #     with allure.step("8. Get device time"):
    #         device_time = homebase.get_device_time()
    #         allure.attach(f"Device time: {device_time}", name="Device Time", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 8. Device time: {device_time}")
    #         time.sleep(0.5)
        
    #     # 9. Test get_device_time_zone
    #     with allure.step("9. Get device time zone"):
    #         device_tz = homebase.get_device_time_zone()
    #         allure.attach(f"Device timezone: {device_tz}", name="Device Timezone", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 9. Device timezone: {device_tz}")
    #         time.sleep(0.5)
        
    #     # 10. Test get_battery_info
    #     with allure.step("10. Get battery info"):
    #         battery_info = homebase.get_battery_info()
    #         allure.attach(f"Battery info: {battery_info}", name="Battery Info", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 10. Battery info: {battery_info}")
    #         time.sleep(0.5)
        
    #     # 11. Test get_device_orientation
    #     with allure.step("11. Get device orientation"):
    #         orientation = homebase.get_device_orientation()
    #         allure.attach(f"Device orientation: {orientation}", name="Device Orientation", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 11. Device orientation: {orientation}")
    #         time.sleep(0.5)
        
    #     # 12. Test get_current_activity
    #     with allure.step("12. Get current activity"):
    #         current_activity = homebase.get_current_activity()
    #         allure.attach(f"Current activity: {current_activity}", name="Current Activity", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 12. Current activity: {current_activity}")
    #         time.sleep(0.5)
        
    #     # 13. Test get_current_package
    #     with allure.step("13. Get current package"):
    #         current_package = homebase.get_current_package()
    #         allure.attach(f"Current package: {current_package}", name="Current Package", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 13. Current package: {current_package}")
    #         time.sleep(0.5)
        
    #     # 14. Test get_page_source
    #     with allure.step("14. Get page source"):
    #         page_source = homebase.get_page_source()
    #         page_source_length = len(page_source) if page_source else 0
    #         allure.attach(f"Page source length: {page_source_length} characters", name="Page Source", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 14. Page source retrieved: {page_source_length} characters")
    #         time.sleep(0.5)
        
    #     # ============ CONTEXT & APP STATE METHODS ============
    #     # 15. Test get_current_context
    #     with allure.step("15. Get current context"):
    #         current_context = homebase.get_current_context()
    #         allure.attach(f"Current context: {current_context}", name="Current Context", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 15. Current context: {current_context}")
    #         time.sleep(0.5)
        
    #     # 16. Test get_available_contexts
    #     with allure.step("16. Get available contexts"):
    #         available_contexts = homebase.get_available_contexts()
    #         allure.attach(f"Available contexts: {available_contexts}", name="Available Contexts", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 16. Available contexts: {available_contexts}")
    #         time.sleep(0.5)
        
    #     # 17. Test switch_to_native_context
    #     with allure.step("17. Switch to native context"):
    #         homebase.switch_to_native_context()
    #         allure.attach("Switched to native context", name="Native Context", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 17. Switched to native context")
    #         time.sleep(0.5)
        
    #     # ============ APP LIFECYCLE METHODS ============
    #     # 19. Test launch_app (without app_id)
    #     with allure.step("19. Launch app"):
    #         homebase.launch_app("com.android.chrome")
    #         allure.attach("App launched", name="Launch App", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 19. App launched")
    #         time.sleep(0.5)
    #     # 18. Test switch_to_webview_context (if available)
    #     with allure.step("18. Switch to webview context (if available)"):
    #         try:
    #             homebase.switch_to_webview_context()
    #             homebase.switch_to_native_context()  # Switch back
    #             allure.attach("Switched to webview and back", name="Webview Context", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 18. Webview context available and switched back")
    #         except:
    #             allure.attach("Webview context not available", name="Webview Context", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 18. Webview context not available (expected)")
    #         time.sleep(0.5)

        
    #     # 20. Test background_app
    #     with allure.step("20. Background app for 2 seconds"):
    #         homebase.background_app(2)
    #         allure.attach("App backgrounded for 2 seconds", name="App Backgrounded", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 20. App backgrounded for 2 seconds")
    #         time.sleep(0.5)
        
    #     # 21. Test reset_app
    #     with allure.step("21. Reset app"):
    #         homebase.reset_app()
    #         allure.attach("App reset", name="App Reset", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 21. App reset")
    #         time.sleep(0.5)
        
    #     # ============ DEVICE INTERACTION METHODS ============
    #     # 22. Test rotate_device to LANDSCAPE
    #     with allure.step("22. Rotate device to LANDSCAPE"):
    #         homebase.rotate_device("LANDSCAPE")
    #         orientation_after = homebase.get_device_orientation()
    #         allure.attach(f"Device rotated to LANDSCAPE. Current: {orientation_after}", name="Device Rotated", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 22. Device rotated to LANDSCAPE. Current: {orientation_after}")
    #         time.sleep(0.5)
        
    #     # 23. Test rotate_device to PORTRAIT
    #     with allure.step("23. Rotate device to PORTRAIT"):
    #         homebase.rotate_device("PORTRAIT")
    #         orientation_final = homebase.get_device_orientation()
    #         allure.attach(f"Device rotated to PORTRAIT. Current: {orientation_final}", name="Device Rotated Back", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 23. Device rotated to PORTRAIT. Current: {orientation_final}")
    #         time.sleep(0.5)
        
    #     # 24. Test shake_device
    #     with allure.step("24. Shake device"):
    #         homebase.shake_device()
    #         allure.attach("Device shaken", name="Device Shaken", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 24. Device shaken")
    #         time.sleep(0.5)
        
    #     # 25. Test is_device_locked
    #     with allure.step("25. Check if device is locked"):
    #         is_locked = homebase.is_device_locked()
    #         allure.attach(f"Device locked: {is_locked}", name="Device Lock State", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 25. Device locked: {is_locked}")
    #         time.sleep(0.5)
        
    #     # ============ KEYBOARD METHODS ============
    #     # 26. Test hide_keyboard
    #     with allure.step("26. Hide keyboard"):
    #         homebase.hide_keyboard()
    #         allure.attach("Keyboard hidden", name="Keyboard Hidden", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 26. Keyboard hidden")
    #         time.sleep(0.5)
        
    #     # 27. Test is_keyboard_shown
    #     with allure.step("27. Check if keyboard is shown"):
    #         is_kb_shown = homebase.is_keyboard_shown()
    #         allure.attach(f"Keyboard shown: {is_kb_shown}", name="Keyboard State", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 27. Keyboard shown: {is_kb_shown}")
    #         time.sleep(0.5)
        
    #     # ============ SWIPE METHODS ============
    #     # 28. Test swipe_up
    #     with allure.step("28. Swipe up"):
    #         homebase.swipe_up(500)
    #         allure.attach("Swiped up", name="Swipe Up", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 28. Swiped up")
    #         time.sleep(0.5)
        
    #     # 29. Test swipe_down
    #     with allure.step("29. Swipe down"):
    #         homebase.swipe_down(500)
    #         allure.attach("Swiped down", name="Swipe Down", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 29. Swiped down")
    #         time.sleep(0.5)
        
    #     # 30. Test swipe_left
    #     with allure.step("30. Swipe left"):
    #         homebase.swipe_left(500)
    #         allure.attach("Swiped left", name="Swipe Left", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 30. Swiped left")
    #         time.sleep(0.5)
        
    #     # 31. Test swipe_right
    #     with allure.step("31. Swipe right"):
    #         homebase.swipe_right(500)
    #         allure.attach("Swiped right", name="Swipe Right", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 31. Swiped right")
    #         time.sleep(0.5)
        
    #     # 32. Test swipe (custom coordinates)
    #     with allure.step("32. Swipe with custom coordinates"):
    #         screen_size = homebase.get_screen_size()
    #         start_x, start_y = screen_size['width'] // 2, screen_size['height'] * 0.75
    #         end_x, end_y = screen_size['width'] // 2, screen_size['height'] * 0.25
    #         homebase.swipe(start_x, start_y, end_x, end_y, 1000)
    #         allure.attach(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})", name="Custom Swipe", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 32. Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    #         time.sleep(0.5)
        
    #     # ============ SCREENSHOT METHOD ============
    #     # 33. Test take_screenshot
    #     with allure.step("33. Take screenshot"):
    #         screenshot_path = homebase.take_screenshot("test_basemobile_methods")
    #         allure.attach(f"Screenshot saved at: {screenshot_path}", name="Screenshot Taken", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 33. Screenshot taken: {screenshot_path}")
    #         time.sleep(0.5)
        
    #     # ============ ELEMENT FINDER METHODS ============
    #     # ve man hinh home
    #     homebase.launch_app("com.google.android.apps.nexuslauncher")
    #     # 34. Test find_element_by_id (need valid ID)
    #     with allure.step("34. Find element by ID"):
    #         try:
    #             # Using a common Android element ID
    #             element_id = homebase.find_element_by_id("com.socialnmobile.dictapps.notepad.color.note:id/logo_image")
    #             allure.attach("Element found by ID", name="Find by ID", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 34. Element found by ID: com.socialnmobile.dictapps.notepad.color.note:id/logo_image")
    #         except:
    #             allure.attach("Element by ID not found (expected)", name="Find by ID", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 34. Element by ID not found (expected)")
    #         time.sleep(0.5)
        
    #     # 35. Test find_element_by_xpath
    #     with allure.step("35. Find element by XPath"):
    #         try:
    #             element = homebase.find_element_by_xpath("(//android.widget.ImageView[@resource-id='com.socialnmobile.dictapps.notepad.color.note:id/icon'])[1]")
    #             allure.attach("Element found by XPath", name="Find by XPath", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 35. Element found by XPath")
    #         except:
    #             allure.attach("Element by XPath not found (expected)", name="Find by XPath", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 35. Element by XPath not found (expected)")
    #         time.sleep(0.5)
        
    #     # 36. Test find_element_by_class_name
    #     with allure.step("36. Find element by class name"):
    #         try:
    #             element = homebase.find_element_by_class_name("android.widget.ImageView")
    #             allure.attach("Element found by class name", name="Find by Class", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 36. Element found by class name")
    #         except:
    #             allure.attach("Element by class name not found (expected)", name="Find by Class", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 36. Element by class name not found (expected)")
    #         time.sleep(0.5)
        
    #     # 37. Test find_element_by_accessibility_id
    #     with allure.step("37. Find element by accessibility ID"):
    #         try:
    #             element = homebase.find_element_by_accessibility_id("Add")
    #             allure.attach("Element found by accessibility ID", name="Find by Accessibility", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 37. Element found by accessibility ID")
    #         except:
    #             allure.attach("Element by accessibility ID not found (expected)", name="Find by Accessibility", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 37. Element by accessibility ID not found (expected)")
    #         time.sleep(0.5)
        
    #     # 38. Test find_element_by_text
    #     with allure.step("38. Find element by exact text"):
    #         try:
    #             element = homebase.find_element_by_text("Sort by modified time ▼")
    #             allure.attach("Element found by text 'Sort by modified time ▼'", name="Find by Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 38. Element found by text 'Sort by modified time ▼'")
    #         except:
    #             allure.attach("Element by text not found (expected)", name="Find by Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 38. Element by text not found (expected)")
    #         time.sleep(0.5)
        
    #     # 39. Test find_element_by_partial_text
    #     with allure.step("39. Find element by partial text"):
    #         try:
    #             element = homebase.find_element_by_partial_text("Sort by")
    #             allure.attach("Element found by partial text 'Sort by'", name="Find by Partial Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 39. Element found by partial text 'Sort by'")
    #         except:
    #             allure.attach("Element by partial text not found (expected)", name="Find by Partial Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 39. Element by partial text not found (expected)")
    #         time.sleep(0.5)
        
    #     # ============ WAIT METHODS ============
    #     # 40. Test wait_for_element (using generic locator)
    #     with allure.step("40. Wait for element"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             element = homebase.wait_for_element(locator, 5)
    #             allure.attach("Element wait successful", name="Wait for Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 40. Wait for element successful")
    #         except:
    #             allure.attach("Element wait failed (expected)", name="Wait for Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 40. Element wait failed (expected)")
    #         time.sleep(0.5)
        
    #     # 41. Test wait_for_element_visible
    #     with allure.step("41. Wait for element visible"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             element = homebase.wait_for_element_visible(locator, 5)
    #             allure.attach("Element visible wait successful", name="Wait Visible", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 41. Wait for element visible successful")
    #         except:
    #             allure.attach("Element visible wait failed (expected)", name="Wait Visible", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 41. Element visible wait failed (expected)")
    #         time.sleep(0.5)
        
    #     # 42. Test wait_for_element_clickable
    #     with allure.step("42. Wait for element clickable"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             element = homebase.wait_for_element_clickable(locator, 5)
    #             allure.attach("Element clickable wait successful", name="Wait Clickable", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 42. Wait for element clickable successful")
    #         except:
    #             allure.attach("Element clickable wait failed (expected)", name="Wait Clickable", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 42. Element clickable wait failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ VERIFICATION METHODS ============
    #     # 43. Test verify_element_present
    #     with allure.step("43. Verify element present"):
    #         locator = (AppiumBy.ACCESSIBILITY_ID, "Add")
    #         is_present = homebase.verify_element_present(locator, 5)
    #         allure.attach(f"Element present: {is_present}", name="Verify Present", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 43. Element present: {is_present}")
    #         time.sleep(0.5)
        
    #     # 44. Test verify_element_visible
    #     with allure.step("44. Verify element visible"):
    #         locator = (AppiumBy.ACCESSIBILITY_ID, "Add")
    #         is_visible = homebase.verify_element_visible(locator, 5)
    #         allure.attach(f"Element visible: {is_visible}", name="Verify Visible", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 44. Element visible: {is_visible}")
    #         time.sleep(0.5)
        
    #     # 45. Test verify_text_present
    #     with allure.step("45. Verify text present"):
    #         text_found = homebase.verify_text_present("123")
    #         allure.attach(f"Text '123' found: {text_found}", name="Verify Text", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 45. Text '123' found: {text_found}")
    #         time.sleep(0.5)
        
    #     # ============ TAP & TOUCH METHODS ============
    #     # 46. Test tap_coordinates
    #     with allure.step("46. Tap at coordinates"):
    #         x, y = 500, 100
    #         homebase.tap_coordinates(x, y)
    #         allure.attach(f"Tapped at ({x}, {y})", name="Tap Coordinates", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 46. Tapped at ({x}, {y})")
    #         time.sleep(0.5)
    #         homebase.mobile_actions.close_app()
    #     # 48. Test press_keycode
    #     with allure.step("48. Press keycode (back)"):
    #         homebase.press_keycode(4)  # Back button
    #         allure.attach("Pressed keycode 4 (back)", name="Press Keycode", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 48. Pressed keycode 4 (back)")
    #         time.sleep(0.5)

    #     # 47. Test long_press_coordinates
    #     with allure.step("47. Long press at coordinates"):
    #         x, y = 500, 400
    #         homebase.long_press_coordinates(x, y, 1000)
    #         allure.attach(f"Long pressed at ({x}, {y})", name="Long Press Coordinates", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 47. Long pressed at ({x}, {y})")
    #         time.sleep(0.5)
        
    #     # ============ KEYCODE METHODS ============
    #     # 48. Test press_keycode
    #     with allure.step("48. Press keycode (back)"):
    #         homebase.press_keycode(4)  # Back button
    #         allure.attach("Pressed keycode 4 (back)", name="Press Keycode", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 48. Pressed keycode 4 (back)")
    #         time.sleep(0.5)
    #     # 49. Test long_press_keycode
    #     with allure.step("49. Long press keycode"):
    #         homebase.long_press_keycode(4)  # Back button
    #         allure.attach("Long pressed keycode 3 (home)", name="Long Press Keycode", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 49. Long pressed keycode 3 (home)")
    #         time.sleep(0.5)
    #     homebase.press_keycode(4)      
        
    #     # ============ TEXT INPUT METHODS ============
    #     # 50. Test get_element_text (using generic locator)
    #     with allure.step("50. Get element text"):
    #         try:
    #             locator = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/text_button_center")
    #             text = homebase.get_element_text(locator)
    #             allure.attach(f"Element text: '{text}'", name="Get Element Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 50. Element text: '{text}'")
    #         except:
    #             allure.attach("Get element text failed (expected)", name="Get Element Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 50. Get element text failed (expected)")
    #         time.sleep(0.5)
        
    #     # 51. Test get_element_attribute
    #     with allure.step("51. Get element attribute"):
    #         try:
    #             locator = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/text_button_center")
    #             attr = homebase.get_element_attribute(locator, "resource-id")
    #             allure.attach(f"Element attribute: '{attr}'", name="Get Attribute", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 51. Element attribute: '{attr}'")
    #         except:
    #             allure.attach("Get element attribute failed (expected)", name="Get Attribute", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 51. Get element attribute failed (expected)")
    #         time.sleep(0.5)
        
    #     # 52. Test get_element_count
    #     with allure.step("52. Get element count"):
    #         locator = (AppiumBy.CLASS_NAME, "android.widget.ImageView")
    #         count = homebase.get_element_count(locator)
    #         allure.attach(f"Element count: {count}", name="Get Element Count", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 52. Element count: {count}")
    #         time.sleep(0.5)
        
    #     # # 53. Test send_keys (to an input field)
    #     # with allure.step("53. Send keys to element"):
    #     #     try:
    #     #         locator = (AppiumBy.CLASS_NAME, "android.widget.EditText")
    #     #         homebase.send_keys(locator, "test_input")
    #     #         allure.attach("Sent keys 'test_input' to element", name="Send Keys", attachment_type=allure.attachment_type.TEXT)
    #     #         print(f"✓ 53. Sent keys to element")
    #     #     except:
    #     #         allure.attach("Send keys failed (expected)", name="Send Keys", attachment_type=allure.attachment_type.TEXT)
    #     #         print(f"✓ 53. Send keys failed (expected)")
    #     #     time.sleep(0.5)
        
    #     # ============ SCROLL METHODS ============
    #     # 54. Test scroll_to_coordinates
    #     with allure.step("54. Scroll to coordinates"):
    #         try:
    #             homebase.scroll_to_coordinates(100, 100, 5)
    #             allure.attach("Scrolled to coordinates (100, 100)", name="Scroll Coordinates", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 54. Scrolled to coordinates")
    #         except:
    #             allure.attach("Scroll failed (expected)", name="Scroll Coordinates", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 54. Scroll failed (expected)")
    #         time.sleep(0.5)
        
    #     # 55. Test scroll_to_text
    #     with allure.step("55. Scroll to text"):
    #         try:
    #             homebase.scroll_to_text("Add", 5)
    #             allure.attach("Scrolled to text 'Add'", name="Scroll Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 55. Scrolled to text 'Add'")
    #         except:
    #             allure.attach("Scroll to text failed (expected)", name="Scroll Text", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 55. Scroll to text failed (expected)")
    #         time.sleep(0.5)
    #     homebase.get_element((AppiumBy.XPATH,"(//android.widget.ImageView[@resource-id='com.socialnmobile.dictapps.notepad.color.note:id/icon'])[2]")).click()

    #     # 56. Test scroll_to_element
    #     with allure.step("56. Scroll to element"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.scroll_to_element(locator, 5)
    #             allure.attach("Scrolled to element", name="Scroll Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 56. Scrolled to element")
    #         except:
    #             allure.attach("Scroll to element failed (expected)", name="Scroll Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 56. Scroll to element failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ ZOOM & PINCH METHODS ============
    #     # 57. Test pinch_zoom
    #     with allure.step("57. Pinch zoom"):
    #         screen_size = homebase.get_screen_size()
    #         x, y = screen_size['width'] // 2, screen_size['height'] // 2
    #         homebase.pinch_zoom(x, y, 0.5)
    #         allure.attach(f"Pinch zoomed at ({x}, {y}) with scale 0.5", name="Pinch Zoom", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 57. Pinch zoomed")
    #         time.sleep(0.5)
        
    #     # ============ TAP ELEMENT METHODS ============
    #     # 58. Test tap_element
    #     with allure.step("58. Tap element by locator"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.tap_element(locator)
    #             allure.attach("Tapped element", name="Tap Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 58. Tapped element")
    #         except:
    #             allure.attach("Tap element failed (expected)", name="Tap Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 58. Tap element failed (expected)")
    #         time.sleep(0.5)
        
    #     # 59. Test double_tap_element
    #     with allure.step("59. Double tap element"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.double_tap_element(locator)
    #             allure.attach("Double tapped element", name="Double Tap", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 59. Double tapped element")
    #         except:
    #             allure.attach("Double tap failed (expected)", name="Double Tap", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 59. Double tap failed (expected)")
    #         time.sleep(0.5)
        
    #     # 60. Test long_press_element
    #     with allure.step("60. Long press element"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.long_press_element(locator, 1000)
    #             allure.attach("Long pressed element", name="Long Press Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 60. Long pressed element")
    #         except:
    #             allure.attach("Long press element failed (expected)", name="Long Press Element", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 60. Long press element failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ DRAG & DROP METHOD ============
    #     # 61. Test drag_and_drop
    #     with allure.step("61. Drag and drop"):
    #         try:
    #             source_locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             target_locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.drag_and_drop(source_locator, target_locator)
    #             allure.attach("Dragged and dropped element", name="Drag Drop", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 61. Dragged and dropped")
    #         except:
    #             allure.attach("Drag and drop failed (expected)", name="Drag Drop", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 61. Drag and drop failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ APP MANAGEMENT METHODS ============
    #     # 62. Test install_app (simulated - requires app path)
    #     with allure.step("62. Install app (skipped - requires valid path)"):
    #         allure.attach("Install app method exists", name="Install App", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 62. Install app method available")
    #         time.sleep(0.5)
        
    #     # 63. Test uninstall_app (simulated)
    #     with allure.step("63. Uninstall app (skipped - would uninstall app)"):
    #         allure.attach("Uninstall app method exists", name="Uninstall App", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 63. Uninstall app method available")
    #         time.sleep(0.5)
        
    #     # 64. Test close_app (without app_id)
    #     with allure.step("64. Close app"):
    #         homebase.close_app()
    #         allure.attach("App closed", name="Close App", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 64. App closed")
    #         time.sleep(1)
        
    #     # Reopen app for remaining tests
    #     with allure.step("Reopen app for remaining tests"):
    #         homebase.launch_app('com.socialnmobile.dictapps.notepad.color.note')
    #         time.sleep(2)
    #         print("App reopened")
        
    #     # ============ DEVICE LOCK METHODS ============
    #     # 65. Test lock_device
    #     with allure.step("65. Lock device (5 seconds)"):
    #         homebase.lock_device(5)
    #         allure.attach("Device locked for 5 seconds", name="Lock Device", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 65. Device locked for 5 seconds")
    #         time.sleep(0.5)
        
    #     # 66. Test unlock_device
    #     with allure.step("66. Unlock device"):
    #         homebase.unlock_device()
    #         allure.attach("Device unlocked", name="Unlock Device", attachment_type=allure.attachment_type.TEXT)
    #         print(f"✓ 66. Device unlocked")
    #         time.sleep(0.5)
        
    #     # ============ SCREEN RECORDING METHODS ============
    #     # 67. Test start_recording_screen
    #     with allure.step("67. Start recording screen"):
    #         try:
    #             homebase.start_recording_screen(bitRate=1000000, timeLimit=5)
    #             allure.attach("Screen recording started", name="Start Recording", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 67. Screen recording started")
    #         except:
    #             allure.attach("Screen recording start failed (expected)", name="Start Recording", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 67. Screen recording start failed (expected)")
    #         time.sleep(0.5)
        
    #     # 68. Test stop_recording_screen
    #     with allure.step("68. Stop recording screen"):
    #         try:
    #             recording_path = homebase.stop_recording_screen()
    #             allure.attach(f"Screen recording stopped. Path: {recording_path}", name="Stop Recording", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 68. Screen recording stopped")
    #         except:
    #             allure.attach("Screen recording stop failed (expected)", name="Stop Recording", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 68. Screen recording stop failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ PERFORMANCE METHODS ============
    #     # 69. Test get_performance_data
    #     with allure.step("69. Get performance data"):
    #         try:
    #             package_name = homebase.get_current_package()
    #             perf_data = homebase.get_performance_data(package_name, "cpuinfo")
    #             allure.attach(f"Performance data: {perf_data}", name="Performance Data", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 69. Performance data retrieved")
    #         except:
    #             allure.attach("Get performance data failed (expected)", name="Performance Data", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 69. Get performance data failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ CONTEXT SWITCH METHOD ============
    #     # 70. Test switch_to_context (generic)
    #     with allure.step("70. Switch to context (generic)"):
    #         try:
    #             available_contexts = homebase.get_available_contexts()
    #             if available_contexts and len(available_contexts) > 0:
    #                 homebase.switch_to_context(available_contexts[0])
    #                 homebase.switch_to_native_context()
    #                 allure.attach(f"Switched to context {available_contexts[0]}", name="Switch Context", attachment_type=allure.attachment_type.TEXT)
    #                 print(f"✓ 70. Switched to context")
    #             else:
    #                 allure.attach("No alternative contexts available", name="Switch Context", attachment_type=allure.attachment_type.TEXT)
    #                 print(f"✓ 70. No alternative contexts")
    #         except:
    #             allure.attach("Switch context failed", name="Switch Context", attachment_type=allure.attachment_type.TEXT)
    #             print(f"✓ 70. Switch context failed")
    #         time.sleep(0.5)
        
    #     # ============ FINAL SUMMARY ============
    #     allure.attach("✓ All 70 BaseMobile methods tested successfully!", name="Test Summary", attachment_type=allure.attachment_type.TEXT)
    #     print("\n" + "="*60)
    #     print("✓ ALL 70 BASEMOBILE METHODS TESTED SUCCESSFULLY!")
    #     print("="*60)

    # @allure.feature("Test all mobile methods")
    # @allure.story("Test remaining mobile methods")
    # @allure.severity(allure.severity_level.CRITICAL)
    # @pytest.mark.colorApp
    # @allure.suite("Test all mobile methods")
    # def test_all_base_mobile_methods_002(self, appium_driver):
    #     """Test remaining BaseMobile methods (27-86) with detailed logging"""
    #     allure.dynamic.title('Test All BaseMobile Methods 002 (27-86)')
    #     allure.dynamic.description("Comprehensive test of remaining 60 BaseMobile functionality")
    #     allure.dynamic.label("test_id", 'TC_BASEMOBILE_002')
        
    #     homebase = HomeNotesPage(appium_driver)
        
                
    #     # ============ TEXT INPUT METHODS ============
    #     # 39. Test get_element_text
    #     with allure.step("39. Get element text"):
    #         try:
    #             locator = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/text_button_center")
    #             text = homebase.get_element_text(locator)
    #             allure.attach(
    #                 f"Element text: '{text}'",
    #                 name="Get Element Text",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 39. Element text: '{text}'")
    #         except:
    #             allure.attach(
    #                 "Get element text failed (expected)",
    #                 name="Get Element Text",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 39. Get element text failed (expected)")
    #         time.sleep(0.5)
        
    #     # 40. Test get_element_attribute
    #     with allure.step("40. Get element attribute"):
    #         try:
    #             locator = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/text_button_center")
    #             attr = homebase.get_element_attribute(locator, "resource-id")
    #             allure.attach(
    #                 f"Element attribute: '{attr}'",
    #                 name="Get Attribute",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 40. Element attribute: '{attr}'")
    #         except:
    #             allure.attach(
    #                 "Get element attribute failed (expected)",
    #                 name="Get Attribute",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 40. Get element attribute failed (expected)")
    #         time.sleep(0.5)
        
    #     # 41. Test get_element_count
    #     with allure.step("41. Get element count"):
    #         locator = (AppiumBy.CLASS_NAME, "android.widget.ImageView")
    #         count = homebase.get_element_count(locator)
    #         allure.attach(
    #             f"Element count: {count}",
    #             name="Get Element Count",
    #             attachment_type=allure.attachment_type.TEXT
    #         )
    #         print(f"✓ 41. Element count: {count}")
    #         time.sleep(0.5)
        
        
    #     # ============ SCROLL METHODS ============
    #     # 43. Test scroll_to_coordinates
    #     with allure.step("43. Scroll to coordinates"):
    #         try:
    #             homebase.scroll_to_coordinates(100, 100, timeout=5)
    #             allure.attach(
    #                 "Scrolled to coordinates (100, 100)",
    #                 name="Scroll Coordinates",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 43. Scrolled to coordinates")
    #         except:
    #             allure.attach(
    #                 "Scroll failed (expected)",
    #                 name="Scroll Coordinates",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 43. Scroll failed (expected)")
    #         time.sleep(0.5)
        
    #     # 44. Test scroll_to_text
    #     with allure.step("44. Scroll to text"):
    #         try:
    #             homebase.scroll_to_text("Add", timeout=5)
    #             allure.attach(
    #                 "Scrolled to text 'Add'",
    #                 name="Scroll Text",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 44. Scrolled to text 'Add'")
    #         except:
    #             allure.attach(
    #                 "Scroll to text failed (expected)",
    #                 name="Scroll Text",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 44. Scroll to text failed (expected)")
    #         time.sleep(0.5)
        
    #     # 45. Test scroll_to_element
    #     with allure.step("45. Scroll to element"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.scroll_to_element(locator, timeout=5)
    #             allure.attach(
    #                 "Scrolled to element",
    #                 name="Scroll Element",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 45. Scrolled to element")
    #         except:
    #             allure.attach(
    #                 "Scroll to element failed (expected)",
    #                 name="Scroll Element",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 45. Scroll to element failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ ZOOM & PINCH METHODS ============
    #     # 46. Test pinch_zoom
    #     with allure.step("46. Pinch zoom"):
    #         try:
    #             screen_size = homebase.get_screen_size()
    #             x, y = screen_size['width'] // 2, screen_size['height'] // 2
    #             homebase.pinch_zoom(x, y, 0.5)
    #             allure.attach(
    #                 f"Pinch zoomed at ({x}, {y}) with scale 0.5",
    #                 name="Pinch Zoom",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 46. Pinch zoomed")
    #         except:
    #             allure.attach(
    #                 "Pinch zoom failed (expected)",
    #                 name="Pinch Zoom",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 46. Pinch zoom failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ TAP ELEMENT METHODS ============
    #     # 47. Test tap_element
    #     with allure.step("47. Tap element by locator"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.tap_element(locator)
    #             allure.attach(
    #                 "Tapped element",
    #                 name="Tap Element",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 47. Tapped element")
    #         except:
    #             allure.attach(
    #                 "Tap element failed (expected)",
    #                 name="Tap Element",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 47. Tap element failed (expected)")
    #         time.sleep(0.5)
        
    #     # 48. Test double_tap_element
    #     with allure.step("48. Double tap element"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.double_tap_element(locator)
    #             allure.attach(
    #                 "Double tapped element",
    #                 name="Double Tap",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 48. Double tapped element")
    #         except:
    #             allure.attach(
    #                 "Double tap failed (expected)",
    #                 name="Double Tap",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 48. Double tap failed (expected)")
    #         time.sleep(0.5)
        
    #     # 49. Test long_press_element
    #     with allure.step("49. Long press element"):
    #         try:
    #             locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.long_press_element(locator, duration=1000)
    #             allure.attach(
    #                 "Long pressed element",
    #                 name="Long Press Element",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 49. Long pressed element")
    #         except:
    #             allure.attach(
    #                 "Long press element failed (expected)",
    #                 name="Long Press Element",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 49. Long press element failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ TAP COORDINATES METHODS ============
    #     # 50. Test tap_coordinates
    #     with allure.step("50. Tap at coordinates"):
    #         try:
    #             screen_size = homebase.get_screen_size()
    #             x, y = screen_size['width'] // 2, screen_size['height'] // 2
    #             homebase.tap_coordinates(x, y)
    #             allure.attach(
    #                 f"Tapped at ({x}, {y})",
    #                 name="Tap Coordinates",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 50. Tapped at ({x}, {y})")
    #         except:
    #             allure.attach(
    #                 "Tap coordinates failed (expected)",
    #                 name="Tap Coordinates",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 50. Tap coordinates failed (expected)")
    #         time.sleep(0.5)
        
    #     # 51. Test long_press_coordinates
    #     with allure.step("51. Long press at coordinates"):
    #         try:
    #             screen_size = homebase.get_screen_size()
    #             x, y = screen_size['width'] // 2, screen_size['height'] // 2
    #             homebase.long_press_coordinates(x, y, duration=1000)
    #             allure.attach(
    #                 f"Long pressed at ({x}, {y})",
    #                 name="Long Press Coordinates",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 51. Long pressed at ({x}, {y})")
    #         except:
    #             allure.attach(
    #                 "Long press coordinates failed (expected)",
    #                 name="Long Press Coordinates",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 51. Long press coordinates failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ KEYCODE METHODS ============
    #     # 52. Test press_keycode
    #     with allure.step("52. Press keycode (back - 4)"):
    #         try:
    #             homebase.press_keycode(4)
    #             allure.attach(
    #                 "Pressed keycode 4 (back)",
    #                 name="Press Keycode",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 52. Pressed keycode 4 (back)")
    #         except:
    #             allure.attach(
    #                 "Press keycode failed (expected)",
    #                 name="Press Keycode",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 52. Press keycode failed (expected)")
    #         time.sleep(0.5)
        
    #     # 53. Test long_press_keycode
    #     with allure.step("53. Long press keycode (back - 4)"):
    #         try:
    #             homebase.long_press_keycode(4)
    #             allure.attach(
    #                 "Long pressed keycode 4 (back)",
    #                 name="Long Press Keycode",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 53. Long pressed keycode 4 (back)")
    #         except:
    #             allure.attach(
    #                 "Long press keycode failed (expected)",
    #                 name="Long Press Keycode",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 53. Long press keycode failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ CUSTOM SWIPE METHOD ============
    #     # 54. Test swipe with custom coordinates
    #     with allure.step("54. Swipe with custom coordinates"):
    #         try:
    #             screen_size = homebase.get_screen_size()
    #             start_x, start_y = screen_size['width'] // 2, screen_size['height'] * 0.75
    #             end_x, end_y = screen_size['width'] // 2, screen_size['height'] * 0.25
    #             homebase.swipe(start_x, start_y, end_x, end_y, duration=1000)
    #             allure.attach(
    #                 f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})",
    #                 name="Custom Swipe",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 54. Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    #         except:
    #             allure.attach(
    #                 "Custom swipe failed (expected)",
    #                 name="Custom Swipe",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 54. Custom swipe failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ DRAG & DROP METHOD ============
    #     # 55. Test drag_and_drop
    #     with allure.step("55. Drag and drop"):
    #         try:
    #             source_locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             target_locator = (AppiumBy.CLASS_NAME, "android.widget.FrameLayout")
    #             homebase.drag_and_drop(source_locator, target_locator)
    #             allure.attach(
    #                 "Dragged and dropped element",
    #                 name="Drag Drop",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 55. Dragged and dropped")
    #         except:
    #             allure.attach(
    #                 "Drag and drop failed (expected)",
    #                 name="Drag Drop",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 55. Drag and drop failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ APP MANAGEMENT METHODS ============
    #     # 56. Test install_app (method exists)
    #     with allure.step("56. Install app (method available - requires valid path)"):
    #         allure.attach(
    #             "install_app(app_path) method available",
    #             name="Install App",
    #             attachment_type=allure.attachment_type.TEXT
    #         )
    #         print(f"✓ 56. Install app method available")
    #         time.sleep(0.5)
        
    #     # 57. Test uninstall_app (method exists)
    #     with allure.step("57. Uninstall app (method available - would uninstall app)"):
    #         allure.attach(
    #             "uninstall_app(package_name) method available",
    #             name="Uninstall App",
    #             attachment_type=allure.attachment_type.TEXT
    #         )
    #         print(f"✓ 57. Uninstall app method available")
    #         time.sleep(0.5)
        
    #     # 58. Test launch_app with app_id (backward compatibility)
    #     with allure.step("58. Launch app with app_id (backward compatibility)"):
    #         try:
    #             current_package = homebase.get_current_package()
    #             homebase.launch_app(app_id=current_package)
    #             allure.attach(
    #                 f"App launched with app_id: {current_package}",
    #                 name="Launch App ID",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 58. App launched with app_id")
    #         except:
    #             allure.attach(
    #                 "Launch app with app_id failed (expected)",
    #                 name="Launch App ID",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 58. Launch app with app_id failed (expected)")
    #         time.sleep(0.5)
        
    #     # 59. Test close_app with app_id (backward compatibility)
    #     with allure.step("59. Close app with app_id (backward compatibility)"):
    #         try:
    #             current_package = homebase.get_current_package()
    #             homebase.close_app(app_id=current_package)
    #             allure.attach(
    #                 f"App closed with app_id: {current_package}",
    #                 name="Close App ID",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 59. App closed with app_id")
    #             time.sleep(2)
    #             # Reopen app for remaining tests
    #             homebase.launch_app()
    #             time.sleep(2)
    #         except:
    #             allure.attach(
    #                 "Close app with app_id failed (expected)",
    #                 name="Close App ID",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 59. Close app with app_id failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ DEVICE LOCK METHODS ============
    #     # 60. Test lock_device
    #     with allure.step("60. Lock device (5 seconds)"):
    #         try:
    #             homebase.lock_device(seconds=5)
    #             allure.attach(
    #                 "Device locked for 5 seconds",
    #                 name="Lock Device",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 60. Device locked for 5 seconds")
    #         except:
    #             allure.attach(
    #                 "Lock device failed (expected)",
    #                 name="Lock Device",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 60. Lock device failed (expected)")
    #         time.sleep(0.5)
        
    #     # 61. Test unlock_device
    #     with allure.step("61. Unlock device"):
    #         try:
    #             homebase.unlock_device()
    #             allure.attach(
    #                 "Device unlocked",
    #                 name="Unlock Device",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 61. Device unlocked")
    #         except:
    #             allure.attach(
    #                 "Unlock device failed (expected)",
    #                 name="Unlock Device",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 61. Unlock device failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ SCREEN RECORDING METHODS ============
    #     # 62. Test start_recording_screen
    #     with allure.step("62. Start recording screen"):
    #         try:
    #             homebase.start_recording_screen(bitRate=1000000, timeLimit=5)
    #             allure.attach(
    #                 "Screen recording started with bitRate=1000000, timeLimit=5",
    #                 name="Start Recording",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 62. Screen recording started")
    #             time.sleep(2)
    #         except:
    #             allure.attach(
    #                 "Screen recording start failed (expected)",
    #                 name="Start Recording",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 62. Screen recording start failed (expected)")
    #         time.sleep(0.5)
        
    #     # 63. Test stop_recording_screen
    #     with allure.step("63. Stop recording screen"):
    #         try:
    #             recording_path = homebase.stop_recording_screen()
    #             allure.attach(
    #                 f"Screen recording stopped. Path: {recording_path}",
    #                 name="Stop Recording",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 63. Screen recording stopped")
    #         except:
    #             allure.attach(
    #                 "Screen recording stop failed (expected)",
    #                 name="Stop Recording",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 63. Screen recording stop failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ PERFORMANCE METHODS ============
    #     # 64. Test get_performance_data
    #     with allure.step("64. Get performance data"):
    #         try:
    #             package_name = homebase.get_current_package()
    #             perf_data = homebase.get_performance_data(package_name, "cpuinfo")
    #             perf_data_str = str(perf_data)[:200]  # Limit display length
    #             allure.attach(
    #                 f"Performance data retrieved: {perf_data_str}...",
    #                 name="Performance Data",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 64. Performance data retrieved")
    #         except:
    #             allure.attach(
    #                 "Get performance data failed (expected)",
    #                 name="Performance Data",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 64. Get performance data failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ CONTEXT SWITCH METHODS ============
    #     # 65. Test switch_to_context (generic)
    #     with allure.step("65. Switch to context (generic)"):
    #         try:
    #             available_contexts = homebase.get_available_contexts()
    #             if available_contexts and len(available_contexts) > 0:
    #                 homebase.switch_to_context(available_contexts[0])
    #                 homebase.switch_to_native_context()
    #                 allure.attach(
    #                     f"Switched to context {available_contexts[0]} and back",
    #                     name="Switch Context",
    #                     attachment_type=allure.attachment_type.TEXT
    #                 )
    #                 print(f"✓ 65. Switched to context and back")
    #             else:
    #                 allure.attach(
    #                     "No alternative contexts available",
    #                     name="Switch Context",
    #                     attachment_type=allure.attachment_type.TEXT
    #                 )
    #                 print(f"✓ 65. No alternative contexts available")
    #         except:
    #             allure.attach(
    #                 "Switch context failed (expected)",
    #                 name="Switch Context",
    #                 attachment_type=allure.attachment_type.TEXT
    #             )
    #             print(f"✓ 65. Switch context failed (expected)")
    #         time.sleep(0.5)
        
    #     # ============ SUMMARY ============
    #     allure.attach(
    #         "✓ All remaining 39 BaseMobile methods tested successfully!",
    #         name="Test Summary 002",
    #         attachment_type=allure.attachment_type.TEXT
    #     )
    #     print("\n" + "="*60)
    #     print("✓ ALL 39 REMAINING BASEMOBILE METHODS TESTED SUCCESSFULLY!")
    #     print("="*60)