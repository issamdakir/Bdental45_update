import bpy# type: ignore
from os.path import exists
from .utils import (BdentalConstants, get_bdental_version, update_is_availible)



def get_icon_value(icon_name: str) -> int:
    icon_items = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.items()
    icon_dict = {tup[1].identifier : tup[1].value for tup in icon_items}

    return icon_dict[icon_name]

class BDENTAL_PT_MainPanel(bpy.types.Panel):
    """Main Panel"""

    bl_idname = "BDENTAL_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = ""
    bl_options = {"HIDE_HEADER", "DEFAULT_CLOSED"}
    remote_version = update_is_availible()

    def draw(self, context):
        _props = context.scene.BDENTAL_Props
        
        if bpy.data.is_dirty or not bpy.data.filepath : save_alert=True 
        else : save_alert=False
        # Draw Addon UI :
        layout = self.layout
        box = layout.box()
        split = box.split(factor=0.5, align=True)
        coll = split.column(align=True)
        coll.alert = True
        coll.label(text=f"{BdentalConstants.ADDON_NAME} (ver. {BdentalConstants.ADDON_VER_DATE})")
        g = box.grid_flow(columns=2, align=True)
        g.operator("wm.bdental_support_telegram")
        g.operator("wm.bdental_remove_info_footer", icon="CANCEL")
        
        if self.remote_version :
            grid = box.grid_flow(columns=1, align=True)
            grid.alert = True
            grid.label(text=f"new version availible :{self.remote_version} ")
            grid.operator("wm.bdental_checkupdate", text="Check for Updates", icon="FILE_REFRESH")
        
        
        
        # g = box.grid_flow(columns=1, align=True)
        # g.operator("wm.bdental_draw_tester")

        if not bpy.data.filepath:
            box = layout.box()
            split = box.split(factor=0.5, align=True)

            coll = split.column(align=True)
            coll.alert = True
            coll.operator("wm.bdental_new_project")

            coll = split.column(align=True)
            coll.operator("wm.open_mainfile")

            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")
            
        else :
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.operator("wm.open_mainfile")

            g = box.grid_flow(columns=2, align=True)
            g.alert = save_alert
            g.operator("wm.save_mainfile", text="Save", icon="FOLDER_REDIRECT")
            g.operator("wm.save_as_mainfile", text="Save As...", icon="FILE_BLEND")

            g = box.grid_flow(columns=2, align=True)
            g.operator("wm.bdental_import_mesh", icon="IMPORT")
            g.operator("wm.bdental_export_mesh", icon="EXPORT")

class BDENTAL_PT_DicomPanel(bpy.types.Panel):
    """Dicom Panel"""

    bl_idname = "BDENTAL_PT_DicomPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = "DICOM"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        BDENTAL_Props = context.scene.BDENTAL_Props
        layout = self.layout
        
        if not bpy.data.filepath:
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")


        else :
            box = layout.box()
            g = box.grid_flow(columns=2, align=True)           
            g.prop(BDENTAL_Props, "dicomDataType", text="")
            if BDENTAL_Props.dicomDataType == "DICOM Series":
                g.prop(BDENTAL_Props, "UserDcmDir", text="")           
            elif BDENTAL_Props.dicomDataType == "3D Image File":
                g.prop(BDENTAL_Props, "UserImageFile", text="")

            split = box.split(factor=0.4, align=True)
            coll = split.column(align=True)
            coll.label(text="Visualisation Options")
            coll = split.column(align=True)
            coll.prop(BDENTAL_Props, "visualisation_mode", text="")
            
            g = box.grid_flow(columns=1, align=False)
            g.operator("wm.bdental_dicom_reader", text="Read DICOM", icon="IMPORT")
            
            
            
            if context.object and context.object.get(BdentalConstants.BDENTAL_TYPE_TAG) == BdentalConstants.PCD_OBJECT_TYPE:
                box = layout.box()
                g = box.grid_flow(columns=1, align=True)
                g.prop(BDENTAL_Props, "ThresholdMin", text="threshold", slider=True)

                box.label(text="Point cloud settings :")
                g = box.grid_flow(columns=2, align=True)
                g.prop(BDENTAL_Props, "pcd_point_radius", text="Point radius", slider=True)
                g.prop(BDENTAL_Props, "pcd_point_auto_resize", text="Auto resize")

                g = box.grid_flow(columns=1, align=True)
                
                g.prop(BDENTAL_Props, "pcd_points_opacity", text="Opacity", slider=True)
                g.prop(BDENTAL_Props, "pcd_points_emission", text="Emission", slider=True)

            else :
                g = box.grid_flow(columns=1, align=True)
                g.prop(BDENTAL_Props, "ThresholdMin", text="threshold", slider=True)
                

            box.separator()

            g = box.grid_flow(columns=2, align=True)
            g.prop(BDENTAL_Props, "SegmentColor", text="")
            g.operator("wm.bdental_dicom_to_mesh", text="DICOM to Mesh", icon="MESH_CUBE")

