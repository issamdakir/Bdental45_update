bl_info = {
    "name": "Bdental-4.5",  
    "author": "Dr. Essaid Issam Dakir DMD\n,Dr. Ilya Fomenco DMD\n, Dr. Krasouski Dmitry DMD",
    "version": (4, 5, 0),
    "blender": (4, 5, 0),  
    "location": "3D View -> UI SIDE PANEL ",
    "description": "3D Digital Dentistry",  
    "warning": "",
    "doc_url": "",
    # "tracker_url": "https://t.me/bdental3",
    "category": "Dental",  
}
#############################################################################################
# IMPORTS :
#############################################################################################
import shutil
import os
import bpy # type: ignore
import zipfile
from os.path import join, abspath,exists, isdir
from time import sleep
import tempfile
import requests
from requests.exceptions import HTTPError, Timeout, RequestException
from .utils import (
    BDENTAL_GpuDrawText,
    BDENTAL_OT_BdentalModulesPipInstaller,
    BdentalConstants,
    bdental_log,
    add_bdental_libray,
    set_modules_path,
    isConnected,
    BdentalColors,
    browse,
    get_bdental_version,
    import_required_modules,
    addon_update_preinstall,
    get_update_version,
    addon_update_download
)
ERROR_MESSAGE = []
ERROR_PANEL = False

set_modules_path()

