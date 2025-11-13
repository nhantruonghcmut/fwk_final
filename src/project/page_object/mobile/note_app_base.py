from src.core.base.base_mobile import BaseMobile

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class IntroPage(BaseMobile):
    def __init__(self, driver):
        super().__init__(driver)
    STEP1_NEXT = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/step1_next")
    STEP2_NEXT = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/step2_next")
    PERMISS_ALLOW_BUTTON = (AppiumBy.ID, "com.android.packageinstaller:id/permission_allow_button")
    SKIP = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/btn_start_skip")
    BTN_START = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/btn_start")
    def skip_intro_use(self):
        self.get_element(self.STEP1_NEXT).click()
        if self.verify_element_present(self.STEP2_NEXT, 2):
            self.get_element(self.STEP2_NEXT).click()
            self.get_element(self.PERMISS_ALLOW_BUTTON).click()
        self.get_element(self.SKIP).click()

    def click_next(self):
        next_button = self.get_element(self.STEP1_NEXT)
        self.tap_element(next_button)

class HomeNotesPage(BaseMobile):
    def __init__(self, driver):
        super().__init__(driver)
    # Locators
    ADD_NOTE_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/bottom_fab")
    NOTES_LIST = (AppiumBy.XPATH, '//android.widget.TextView[@resource-id="com.socialnmobile.dictapps.notepad.color.note:id/text" and @text="Checklist"]')
    OPTION_BUTTON = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/text_button_center')
    MENU_BUTTON = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/main_btn3')
    COLOR_BUTTON = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/main_btn1')
    ITEM = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/background')
    ADD_TEXT = (AppiumBy.XPATH,'//android.widget.TextView[@resource-id="com.socialnmobile.dictapps.notepad.color.note:id/text" and @text="Text"]')
    ADD_CHECKLIST = (AppiumBy.XPATH,'//android.widget.TextView[@resource-id="com.socialnmobile.dictapps.notepad.color.note:id/text" and @text="Checklist"]')
    BOT_MENU_DELETE = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/bottom_menu_delete')
    BOT_MENU_ARCHIVE = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/bottom_menu_archive')
    BOT_MENU_REMINDER = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/bottom_menu_reminder')
    BOT_MENU_COLOR = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/bottom_menu_color')
    BOT_MENU_MORE = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/bottom_menu_more')
    OK = (AppiumBy.ID, "android:id/button1")
    CANCEL = (AppiumBy.ID, "android:id/button2")

    def count_notes(self):
        if self.verify_element_present(self.ITEM,5):
            notes = self.get_elements(self.ITEM)
            return len(notes)
        return 0           

    def find_note_have_title(self, title: str):
        notes = self.get_elements(self.ITEM)
        for note in notes:
            if note.get_element((AppiumBy.CLASS_NAME,'android.widget.TextView')).get_text() == title:
                return note
        return None
    def longtap_note_have_title(self, title: str, duration=1000):
        note = self.find_note_have_title(title)
        if note:
            note.long_tap(duration)
    def tap_bot_menu_option(self, option_name: str):
        option_dict = {
            "Delete": self.BOT_MENU_DELETE,
            "Archive": self.BOT_MENU_ARCHIVE,
            "Reminder": self.BOT_MENU_REMINDER,
            "Color": self.BOT_MENU_COLOR,
            "More": self.BOT_MENU_MORE
        }
        option_locator = option_dict.get(option_name)
        if option_locator:
            self.tap_element(option_locator)
        self.tap_element(self.OK)
    def is_note_exist(self, title: str):
        return self.find_note_have_title(title) is not None
    
    def add_new_note_text(self):
        self.get_element(self.ADD_NOTE_BUTTON).click()
        self.get_element(self.ADD_TEXT).click()
        return NoteTextTypePage(self.driver)
    
    def add_new_note_checklist(self):
        self.get_element(self.ADD_NOTE_BUTTON).click()
        self.get_element(self.ADD_CHECKLIST).click()
        return NoteChecklistTypePage(self.driver)
    def delete_note(self, title: str):
        note = self.find_note_have_title(title)
        pass

class NoteTextTypePage(BaseMobile):
    def __init__(self, driver):
        super().__init__(driver)
    # Locators
    HOME_NOTES_LIST = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/note_list")
    TITLE_FIELD = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/edit_title")
    COLOR_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/color_btn")
    MENU_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/menu_btn")
    DONE_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/back_btn")
    TEXT_BODY_FIELD = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/edit_note")
    UNDO = (AppiumBy.ID,"Undo")
    REDO = (AppiumBy.ID,"Redo")
    DATE_TIME_EDIT = (AppiumBy.ID,"com.socialnmobile.dictapps.notepad.color.note:id/datetime_absolute")
    STATUS = (AppiumBy.ID,"com.socialnmobile.dictapps.notepad.color.note:id/datetime_relative")
    color_dict = {"Red":1,"Orange":2,"Yellow":3,"Green":4,"Blue":5,"Purple":6,"Black":7,"Gray":8,"White":9}
    def enter_title(self, title):
        self.send_keys(self.TITLE_FIELD, title)
    def enter_body(self, body):
        self.send_keys(self.TEXT_BODY_FIELD, body)
    def tap_element_done(self):
        self.tap_element(self.DONE_BUTTON)
    def back_to_homenote(self):        
        while True:
            self.get_element(self.DONE_BUTTON).click()
            if self.verify_element_visible(self.HOME_NOTES_LIST, timeout=2):
                break
        
    def set_color_option(self, color_name):
        self.tap_element(self.COLOR_BUTTON)
        color_index = self.color_dict.get(color_name)
        if color_index:
            color_locator = (AppiumBy.ID, f"com.socialnmobile.dictapps.notepad.color.note:id/txt{color_index}']")
            self.tap_element(color_locator)
    def tap_element_undo(self):
        self.tap_element(self.UNDO)
    def tap_element_redo(self):
        self.tap_element(self.REDO)
    def get_status_text(self):
        return self.get_element(self.STATUS).get_text()
    def get_datetime_text(self):
        return self.get_element(self.DATE_TIME_EDIT).get_text()