class BDENTAL_PT_SlicesPanel(bpy.types.Panel):
    """Slices Panel"""

    bl_idname = "BDENTAL_PT_SlicesPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = "SLICES"
    bl_options = {"DEFAULT_CLOSED"}

    # @classmethod
    # def poll(cls, context):
    #     if context.screen.name == "Bdental Slicer" :
    #         return True
    #     else:
    #         return False

    def draw(self, context):
        # if context.screen.name != "Bdental Slicer" :
        #     return
        BDENTAL_Props = context.scene.BDENTAL_Props
        layout = self.layout
        
        if not bpy.data.filepath:
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")


        else :
            box = layout.box()
            row = box.row()
            row.operator("wm.bdental_volume_slicer",text="Update Dicom Slices", icon="EMPTY_AXIS")
            row.prop(BDENTAL_Props, "slicesColorThresholdBool", text="Slices Label")

                    
            row = box.row()
            row.alert = True 
            mats = [mat for mat in bpy.data.materials if "_SLICE_mat" in mat.name]
            if not mats:
                row.alert = False 
                    
            row.prop(BDENTAL_Props, "slices_brightness", text="Brightness")
            row.prop(BDENTAL_Props, "slices_contrast", text="Contrast")
                    
            row = box.row()
            row.label(text="Axial Slice Flip :")

            row = box.row()
            row.operator("wm.bdental_flip_camera_axial_90_plus", icon="PLUS")
            row.operator("wm.bdental_flip_camera_axial_90_minus", icon="REMOVE")
            row.operator("wm.bdental_flip_camera_axial_up_down", icon="TRIA_UP")
            row.operator("wm.bdental_flip_camera_axial_left_right", icon="TRIA_RIGHT")

            row = box.row()
            row.label(text="Coronal Slice Flip :")

            row = box.row()
            row.operator("wm.bdental_flip_camera_coronal_90_plus", icon="PLUS")
            row.operator("wm.bdental_flip_camera_coronal_90_minus", icon="REMOVE")
            row.operator("wm.bdental_flip_camera_coronal_up_down", icon="TRIA_UP")
            row.operator("wm.bdental_flip_camera_coronal_left_right", icon="TRIA_RIGHT")

            row = box.row()
            row.label(text="Sagittal Slice Flip :")

            row = box.row()
            row.operator("wm.bdental_flip_camera_sagittal_90_plus", icon="PLUS")
            row.operator("wm.bdental_flip_camera_sagittal_90_minus", icon="REMOVE")
            row.operator("wm.bdental_flip_camera_sagittal_up_down", icon="TRIA_UP")
            row.operator("wm.bdental_flip_camera_sagittal_left_right", icon="TRIA_RIGHT")