def addon_download():
    message = []
    _dir = None 
    try :
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        bdental_zip_local = join(temp_dir,'Bdental-3.zip')

        # Download the file
        with requests.get(BdentalConstants.REPO_URL, stream=True, timeout=10) as r:
            try:
                r.raise_for_status()
            except HTTPError as http_err:
                txt = "HTTP error occurred"
                print(f"{txt} : {http_err}")
                message.extend([txt])
                return message,_dir
            except ConnectionError as conn_err:
                txt = "Connection error occurred"
                print(f"{txt} : {conn_err}")
                message.extend([txt])
                return message,_dir
            except Timeout as timeout_err:
                txt = "Timeout error occurred"
                print(f"{txt} : {timeout_err}")
                message.extend([txt])
                return message,_dir
            except RequestException as req_err:
                txt = f"Error during requests to {BdentalConstants.REPO_URL}"
                print(f"{txt} : {req_err}")
                message.extend([txt])
                return message,_dir
            
            with open(bdental_zip_local, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        
        
        try :
            with zipfile.ZipFile(bdental_zip_local, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile as zip_err:
            txt = "Error occurred while extracting the downloaded addon ZIP file"
            print(f"{txt} : {zip_err}")
            message.extend([txt])
            return message,_dir
        
        src = [abspath(e) for e in os.listdir(temp_dir) if isdir(abspath(e))][0]
        _dir = join(temp_dir,"Bdental-3")
        os.rename(src,_dir)

    except OSError as os_err:
        print(f"OS error occurred: {os_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}") 
    return message,_dir

class BDENTAL_OT_SupportTelegram(bpy.types.Operator):
        """ open telegram bdental support link"""

        bl_idname = "wm.bdental_support_telegram"
        bl_label = "Bdental Support (Telegram)"

        #### this freezes blender ui !! ###
        # @classmethod
        # def poll(cls, context):
        #     return isConnected()
        ###################################


        def execute(self, context):
            browse(BdentalConstants.TELEGRAM_LINK)
            
            return{"FINISHED"}

class BDENTAL_OT_AddBdentalLibrary(bpy.types.Operator):
    """ add bdental library """

    bl_idname = "wm.bdental_add_bdental_library"
    bl_label = "Add Bdental Library"
    def execute(self, context):
        with context.temp_override(window=context.window_manager.windows[0]):
            message = ["Adding Bdental library..."]
            BDENTAL_GpuDrawText(message)
            sleep(1)
            message, success = add_bdental_libray()
            if not success and message :
                BDENTAL_GpuDrawText(message_list=message,rect_color=BdentalColors.red)
                sleep(3)
                BDENTAL_GpuDrawText()
                return {"CANCELLED"}


            message = ["FINISHED"]
            BDENTAL_GpuDrawText(message_list=message,rect_color=BdentalColors.green)
            sleep(2)
            BDENTAL_GpuDrawText()
            return {"FINISHED"}
    
class BdentalAddonPreferences(bpy.types.AddonPreferences):
        bl_idname = __name__

        def draw(self, context):
            layout = self.layout
            box = layout.box()
            row = box.row()
            row.operator("wm.bdental_add_app_template", text="Bdental as template",icon="SETTINGS")
            row = box.row()
            row.operator("wm.bdental_set_config", text="Bdental as default", icon="TOOL_SETTINGS")
            row = box.row()
            row.operator("wm.bdental_add_bdental_library", text="Add Bdental Library", icon="TOOL_SETTINGS")

class BDENTAL_OT_checkUpdate(bpy.types.Operator):
    """ check addon update """

    bl_idname = "wm.bdental_checkupdate"
    bl_label = "check update"
    bl_options = {"REGISTER", "UNDO"}

    txt = []
    restart = 0
    
    def modal(self, context, event):
        if not event.type in {'ESC', 'RET'}:
            return {'PASS_THROUGH'}

        elif event.type in {'ESC'}:
            BDENTAL_GpuDrawText(message_list=["Cancelled."], sleep_time=1)
            return {'CANCELLED'}
        
        elif event.type in {'RET'} and event.value == "PRESS":
            BDENTAL_GpuDrawText(message_list=["Downloading..."])
            _message, update_root = addon_update_download()
            if _message :
                BDENTAL_GpuDrawText(message=_message, rect_color=BdentalColors.red, sleep_time=2)
                return{"CANCELLED"}
            
            BDENTAL_GpuDrawText(message_list=["Preparing update..."])
            addon_update_preinstall(update_root)
            add_bdental_libray()
            BDENTAL_GpuDrawText(message_list=["Please restart blender to finalize Bdental update."], rect_color=BdentalColors.green)
            return {'FINISHED'}
        return {'RUNNING_MODAL'}
        

    def invoke(self, context, event):
        addon_version = BdentalConstants.ADDON_VER_DATE
        if addon_version == "####" :
            info_txt_list = ["Can't get current version!"]
            BDENTAL_GpuDrawText(message_list=info_txt_list, rect_color=BdentalColors.red, sleep_time=2)
            bdental_log(info_txt_list)
            return{"CANCELLED"}

        if not isConnected() :
            info_txt_list = ["Bdental update error : Please check internet connexion !"]
            bdental_log(info_txt_list)
            BDENTAL_GpuDrawText(message_list=info_txt_list, rect_color=BdentalColors.red, sleep_time=2)
            return{"CANCELLED"}
        
        update_version,success,error_txt_list = get_update_version()
            
        if not success :
            BDENTAL_GpuDrawText(message_list=error_txt_list, rect_color=BdentalColors.red, sleep_time=2)
            return{"CANCELLED"}
        
        if update_version <= addon_version :
            txt_list = ["Bdental is up to date."]
            bdental_log(txt_list)
            BDENTAL_GpuDrawText(message_list=txt_list, rect_color=BdentalColors.green, sleep_time=2)
            return{"CANCELLED"}
        
        txt_list = [f"Current version = {addon_version}, New version = {update_version}",
                    "<ENTER> : to install last update / <ESC> : to cancel"]
        BDENTAL_GpuDrawText(message_list=txt_list, rect_color=BdentalColors.yellow)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class BDENTAL_PT_ModulesErrorPanel(bpy.types.Panel):
    """ Modules error panel"""

    bl_idname = "BDENTAL_PT_ModulesErrorPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI" 
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = f"{BdentalConstants.ADDON_NAME} (ver. {BdentalConstants.ADDON_VER_DATE})"

    def draw(self, context):

        layout = self.layout
        
        box = layout.box()
        grid = box.grid_flow(columns=1, align=True)
        grid.alert = True
        for l in ERROR_MESSAGE :
            grid.label(text=l)
        grid = box.grid_flow(columns=2, align=True)
        grid.operator("wm.bdental_checkupdate")
        grid.operator("wm.bdental_support_telegram")
        grid = box.grid_flow(columns=1, align=True)
        grid.operator("wm.bdental_modules_pip_installer")

###################################################
txt_list = [f"{bl_info.get('name')} started version : {BdentalConstants.ADDON_VER_DATE}"]
bdental_log(txt_list)

new_modules = join(BdentalConstants.RESOURCES, "bdental_modules")
if exists(new_modules) :
    sleep(3)
    if exists(BdentalConstants.BDENTAL_MODULES_PATH):
        shutil.rmtree(BdentalConstants.BDENTAL_MODULES_PATH)

    shutil.move(new_modules, BdentalConstants.ADDON_DIR)



# if not exists(BdentalConstants.BDENTAL_MODULES_PATH) :
#     ERROR_PANEL = True
#     ERROR_MESSAGE.extend([
#             "Bdental Modules are not installed properly",
#             "Please install bdental required modules online or",
#             "contact support",
#         ])

if not ERROR_PANEL :
    
    missing_modules = import_required_modules(BdentalConstants.REQ_DICT)
    if missing_modules :
        ERROR_PANEL = True
        ERROR_MESSAGE.extend([
            "Bdental Modules are not installed properly",
            "Please install bdental required modules online or",
            "contact support",
        ])

if ERROR_PANEL :
    addon_modules = []
    init_classes = [
            BDENTAL_OT_SupportTelegram,
            BDENTAL_OT_checkUpdate,
            BDENTAL_PT_ModulesErrorPanel,
            BDENTAL_OT_BdentalModulesPipInstaller,

            
        ]
    def register():
        
        for module in addon_modules:
            module.register()
        for cl in init_classes:
            bpy.utils.register_class(cl)

    def unregister():
        
        for cl in reversed(init_classes):
            bpy.utils.unregister_class(cl)
        for module in reversed(addon_modules):
            module.unregister()
else:
    
    from . import BDENTAL_Props, BDENTAL_Panel
    from .Operators import (
        BDENTAL_Operators, looptools
    )
    addon_modules = [
    BDENTAL_Props,
    BDENTAL_Panel,
    BDENTAL_Operators,
    looptools
    
    ]
    init_classes = [
        BDENTAL_OT_SupportTelegram,
        BDENTAL_OT_AddBdentalLibrary,
        BDENTAL_OT_checkUpdate,
        BdentalAddonPreferences,
        
        ]

    def register():
        
        for module in addon_modules:
            module.register()
        for cl in init_classes:
            bpy.utils.register_class(cl)

    def unregister():
        for cl in reversed(init_classes):
            bpy.utils.unregister_class(cl)
        for module in reversed(addon_modules):
            module.unregister()
        

if __name__ == "__main__":
    register()