class NoteChecklistTypePage(BaseMobile):
    def __init__(self, driver):
        super().__init__(driver)
    # Locators
    HOME_NOTES_LIST = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/note_list")
    VIEWLIST = (AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/viewlist')
    EDITLIST = (AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/editlist')
    EDIT_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/edit_btn")
    EDIT_TITLE = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/edit_title")
    VIEW_TITLE = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/view_title')
    COLOR_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/color_btn")
    MENU_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/menu_btn") 
    DONE_BUTTON = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/back_btn")  
    UNDO = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/btn_undo")
    REDO = (AppiumBy.ID, "com.socialnmobile.dictapps.notepad.color.note:id/btn_redo")
    ADD_FIRST = (AppiumBy.XPATH,'(//android.widget.TextView[@resource-id="com.socialnmobile.dictapps.notepad.color.note:id/text"])[1]') 
    # ADD_LAST = (AppiumBy.XPATH,'(//android.widget.TextView[@resource-id="com.socialnmobile.dictapps.notepad.color.note:id/text"])[last()]')
    ADD_ITEM_CONTAIN = (AppiumBy.ID,'com.socialnmobile.dictapps.notepad.color.note:id/edit')
    OK = (AppiumBy.ID, "android:id/button1")
    CANCEL = (AppiumBy.ID, "android:id/button2")
    NEXT = (AppiumBy.ID, "android:id/button3")
    DATE_TIME_EDIT = (AppiumBy.ID,"com.socialnmobile.dictapps.notepad.color.note:id/datetime_absolute")
    STATUS = (AppiumBy.ID,"com.socialnmobile.dictapps.notepad.color.note:id/datetime_relative")
    color_dict = {"Red":1,"Orange":2,"Yellow":3,"Green":4,"Blue":5,"Purple":6,"Black":7,"Gray":8,"White":9}
  
    def enter_title(self, title):
        self.send_keys(self.EDIT_TITLE, title)

    def add_first_checklist_item(self, item_text):
        if self.verify_element_visible(self.EDIT_BUTTON, 2):
            self.tap_element(self.EDIT_BUTTON)
        self.tap_element(self.ADD_FIRST)
        self.send_keys(self.ADD_ITEM_CONTAIN, item_text)
        self.tap_element(self.OK)

    def add_last_checklist_item(self, item_text):
        if self.verify_element_visible(self.EDIT_BUTTON, 2):
            self.tap_element(self.EDIT_BUTTON)
        edit_area = self.get_element(self.EDITLIST)
        itemslist = edit_area.get_elements((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/content'))
        itemslast = itemslist[-1]
        itemslast.click()
        self.send_keys(self.ADD_ITEM_CONTAIN, item_text)
        self.tap_element(self.OK)

    def longtap_item(self, item_text, duration=1000):
        items = self.get_elements((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/text'))
        for item in items:
            if item.get_text() == item_text:
                item.long_tap(duration)
                break
    def change_order_item(self, item_text, new_position):
        """
        position is start from 1
        """
        items = self.get_elements((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/content'))
        target_item = items[new_position].get_element((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/icon_drag'))

        for item in items:
            text = item.get_element((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/text')).get_text()
            if text == item_text:
                source_item = item.get_element((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/icon_drag'))
                break       
        source_item.drag_to(target_item)

    def tap_menu_checklist_item(self, menu_label):
        Xpath = (AppiumBy.XPATH, f'//android.widget.TextView[@resource-id="android:id/title" and @text="{menu_label}"]')
        self.tap_element(Xpath)

    def back_to_homenote(self):        
        while not self.verify_element_visible(self.HOME_NOTES_LIST, 2):
            self.tap_element(self.DONE_BUTTON)

    def set_color_option(self, color_name):
        self.tap_element(self.COLOR_BUTTON)
        color_index = self.color_dict.get(color_name)
        if color_index:
            color_locator = (AppiumBy.ID, f"com.socialnmobile.dictapps.notepad.color.note:id/txt{color_index}']")
            self.tap_element(color_locator)

    def click_to_view_checklist(self):
        self.tap_element(self.DONE_BUTTON)

    def click_to_edit_checklist(self):
        edit_btn = self.get_element(self.EDIT_BUTTON)
        edit_btn.click()
        # self.tap_element(self.EDIT_BUTTON)

    def delete_checklist_item(self, item_text):
        if self.verify_element_visible(self.EDIT_BUTTON, 2):
            self.tap_element(self.EDIT_BUTTON)
        item = self.get_element((AppiumBy.XPATH, f"//android.widget.LinearLayout[@resource-id='com.socialnmobile.dictapps.notepad.color.note:id/content']//android.widget.TextView[contains(@text, '{item_text}')]/.."))
        if item:
            delete_xpath= (AppiumBy.CLASS_NAME,"android.widget.RelativeLayout")
            delete_btn = item.get_element(delete_xpath)
            delete_btn.click()

    def count_checklist_items(self):
        if self.verify_element_visible(self.VIEWLIST, 2):
            viewlist = self.get_element(self.VIEWLIST)
            return len(viewlist.get_elements((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/container')))
        else:
            editlist = self.get_element(self.EDITLIST, 2)
            return len(editlist.get_elements((AppiumBy.ID, 'com.socialnmobile.dictapps.notepad.color.note:id/content')))-2