class BDENTAL_PT_ToolsPanel(bpy.types.Panel):
    """Tools Panel"""

    bl_idname = "BDENTAL_PT_ToolsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = "TOOLS"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        BDENTAL_Props = context.scene.BDENTAL_Props
        layout = self.layout
        ob = context.object
        if not bpy.data.filepath:
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")


        else :
            # Model color :
            if ob and ob.type in ["MESH", "CURVE"]:
                try :
                    mat = ob.active_material
                    box = layout.box()
                    
                    grid = box.grid_flow(columns=2, align=True)
                    
                    if mat :
                        grid.prop(mat, "diffuse_color", text="")
                    else :
                        grid.template_icon(get_icon_value("COLORSET_12_VEC"), scale=1.5)
                    grid.label(text="COLOR")#icon=yellow_point
                    

                    grid = box.grid_flow(columns=2, align=True)
                    grid.operator("wm.bdental_add_color", text="Add Color", icon="MATERIAL")
                    # grid.template_ID(context.object, "active_material",new="material.new",live_icon=0)
                    if mat :
                        grid.operator("wm.bdental_remove_color", text="Remove Color")
                    else :
                        grid.operator("wm.bdental_remove_color", text="Remove Color")
                except :
                    pass

            box = layout.box()
            grid = box.grid_flow(columns=2, align=True)
            grid.label(text="RELATIONS")
            grid.template_icon(get_icon_value("LINKED"), scale=1.5)

            grid = box.grid_flow(columns=2, align=True)
            grid.operator("wm.bdental_parent_object", text="Parent", icon="LINKED")
            grid.operator("wm.bdental_join_objects", text="Join", icon="SNAP_FACE")
            grid.operator("wm.bdental_lock_objects", text="Lock", icon="LOCKED")

            
            grid.operator("wm.bdental_unparent_objects", text="Un-Parent", icon="LIBRARY_DATA_OVERRIDE")
            grid.operator("wm.bdental_separate_objects", text="Separate", icon="SNAP_VERTEX")
            grid.operator("wm.bdental_unlock_objects", text="Un-Lock", icon="UNLOCKED")

            # Model Repair Tools :
            # layout.separator()
            
            box = layout.box()
            grid = box.grid_flow(columns=2, align=True)
            grid.label(text="REPAIR")  
            grid.template_icon(get_icon_value("TOOL_SETTINGS"), scale=1.5)

            grid = box.grid_flow(columns=2, align=True)

            grid.operator("wm.bdental_decimate", text="Decimate", icon="MOD_DECIM")
            grid.operator("wm.bdental_clean_mesh2", text="Clean Mesh", icon="BRUSH_DATA")
            grid.operator("wm.bdental_retopo_smooth", text="Retopo-Smooth", icon="SMOOTHCURVE")
            grid.operator("wm.bdental_normals_toggle")

            grid.prop(BDENTAL_Props, "decimate_ratio", text="")
            grid.operator("wm.bdental_voxelremesh", text="Remesh", icon="MOD_REMESH")
            if ob and ob.mode == "SCULPT":
                try : grid.operator("sculpt.sample_detail_size", text="", icon="EYEDROPPER")
                except : grid.operator("wm.bdental_fill", text="Fill", icon="OUTLINER_OB_LIGHTPROBE")
            else : grid.operator("wm.bdental_fill", text="Fill", icon="OUTLINER_OB_LIGHTPROBE")
            grid.operator("wm.bdental_flip_normals")


            # Cutting Tools :
            # layout.row().separator()
            box = layout.box()
            g = box.grid_flow(columns=2, align=True)
            g.label(text="CUT") 
            g.template_icon(get_icon_value("COLOR"), scale=1.5)
            
            g = box.grid_flow(columns=1, align=True)
            g.prop(BDENTAL_Props, "Cutting_Tools_Types_Prop", text="Cutters")
            if BDENTAL_Props.Cutting_Tools_Types_Prop == "Path Split" :
                g = box.grid_flow(columns=2, align=True)
                g.operator("wm.bdental_curvecutteradd2", text="Add Cutter", icon="GP_SELECT_STROKES")
                g.operator(
                    "wm.bdental_curvecutter2_cut_new",
                    text="Perform Cut",
                    icon="GP_MULTIFRAME_EDITING",
                )

            elif BDENTAL_Props.Cutting_Tools_Types_Prop == "Ribbon Split":
                g = box.grid_flow(columns=2, align=True)
                g.operator("wm.bdental_curvecutter1_new", text="Add Cutter", icon="GP_SELECT_STROKES")
                
                g.operator("wm.bdental_curvecutter1_new_perform_cut", text="Perform Cut", icon="GP_MULTIFRAME_EDITING")
            

            elif BDENTAL_Props.Cutting_Tools_Types_Prop == "Ribbon Cutter":
                g = box.grid_flow(columns=2, align=True)
                g.operator(
                    "wm.bdental_ribboncutteradd", text="Add Cutter", icon="GP_SELECT_STROKES"
                )
                g.operator(
                    "wm.bdental_ribboncutter_perform_cut",
                    text="Perform Cut",
                    icon="GP_MULTIFRAME_EDITING",
                )
            elif BDENTAL_Props.Cutting_Tools_Types_Prop == "Frame Cutter":

                g = box.grid_flow(columns=2, align=True)
                g.prop(BDENTAL_Props, "cutting_mode", text="Cutting Mode")
                g.operator("wm.bdental_add_square_cutter", text="Frame Cutter")
                

            # elif BDENTAL_Props.Cutting_Tools_Types_Prop == "Paint Cutter":

            #     row = box.row()
            #     row.operator("wm.bdental_paintarea_toggle", text="Add Cutter")
            #     row.operator("wm.bdental_paintarea_plus", text="", icon="ADD")
            #     row.operator("wm.bdental_paintarea_minus", text="", icon="REMOVE")
            #     row = box.row()
            #     row.operator("wm.bdental_paint_cut", text="Perform Cut")
            
            # elif BDENTAL_Props.Cutting_Tools_Types_Prop == "Path Cutter":
            #     row = box.row()
            #     row.operator("wm.bdental_add_path_cutter")

            if context.object and context.object.get("bdental_type"):
                
                obj = context.object
                if obj.get("bdental_type") in ["curvecutter1", "curvecutter2"] :
                    g = box.grid_flow(columns=2, align=True)
                    g.prop(obj.data, "extrude", text="Extrude")
                    g.prop(obj.data, "offset", text="Offset")
                elif obj.get("bdental_type") == "curvecutter3" :
                    g = box.grid_flow(columns=3, align=True)
                    g.prop(obj.data, "extrude", text="Extrude")
                    g.prop(obj.data, "bevel_depth", text="Bevel")
                    g.prop(obj.data, "offset", text="Offset")

            # Make BaseModel, survey, Blockout :
            # layout.separator()
            
            box = layout.box()
            grid = box.grid_flow(columns=2, align=True)
            grid.label(text="MODEL")
            grid.template_icon(get_icon_value("FILE_VOLUME"), scale=1.5)

            grid = box.grid_flow(columns=2, align=True)

            grid.operator("wm.bdental_model_base", text="Make Model Base")
            grid.operator("wm.bdental_undercuts_preview", text="Preview Undercuts")

            grid.operator("wm.bdental_add_offset", text="Add Offset")
            grid.operator("wm.bdental_blockout_new", text="Blocked Model")
            
            # layout.separator()
            
            # box = layout.box()
            # grid = box.grid_flow(columns=2, align=True)
            # grid.label(text="TEETH")
            # grid.template_icon(get_icon_value("OUTLINER_OB_LATTICE"), scale=1.5)

            # grid = box.grid_flow(columns=2, align=True)
            # grid.prop(BDENTAL_Props, "TeethLibrary", text="")
            # grid.operator("wm.bdental_add_teeth")

            box = layout.box()
            grid = box.grid_flow(columns=2, align=True)
            grid.label(text="TEXTE")
            grid.template_icon(get_icon_value("SMALL_CAPS"), scale=1.5)

            grid = box.grid_flow(columns=2, align=True)
            grid.prop(BDENTAL_Props, "text", text="")
            grid.operator("wm.bdental_add_3d_text", text="Add 3D Text")

