import os
import glob
from datetime import datetime
import flet as ft

def main(page: ft.Page):
    # 📱 1. 基本設定
    page.title = "智慧巡檢 App V1"
    page.padding = 0 

    # 📷 加入底層的「原生系統呼叫器」
    def on_photo_picked(e: ft.FilePickerResultEvent):
        nonlocal current_step, retake_target
        if e.files and len(e.files) > 0:
            photo_path = e.files[0].path
            if retake_target > 0:
                captured_photos[retake_target - 1] = photo_path
                retake_target = 0 
                show_review_panel() 
            else:
                captured_photos[current_step - 1] = photo_path
                if current_step < 4:
                    current_step += 1
                    update_camera_ui()
                else:
                    show_review_panel()

    # 💥 修復點 1：建立 FilePicker 後，立刻 page.update() 消除紅色 Unknown 警告
    file_picker = ft.FilePicker()
    file_picker.on_result = on_photo_picked
    page.overlay.append(file_picker)
    page.update() 

    # 📂 2. 資料夾與記憶體初始化
    today_str = datetime.now().strftime("%Y%m%d")
    current_step = 1  
    group_counter = 1 
    captured_photos = ["", "", "", ""]
    previous_photos = None 

    step_titles = {
        1: "【步驟 1 / 4】請拍攝：遠照（整體環境）",
        2: "【步驟 2 / 4】請拍攝：近照（異常點特寫）",
        3: "【步驟 3 / 4】請拍攝：設備編號 (對準標籤)",
        4: "【步驟 4 / 4】請拍攝：異常周遭的設備"
    }
    retake_target = 0 

    # 🎨 3. 建立畫面的 UI 元件
    info_text = ft.Text(value="", size=15, weight="bold", color="blue", text_align="center")
    
    camera_view = ft.Container(
        expand=True, 
        bgcolor="black", border_radius=10, alignment=ft.Alignment(0, 0),
        content=ft.Container(
            expand=True, margin=10,
            border=ft.Border(top=ft.BorderSide(2, "white"), right=ft.BorderSide(2, "white"), bottom=ft.BorderSide(2, "white"), left=ft.BorderSide(2, "white")),
            alignment=ft.Alignment(0, 0), 
            content=ft.Text("📷\n此區域將呼叫手機原生相機\n(可於原生相機開啟九宮格)", color="white", size=14, text_align="center")
        )
    )

    def update_camera_ui():
        prefix = f"(第 {group_counter:03d} 組)\n"
        info_text.value = f"🔥 [單獨重拍中]\n{step_titles[retake_target]}" if retake_target > 0 else prefix + step_titles[current_step]
        
        if retake_target == 0 and previous_photos is not None and current_step in [3, 4]:
            reuse_btn.visible = True
            reuse_btn.content.value = "♻️ 沿用上一組"
        else:
            reuse_btn.visible = False
        page.update()

    # 💥 修復點 2：加上 async (非同步) 與 await，並將檔案類型改為安全字串 "image"
    async def take_photo_click(e):
        await file_picker.pick_files(allow_multiple=False, file_type="image")

    def reuse_photo_click(e):
        nonlocal current_step
        captured_photos[current_step - 1] = previous_photos[current_step - 1]
        if current_step < 4:
            current_step += 1
            update_camera_ui()
        else:
            show_review_panel()

    shutter_btn = ft.Container(
        content=ft.Text("🔴 點擊啟動相機", color="white", weight="bold", size=16),
        bgcolor="red", width=250, height=50, border_radius=25, alignment=ft.Alignment(0, 0), on_click=take_photo_click
    )
    reuse_btn = ft.Container(
        content=ft.Text("", color="white", size=14, weight="bold"), 
        bgcolor="blue", width=250, height=40, border_radius=10, alignment=ft.Alignment(0, 0), on_click=reuse_photo_click, visible=False
    )
    camera_controls = ft.Column([shutter_btn, reuse_btn], alignment="center", horizontal_alignment="center", spacing=10)

    main_layout = ft.Column([
        info_text, 
        camera_view, 
        camera_controls
    ], expand=True, horizontal_alignment="center", spacing=15)

    # 🧩 5. 2x2 綜合確認面板排版
    def on_single_box_click(e, box_idx):
        nonlocal retake_target
        retake_target = box_idx
        page.controls.clear()
        page.add(safe_area_layout)
        update_camera_ui()

    def save_and_next_group(e):
        nonlocal current_step, group_counter, previous_photos
        previous_photos = list(captured_photos) 
        
        for i in range(4):
            captured_photos[i] = ""
            
        current_step = 1
        group_counter += 1
        
        page.controls.clear()
        page.add(safe_area_layout)
        update_camera_ui()

    def create_preview_box(idx, title):
        box_content = ft.Image(src=captured_photos[idx-1], fit="cover") if captured_photos[idx-1] != "" else ft.Text(title, text_align="center", color="black")
        
        return ft.Container(
            content=box_content, 
            bgcolor="#e1e1e1", expand=1, height=140, border_radius=5, alignment=ft.Alignment(0, 0), 
            on_click=lambda e: on_single_box_click(e, idx)
        )

    def show_review_panel():
        info_text.value = f"🔎 第 {group_counter:03d} 組確認 (點擊單格重拍)"
        
        grid = ft.Column([
            ft.Row([create_preview_box(1, "1.遠照\n(點擊重拍)"), create_preview_box(2, "2.近照\n(點擊重拍)")], alignment="center", expand=True), 
            ft.Row([create_preview_box(3, "3.編號\n(點擊重拍)"), create_preview_box(4, "4.周遭\n(點擊重拍)")], alignment="center", expand=True), 
        ], spacing=10, expand=True)

        action_row = ft.Row([
            ft.Container(content=ft.Text("❌ 全部重拍", color="white", weight="bold"), bgcolor="grey", expand=1, height=45, border_radius=5, alignment=ft.Alignment(0, 0), on_click=lambda e: restart_current_group()), 
            ft.Container(content=ft.Text("✔ 確認儲存", color="white", weight="bold"), bgcolor="green", expand=1, height=45, border_radius=5, alignment=ft.Alignment(0, 0), on_click=save_and_next_group)
        ], alignment="center", spacing=15)

        review_layout = ft.Column([info_text, grid, ft.Divider(height=10), action_row], expand=True, horizontal_alignment="center")
        
        page.controls.clear()
        page.add(ft.SafeArea(content=ft.Container(content=review_layout, padding=10, expand=True), expand=True))
        page.update()

    def restart_current_group():
        nonlocal current_step, retake_target
        current_step = 1
        retake_target = 0
        for i in range(4):
            captured_photos[i] = ""
        page.controls.clear()
        page.add(safe_area_layout)
        update_camera_ui()

    # 🚀 6. 啟動首頁
    safe_area_layout = ft.SafeArea(
        content=ft.Container(content=main_layout, padding=10, expand=True),
        expand=True
    )
    
    page.add(safe_area_layout)
    update_camera_ui()

try:
    ft.run(main)
except AttributeError:
    ft.app(target=main)