class BDENTAL_PT_ImplantPanel(bpy.types.Panel):
    """ Implant panel"""

    bl_idname = "BDENTAL_PT_ImplantPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = "IMPLANT"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        
        layout = self.layout
        
        if not bpy.data.filepath:
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")


        else :
            box = layout.box()
            # box.label(text="IMPLANT")#icon=yellow_point
            g = box.grid_flow(columns=3, align=True)
            
            g.operator("wm.bdental_slices_pointer_select", text="Select Pointer", icon="EMPTY_AXIS")
            g.operator("wm.bdental_fly_to_implant_or_fixing_sleeve", text="", icon="TRIA_LEFT").direction = "previous"
            g.operator("wm.bdental_fly_to_implant_or_fixing_sleeve", text="", icon="TRIA_RIGHT").direction = "next"
            

            g = box.grid_flow(columns=2, align=True)

            g.operator("wm.bdental_add_implant", text="Add Implant", icon="ADD")
            g.operator("wm.bdental_remove_implant", text="Remove Implant" , icon="REMOVE")
            
            g = box.grid_flow(columns=1, align=True)
            g.operator("wm.add_fixing_pin")

            g = box.grid_flow(columns=2, align=True)
            g.operator("wm.bdental_lock_object_to_pointer")
            g.operator("wm.bdental_unlock_object_from_pointer")

            g = box.grid_flow(columns=2, align=True)
            g.operator("wm.bdental_object_to_pointer", text="Active to Pointer")
            g.operator("wm.bdental_pointer_to_active", text="Pointer to Active")

            g = box.grid_flow(columns=1, align=True)
            g.operator("wm.bdental_align_objects_axes", text="Align Axes")
              
class BDENTAL_PT_Guide(bpy.types.Panel):
    """ Guide Panel"""

    bl_idname = "BDENTAL_PT_Guide"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = "SURGICAL GUIDE"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        BDENTAL_Props = context.scene.BDENTAL_Props
        layout = self.layout
        if not bpy.data.filepath:
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")


        else :

            box = layout.box()
            row = box.row()
            # row.operator("wm.bdental_add_guide_splint")
            row.operator("wm.bdental_add_guide_splint_geom")
            row = box.row()
            row.operator("wm.bdental_add_tube")
            row.prop(BDENTAL_Props, "TubeCloseMode", text="")

            if context.active_object:
                if (
                    "BDENTAL_GuideTube" in context.active_object.name
                    and context.active_object.type == "CURVE"
                ):
                    obj = context.active_object
                    row = box.row()
                    row.prop(obj.data, "bevel_depth", text="Radius")
                    row.prop(obj.data, "extrude", text="Extrude")
                    row.prop(obj.data, "offset", text="Offset")

            # row = box.row()
            # row.operator("wm.bdental_add_guide_cutters_from_sleeves")

            row = box.row()
            row.operator("wm.bdental_guide_add_component")
            
            # row = box.row()
            # row.operator("wm.bdental_set_guide_components", icon="PLUS")
            # row = box.row()
            # row.operator("wm.bdental_guide_set_cutters", icon="REMOVE")
            

            
            
            row = box.row()
            row.operator("wm.bdental_guide_finalise")
            row = box.row()
            row.operator("wm.bdental_guide_finalise_geonodes")
        
####################################################################
class BDENTAL_PT_Align(bpy.types.Panel):
    """ALIGN Panel"""

    bl_idname = "BDENTAL_PT_Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = "ALIGN"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        BDENTAL_Props = context.scene.BDENTAL_Props
        layout = self.layout

        if not bpy.data.filepath:
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")


        else :
            box = layout.box()

            row = box.row()
            row.operator("wm.bdental_auto_align")
            
            g = box.grid_flow(columns=2, align=True)
            g.operator("wm.bdental_alignpoints", text="ALIGN Points")
            g.operator("wm.bdental_alignpointsinfo", text="INFO", icon="INFO")

            is_ready = context.object and context.object in context.selected_objects and len(context.selected_objects)==2
            txt = []
            if BDENTAL_Props.AlignModalState:
                txt = ["WAITING FOR ALIGNEMENT..."]

            elif is_ready :
                target_name = context.object.name
                src_name = [
                    obj
                    for obj in context.selected_objects
                    if not obj is context.object
                ][0].name

                txt = ["READY FOR ALIGNEMENT.", f"{src_name} will be aligned to, {target_name}"]

            else:
                txt = ["STANDBY MODE"]

            #########################################
            if txt :
                b2 = box.box()
                b2.alert = True

                for t in txt :
                    b2.label(text=t)
            
            # Align Tools :
            box = layout.box()
            g = box.grid_flow(columns=3, align=True)
            g.operator("wm.bdental_align_to_front", text="Align To Me", icon="AXIS_FRONT")
            g.operator("wm.bdental_to_center", text="Move To Center", icon="SNAP_FACE_CENTER")
            g.operator("wm.bdental_align_to_active", text="Align To Active")
            
            # row.operator("wm.bdental_align_to_cursor", text="Move To Cursor", icon="AXIS_FRONT")
            
            g = box.grid_flow(columns=2, align=True)
            g.operator("wm.bdental_occlusalplane", text="OCCLUSAL PLANE")
            g.operator("wm.bdental_occlusalplaneinfo", text="INFO", icon="INFO")

            g = box.grid_flow(columns=2, align=True)
            g.operator("wm.bdental_add_reference_planes", text="Ref planes")
            #Auto align :
            # box = layout.box()
            # row = box.row()
            # row.operator("wm.bdental_auto_align_icp", text="AUTO ALIGN")

class BDENTAL_PT_BLibrary(bpy.types.Panel):
    """ Bdental Library Panel"""

    bl_idname = "BDENTAL_PT_BLibrary"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"  # blender 2.7 and lower = TOOLS
    bl_category = BdentalConstants.ADDON_NAME
    bl_label = "LIBRARY"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        if not bpy.data.filepath:
            box = layout.box()
            g = box.grid_flow(columns=1, align=True)
            g.alert = True
            g.label(text="Please add new Project, or open existing one.")


        else :
            box = layout.box()
            grid = box.grid_flow(columns=1, align=True)
            grid.operator("wm.bdental_asset_browser_toggle")
            grid.operator("wm.add_custom_sleeve_cutter")
            

##########################################################################################
# Registration :
##########################################################################################

classes = [
    BDENTAL_PT_MainPanel,
    # BDENTAL_PT_GeneralPanel,
    BDENTAL_PT_DicomPanel,
    # BDENTAL_PT_SegmentationPanel,
    BDENTAL_PT_SlicesPanel,
    BDENTAL_PT_ImplantPanel,
    BDENTAL_PT_Align,
    BDENTAL_PT_ToolsPanel,
    BDENTAL_PT_BLibrary,
    BDENTAL_PT_Guide,
   
]


def register():
    global ADDON_VER_DATE
    ADDON_VER_DATE = get_bdental_version(filepath=BdentalConstants.ADDON_VER_PATH)

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

